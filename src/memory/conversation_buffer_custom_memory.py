from typing import Any, Dict, List, Union
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage, get_buffer_string
from langchain.memory.chat_memory import BaseChatMemory

class ConversationBufferCustomMemory(BaseChatMemory):
    """Buffer for storing conversation memory inside a limited size window and token limit.."""

    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    memory_key: str = "history"  #: :meta private:
    k: int = 5
    llm: BaseLanguageModel
    max_token_limit: int = 2000
    """Number of messages to store in buffer."""

    @property
    def buffer(self) -> Union[str, List[BaseMessage]]:
        """String buffer of memory."""
        return self.buffer_as_messages if self.return_messages else self.buffer_as_str

    @property
    def buffer_as_str(self) -> str:
        """Exposes the buffer as a string in case return_messages is True."""
        return get_buffer_string(
            self.trimmed_messages,
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )

    @property
    def buffer_as_messages(self) -> List[BaseMessage]:
        """Exposes the buffer as a list of messages in case return_messages is False."""
        return self.trimmed_messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.

        :meta private:
        """
        return [self.memory_key]
    
    @property
    def trimmed_messages(self) -> List[BaseMessage]:
        """Get the trimmed messages.
        
        :meta private:
        """
        messages = self.chat_memory.messages[-self.k * 2 :] if self.k > 0 else []
        print(self.llm)
        while self.llm.get_num_tokens_from_messages(messages) > self.max_token_limit:
            messages.pop(0)
        return messages

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        return {self.memory_key: self.buffer}