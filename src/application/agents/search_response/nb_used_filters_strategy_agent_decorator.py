from application.agents.search_response.search_response_builder_strategy_agent_decorator import SearchResponseBuilderStrategyAgentDecorator
from application.agents.search_response.search_response_builder_strategy_agent import SearchResponseBuilderStrategyAgent

from domain.models import SearchContext

class NbUsedFiltersStrategyAgentDecorator(SearchResponseBuilderStrategyAgentDecorator):

    def __init__(self, search_response_builder: SearchResponseBuilderStrategyAgent, comparer):
        super().__init__(search_response_builder)
        self.comparer = comparer

    @staticmethod
    def no_used_filter(search_response_builder: SearchResponseBuilderStrategyAgent):
        return NbUsedFiltersStrategyAgentDecorator(
            search_response_builder, 
            lambda _, nb_used_filters: nb_used_filters == 0
        )
    
    @staticmethod
    def one_used_filter(search_response_builder: SearchResponseBuilderStrategyAgent):
        return NbUsedFiltersStrategyAgentDecorator(
            search_response_builder, 
            lambda _, nb_used_filters: nb_used_filters == 1
        )
    
    @staticmethod
    def minus_one_used_filter(search_response_builder: SearchResponseBuilderStrategyAgent):
        return NbUsedFiltersStrategyAgentDecorator(
            search_response_builder, 
            lambda nb_detected_filters, nb_used_filters: nb_used_filters + 1 == nb_detected_filters
        )
    
    @staticmethod
    def all_filter(search_response_builder: SearchResponseBuilderStrategyAgent):
        return NbUsedFiltersStrategyAgentDecorator(
            search_response_builder, 
            lambda nb_detected_filters, nb_used_filters: nb_used_filters == nb_detected_filters
        )
    
    def apply(self, context:SearchContext):
        detected_filters = context.get_valued_filters()
        r = self.comparer(len(detected_filters), len(context.search_used_filters))
        return r and self.search_response_builder.apply(context)