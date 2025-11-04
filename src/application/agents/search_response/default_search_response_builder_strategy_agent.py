from domain.models import SearchContext
from domain.ai import LlmProvider
from application.prompts import StaticPromptProvider
from application.agents.search_response.search_response_builder_strategy_agent import SearchResponseBuilderStrategyAgent

class DefaultSearchResponseBuilderStrategyAgent(SearchResponseBuilderStrategyAgent):

    def __init__(self, prompt_provider: StaticPromptProvider, llm_provider: LlmProvider):
        self.prompt_provider = prompt_provider
        self.llm_provider = llm_provider
    
    def apply(self, context:SearchContext):
        return True
    
    def invoke(self, context:SearchContext):
        """Invoke the configured LLM with the provided message and prompt template."""
        
        new_message = ("human", context.exchange)

        messages = self.prompt_provider.get_prompt(context).format_messages(question=new_message)
        output = self.llm_provider.invoke(messages)
        return output.content