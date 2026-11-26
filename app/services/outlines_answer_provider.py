from collections.abc import Callable
from threading import Lock

from app.schemas.answer import GeneratedAnswer

GeneratorResult = str | GeneratedAnswer
StructuredAnswerGenerator = Callable[..., GeneratorResult]


class OutlinesAnswerProvider:
    def __init__(
        self,
        generator: StructuredAnswerGenerator,
        *,
        max_tokens: int,
    ):
        if max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than zero"
            )

        self._generator = generator
        self._max_tokens = max_tokens
        self._generation_lock = Lock()

    def generate(
        self,
        prompt: str,
    ) -> GeneratedAnswer:
        with self._generation_lock:
            result = self._generator(
                prompt,
                max_tokens=self._max_tokens,
                temperature=0.0,
                seed=42,
            )

        if isinstance(result, GeneratedAnswer):
            return result

        return GeneratedAnswer.model_validate_json(
            result
        )