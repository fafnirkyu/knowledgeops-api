from typing import Protocol

from app.schemas.answer import GeneratedAnswer


class AnswerProvider(Protocol):
    def generate(
        self,
        prompt: str,
    ) -> GeneratedAnswer:
        ...