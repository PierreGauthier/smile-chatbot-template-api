from application.agents.search_response.search_response_builder_strategy_agent_decorator import SearchResponseBuilderStrategyAgentDecorator
from application.agents.search_response.search_response_builder_strategy_agent import SearchResponseBuilderStrategyAgent

from domain.models import SearchContext

OK_MAX = 5
OK_MIN = 3

class ResultNumberStrategyAgentDecorator(SearchResponseBuilderStrategyAgentDecorator):

    def __init__(self, search_response_builder: SearchResponseBuilderStrategyAgent, comparer):
        super().__init__(search_response_builder)
        self.comparer = comparer

    @staticmethod
    def a_lot(search_response_builder: SearchResponseBuilderStrategyAgent):
        return ResultNumberStrategyAgentDecorator(
            search_response_builder,
            lambda result_nb: result_nb > OK_MAX
        )
    
    @staticmethod
    def ok(search_response_builder: SearchResponseBuilderStrategyAgent):
        return ResultNumberStrategyAgentDecorator(
            search_response_builder,
            lambda result_nb: result_nb <= OK_MAX and result_nb >= OK_MIN
        )
    
    @staticmethod
    def few(search_response_builder: SearchResponseBuilderStrategyAgent):
        return ResultNumberStrategyAgentDecorator(
            search_response_builder,
            lambda result_nb: result_nb < OK_MIN
        )
    
    def apply(self, context:SearchContext):
        r = self.comparer(context.search_total_count)
        return r and self.search_response_builder.apply(context)