from typing import Annotated, List
from fastapi import Depends
from functools import partial

from domain.models import SearchContext, FilteredSearchApiResponse
from domain.api_client import ConversationalSearchClient
from domain.logger import ContextLogger

from application.agents import QuestionsSummarizerAgent, SearchResponseBuilderAgent, SearchResponseBuilderStrategyAgentDecorator

from dependencies import (
    inject_conversational_search_api, 
    inject_logger, 
    inject_search_response_agent, 
    inject_search_response_builder_agents
)


class SearchManager:
    """Coordinates conversational product search by invoking summarization, retrieval, and response agents."""

    def __init__(
            self,
            summarize_question_agent : Annotated[QuestionsSummarizerAgent, Depends(QuestionsSummarizerAgent)],
            search_response_agent: Annotated[SearchResponseBuilderAgent, Depends(inject_search_response_agent)],
            conversational_search_client: Annotated[ConversationalSearchClient, Depends(inject_conversational_search_api)],
            logger: Annotated[ContextLogger, Depends(partial(inject_logger, module_name="SearchManager"))]):
        """Store injected dependencies used to prepare and execute conversational search queries."""
        self.summarize_question_agent = summarize_question_agent
        self.conversational_search_client = conversational_search_client
        self.search_response_agent = search_response_agent

        self.search_response_agent_strategies:List[SearchResponseBuilderStrategyAgentDecorator] = inject_search_response_builder_agents()

        self.logger = logger

    def search(self, context:SearchContext) -> SearchContext:
        """Execute the conversational search flow and enrich the provided context with results.

        Args:
            context: Carries conversation history, filter hypotheses, and required attribute sets.

        Returns:
            The same context instance updated with `ai_answer` and `search_result`.

        Raises:
            KeyError: When an attribute set referenced by a filter hypothesis is missing.
        """
        # no_question =  all([not request.ai_question.strip() for request in context.request_chain_results])
        # too_many_questions = any([message.type == "ai" for message in context.message_thread])
        
        #if no_question or too_many_questions:
        total_count = 0
        
        # Launch the search (/!\ Only one product search hypothesis)
        items = []
        api_response:FilteredSearchApiResponse = None
        for product in context.request_chain_results:
            attribute_set = next((attr for attr in context.attribute_sets if attr.attribute_set_id == product.attribute_set_id), None)
            if not attribute_set:
                raise KeyError(f"No attribute set found ({product.attribute_set_code})")
            filters_dto = attribute_set.filters
            api_response = self.conversational_search_client.search(
                filter_detection_result=product,
                filters_dto=filters_dto,
                context=context
            )
            if api_response.code == 200:
                items.extend(api_response.items)
                total_count += api_response.total_count
            else:
                self.logger.info_context(api_response.message, context)
            
            # Create an answer calling to the right agent (no products, or products)

        context.search_total_count = total_count
        context.search_result = items
        for response_strategy in self.search_response_agent_strategies:
            if response_strategy.apply(context):
                answer = response_strategy.invoke(context)
                context.ai_answer = answer                
                break

        # if len(items) == 0:
        #     empty_search_answer = self.search_response_agent.invoke_empty(context)
        #     context.ai_answer = empty_search_answer
        #     context.search_result = []
        
        # else:
        #     not_empty_search_answer = self.search_response_agent.invoke_not_empty(
        #         context=context, 
        #         search_result=items, 
        #         filter_name=api_response.filter_name,
        #         is_included=api_response.is_filter_included,
        #         total_count=total_count)
        #     context.ai_answer = not_empty_search_answer
        #     context.search_result = items
            
            # TODO: take into account all the result for the answer

        # else:
        #     # Summarize the set of questions
        #     summarized_question = self.summarize_question_agent.invoke(
        #         last_exchange=context.message_thread,
        #         questions=context.request_chain_results
        #     )
        #     context.ai_answer = summarized_question
        #     context.search_result = []
        
        return context
