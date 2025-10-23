from abc import ABC, abstractmethod


class LlmProvider(ABC):
    """Abstract base for integrations that expose a concrete large language model."""

    @abstractmethod
    def get_llm(self):
        """Return the underlying LLM client or SDK-specific handle."""
        pass

    @abstractmethod
    def invoke(self, messages):
        """Execute the LLM against the provided `messages` payload."""
        pass
