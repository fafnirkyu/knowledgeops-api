from pydantic import Field, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    embedding_model: str = Field(
        default=(
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        )
    )

    answer_model_repo: str = Field(
        default="Qwen/Qwen2.5-3B-Instruct-GGUF",
        min_length=1,
    )
    answer_model_filename: str = Field(
        default="qwen2.5-3b-instruct-q5_k_m.gguf",
        min_length=1,
    )
    answer_context_size: int = Field(
        default=4096,
        ge=1024,
    )
    answer_max_tokens: int = Field(
        default=512,
        ge=1,
        le=2048,
    )
    answer_gpu_layers: int = Field(
        default=0,
        ge=-1,
    )

    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0"
    )
    redis_queue_name: str = Field(
        default="document-processing",
        min_length=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )