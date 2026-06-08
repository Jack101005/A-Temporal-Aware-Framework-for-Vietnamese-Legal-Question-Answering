"""
llm_client.py
=============
One uniform interface to every LLM we test.

WHY:
We evaluate many models -- Vietnamese (PhoGPT, VinaLLaMA, ViGPT-Law) and
commercial (GPT-4, Claude, Gemini). The rest of the system should not care
which one it is talking to. It just calls generate(prompt) and gets text.

WHAT IT WILL DO LATER:
- a small subclass per provider (OpenAIClient, AnthropicClient,
  HuggingFaceClient, ...) all sharing generate().
- build_prompt(question, documents): assemble the temporal-aware prompt that
  tells the model to use ONLY the supplied (already time-filtered) documents.
"""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Uniform generate() interface for any LLM provider."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """TODO: send prompt to the model, return its text answer."""
        ...


def build_prompt(question: str, documents: list) -> str:
    """TODO: format question + filtered documents into a grounded,
    temporal-aware prompt (instruct: cite ONLY these documents)."""
    ...
