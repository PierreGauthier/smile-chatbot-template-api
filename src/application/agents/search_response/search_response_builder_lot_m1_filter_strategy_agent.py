from application.agents.search_response.search_response_builder_strategy_agent import SearchResponseBuilderStrategyAgent

from domain.models import SearchContext
from domain.ai import LlmProvider
from application.prompts import StaticPromptProvider

class SearchResponseBuilderLotM1FilterStrategyAgent(SearchResponseBuilderStrategyAgent):

    def __init__(self, prompt_provider: StaticPromptProvider, llm_provider: LlmProvider):
        super().__init__(prompt_provider=prompt_provider, llm_provider=llm_provider)

    def apply(self, context:SearchContext):
        nb_product_found = context.search_total_count
        nb_detected_filters = len(context.get_valued_filters())
        nb_used_filters = len(context.search_used_filters) 
        return nb_product_found > 5 and nb_detected_filters > 0 and nb_used_filters + 1 == nb_detected_filters
