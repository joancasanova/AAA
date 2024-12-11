import argparse
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import asdict

from infrastructure.external.llm.instruct_model import InstructModel
from infrastructure.external.embeddings.embedder_model import EmbedderModel
from infrastructure.external.model_cache import *

from application.use_cases.generation.generate_text_use_case import (
    GenerateTextUseCase,
    GenerateTextRequest,
)
from application.use_cases.parsing.parse_generated_output_use_case import (
    ParseGeneratedOutputUseCase,
    ParseGeneratedOutputRequest,
)
from application.use_cases.verification.verify_text_use_case import (
    VerifyTextUseCase,
    VerifyTextRequest,
)
from application.use_cases.orchestration.execute_pipeline_use_case import (
    ExecutePipelineUseCase,
    ExecutePipelineRequest,
)
from application.use_cases.benchmark.run_benchmark_use_case import (
    RunBenchmarkUseCase,
    RunBenchmarkRequest,
)

from domain.model.entities.parsing import (
    ParseRule,
    ParseMode,
    ParseScope,
    ParseStrategy,
)
from domain.model.entities.verification import (
    VerificationMethod,
    VerificationMethodType,
    VerificationMode,
)
from domain.services.parse_service import ParseService
from domain.services.verifier_service import VerifierService
from domain.services.metrics_service import MetricsService


class Logger:
    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        logging.log(getattr(logging, level), f"{message} {context or ''}")


def load_json_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def setup_logging(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Text Processing Pipeline")

    # Global arguments
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--output", type=str, help="Output file path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate text")
    gen_parser.add_argument("--system-prompt", required=True, help="System prompt")
    gen_parser.add_argument("--user-prompt", required=True, help="User prompt")
    gen_parser.add_argument(
        "--num-sequences", type=int, default=1, help="Number of sequences to generate"
    )
    gen_parser.add_argument(
        "--max-tokens", type=int, default=100, help="Maximum tokens to generate"
    )
    gen_parser.add_argument(
        "--temperature", type=float, default=1.0, help="Generation temperature"
    )

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse text")
    parse_parser.add_argument("--text", required=True, help="Text to parse")
    parse_parser.add_argument(
        "--rules", required=True, help="JSON file containing parse rules"
    )

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify text")
    verify_parser.add_argument("--text", required=True, help="Text to verify")
    verify_parser.add_argument(
        "--methods", required=True, help="JSON file containing verification methods"
    )
    verify_parser.add_argument(
        "--required-confirmed", type=int, required=True, help="Required confirmations"
    )
    verify_parser.add_argument(
        "--required-review", type=int, required=True, help="Required reviews"
    )

    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Execute pipeline")
    pipeline_parser.add_argument(
        "--config", required=True, help="JSON file containing pipeline configuration"
    )
    pipeline_parser.add_argument(
        "--input", required=True, help="Initial input for pipeline"
    )

    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Run benchmark")
    benchmark_parser.add_argument(
        "--config", required=True, help="JSON file containing benchmark configuration"
    )
    benchmark_parser.add_argument(
        "--entries", required=True, help="JSON file containing benchmark entries"
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    setup_logging(args.debug)
    logger = Logger()
    settings = Settings()

    # Initialize services
    model_cache = ModelCache(cache_dir="model_cache")
    llm = InstructModel()
    embedder = EmbedderModel()

    parse_service = ParseService()
    verifier_service = VerifierService(embedder, llm)
    metrics_service = MetricsService()

    # Initialize use cases
    generate_use_case = GenerateTextUseCase(llm, logger)
    parse_use_case = ParseGeneratedOutputUseCase(parse_service, logger)
    verify_use_case = VerifyTextUseCase(verifier_service, logger)
    pipeline_use_case = ExecutePipelineUseCase(
        generate_use_case, parse_use_case, verify_use_case, logger
    )
    benchmark_use_case = RunBenchmarkUseCase(verifier_service, metrics_service, logger)

    try:
        result = None

        if args.command == "generate":
            request = GenerateTextRequest(
                system_prompt=args.system_prompt,
                user_prompt=args.user_prompt,
                num_sequences=args.num_sequences,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )
            result = generate_use_case.execute(request)

        elif args.command == "parse":
            rules_data = load_json_file(args.rules)
            rules = [ParseRule(**rule) for rule in rules_data]
            request = ParseGeneratedOutputRequest(text=args.text, rules=rules)
            result = parse_use_case.execute(request)

        elif args.command == "verify":
            methods_data = load_json_file(args.methods)
            methods = [VerificationMethod(**method) for method in methods_data]
            request = VerifyTextRequest(
                text=args.text,
                methods=methods,
                required_for_confirmed=args.required_confirmed,
                required_for_review=args.required_review,
            )
            result = verify_use_case.execute(request)

        elif args.command == "pipeline":
            config = load_json_file(args.config)
            request = ExecutePipelineRequest(config=config, initial_input=args.input)
            result = pipeline_use_case.execute(request)

        elif args.command == "benchmark":
            config = load_json_file(args.config)
            entries = load_json_file(args.entries)
            request = RunBenchmarkRequest(configuration=config, entries=entries)
            result = benchmark_use_case.execute(request)

        # Save or print results
        if result:
            if args.output:
                save_json_file(asdict(result), args.output)
            else:
                print(json.dumps(asdict(result), indent=2, ensure_ascii=False))

    except Exception as e:
        logging.error(f"Error executing command: {str(e)}")
        raise


if __name__ == "__main__":
    main()
