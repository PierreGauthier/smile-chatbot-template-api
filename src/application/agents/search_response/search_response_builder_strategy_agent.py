from abc import ABC, abstractmethod

from domain.models import SearchContext
from domain.ai import LlmProvider
from application.prompts import StaticPromptProvider

class SearchResponseBuilderStrategyAgent(ABC):

    def __init__(self, prompt_provider: StaticPromptProvider, llm_provider: LlmProvider):
        self.prompt_provider = prompt_provider
        self.llm_provider = llm_provider

    @abstractmethod
    def apply(self, context:SearchContext):
        pass
    
    def invoke(self, context:SearchContext):
        """Invoke the configured LLM with the provided message and prompt template."""
        
        new_message = ("human", context.exchange)

        messages = self.prompt_provider.get_prompt(context).format_messages(question=new_message)
        output = self.llm_provider.invoke(messages)
        return output.content