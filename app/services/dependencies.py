from functools import lru_cache

import outlines
from llama_cpp import Llama

from app.core.config import Settings
from app.schemas.answer import GeneratedAnswer
from app.services.answer_provider import AnswerProvider
from app.services.embedding_provider import EmbeddingProvider
from app.services.fastembed_provider import (
    FastEmbedEmbeddingProvider,
)
from app.services.outlines_answer_provider import (
    OutlinesAnswerProvider,
)


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    settings = Settings()

    return FastEmbedEmbeddingProvider(
        model_name=settings.embedding_model,
    )


@lru_cache(maxsize=1)
def get_answer_provider() -> AnswerProvider:
    settings = Settings()

    llama_model = Llama.from_pretrained(
        repo_id=settings.answer_model_repo,
        filename=settings.answer_model_filename,
        n_ctx=settings.answer_context_size,
        n_gpu_layers=settings.answer_gpu_layers,
        verbose=False,
    )

    outlines_model = outlines.from_llamacpp(
        llama_model,
    )

    generator = outlines.Generator(
        outlines_model,
        GeneratedAnswer,
    )

    return OutlinesAnswerProvider(
        generator,
        max_tokens=settings.answer_max_tokens,
    )