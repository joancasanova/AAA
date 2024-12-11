# infrastructure/external/embeddings/embeddings_config.py
from typing import Optional
from pydantic import BaseSettings

class LLMConfig(BaseSettings):
    model_name: str = "EleutherAI/gpt-neo-125M"
    device: Optional[str] = None
    max_length: int = 2048
    default_temperature: float = 1.0
    max_batch_size: int = 4

    class Config:
        env_prefix = "LLM_"