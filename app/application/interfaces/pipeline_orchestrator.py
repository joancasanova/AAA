# application/interfaces/pipeline_orchestrator.py
from typing import List, Dict, Any, Protocol, Optional
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class PipelineStageType(Enum):
    GENERATE = "generate"
    PARSE = "parse"
    VERIFY = "verify"

@dataclass(frozen=True)
class PipelineStageConfig:
    stage_type: PipelineStageType
    parameters: Dict[str, Any]
    timeout_seconds: Optional[float] = None
    retry_count: Optional[int] = None

@dataclass(frozen=True)
class PipelineConfig:
    stages: List[PipelineStageConfig]
    max_total_time: Optional[float] = None
    error_handling_strategy: str = "fail_fast"
    metadata: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class StageResult:
    stage_type: PipelineStageType
    input_data: Any
    output_data: Any
    execution_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None

@dataclass(frozen=True)
class PipelineResult:
    stages_results: List[StageResult]
    start_time: datetime
    end_time: datetime
    total_time: float
    success: bool
    error: Optional[str] = None

class PipelineOrchestrator(ABC):
    @abstractmethod
    def execute(
        self,
        config: PipelineConfig,
        initial_input: Any
    ) -> PipelineResult:
        """
        Execute a pipeline with the given configuration.
        
        Args:
            config: Pipeline configuration defining stages and parameters
            initial_input: Initial input data for the pipeline
            
        Returns:
            PipelineResult containing results from all stages
        """
        pass

    @abstractmethod
    def validate_config(self, config: PipelineConfig) -> bool:
        """
        Validate a pipeline configuration.
        
        Args:
            config: Pipeline configuration to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        pass