from typing import Annotated
from fastapi import Depends
from functools import partial

from domain.models import SearchContext, SearchApiResponse
from domain.api_client import ConversationalSearchClient
from domain.logger import ContextLogger

from application.agents import QuestionsSummarizerAgent, SearchResponseBuilderAgent

from dependencies import inject_conversational_search_api, inject_logger, inject_search_response_agent

class SearchManager:

    def __init__(
            self,
            summarize_question_agent : Annotated[QuestionsSummarizerAgent, Depends(QuestionsSummarizerAgent)],
            search_response_agent: Annotated[SearchResponseBuilderAgent, Depends(inject_search_response_agent)],
            conversational_search_client: Annotated[ConversationalSearchClient, Depends(inject_conversational_search_api)],
            logger: Annotated[ContextLogger, Depends(partial(inject_logger, module_name="SearchManager"))]):
        self.summarize_question_agent = summarize_question_agent
        self.conversational_search_client = conversational_search_client
        self.search_response_agent = search_response_agent
        self.logger = logger

    def search(self, context:SearchContext) -> SearchContext:
        # no_question =  all([not request.ai_question.strip() for request in context.request_chain_results])
        # too_many_questions = any([message.type == "ai" for message in context.message_thread])
        
        #if no_question or too_many_questions:
        total_count = 0
        # Launch the search
        items = []
        for product in context.request_chain_results:
            attribute_set = next((attr for attr in context.attribute_sets if attr.attribute_set_id == product.attribute_set_id), None)
            if not attribute_set:
                raise KeyError(f"No attribute set found ({product.attribute_set_code})")
            filters_dto = attribute_set.filters
            api_response:SearchApiResponse = self.conversational_search_client.search_products(
                filter_detection_result=product,
                filters_dto=filters_dto
            )
            #     attribute_set=product.attribute_set_name,
            #     term=product.search_term,
            #     filters=product.detected_filters
            # )
            if api_response.code == 200:
                items.extend(api_response.items)
                total_count += api_response.total_count
            else:
                self.logger.info_context(api_response.message, context)
            
            # Create an answer calling to the right agent (no products, or products)

        if len(items) == 0:
            empty_search_answer = self.search_response_agent.invoke_empty(context)
            context.ai_answer = empty_search_answer
            context.search_result = []
        
        else:
            not_empty_search_answer = self.search_response_agent.invoke_not_empty(context, items, total_count)
            context.ai_answer = not_empty_search_answer
            context.search_result = items
            
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