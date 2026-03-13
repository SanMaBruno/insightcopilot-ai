from __future__ import annotations

from abc import ABC, abstractmethod


class LlmClient(ABC):

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Genera texto a partir de un prompt de sistema y uno de usuario."""
        ...
