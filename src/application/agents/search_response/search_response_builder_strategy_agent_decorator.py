from abc import ABC, abstractmethod

from domain.models import SearchContext
from application.agents.search_response.search_response_builder_strategy_agent import SearchResponseBuilderStrategyAgent

class SearchResponseBuilderStrategyAgentDecorator(SearchResponseBuilderStrategyAgent):

    def __init__(self, search_response_builder: SearchResponseBuilderStrategyAgent):
        self.search_response_builder = search_response_builder

    def invoke(self, context:SearchContext):
        return self.search_response_builder.invoke(context)
