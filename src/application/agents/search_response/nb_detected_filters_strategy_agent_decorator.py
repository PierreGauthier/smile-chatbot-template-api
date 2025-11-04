from application.agents.search_response.search_response_builder_strategy_agent import SearchResponseBuilderStrategyAgent
from application.agents.search_response.search_response_builder_strategy_agent_decorator import SearchResponseBuilderStrategyAgentDecorator

from domain.models import SearchContext

class NbDetectedFiltersStrategyAgentDecorator(SearchResponseBuilderStrategyAgentDecorator):

    def __init__(self, search_response_builder: SearchResponseBuilderStrategyAgent, comparer):
        super().__init__(search_response_builder)
        self.comparer = comparer

    @staticmethod
    def no_detected_filter(search_response_builder: SearchResponseBuilderStrategyAgent):
        return NbDetectedFiltersStrategyAgentDecorator(
            search_response_builder, 
            lambda nb_detected_filters: nb_detected_filters == 0
        )
    
    @staticmethod
    def with_detected_filter(search_response_builder: SearchResponseBuilderStrategyAgent):
        return NbDetectedFiltersStrategyAgentDecorator(
            search_response_builder, 
            lambda nb_detected_filters: nb_detected_filters > 0
        )
    
    def apply(self, context:SearchContext):
        detected_filters = context.get_valued_filters()
        r = self.comparer(len(detected_filters))
        return r and self.search_response_builder.apply(context)
