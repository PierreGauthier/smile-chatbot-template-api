
from typing import Annotated
from fastapi import Depends

from agents import QuestionsSummarizerAgent, EmptySearchResponseBuilderAgent
from models import SearchContext, SearchApiResponse
from api_clients import ConversationalSearchClient
from dependencies import inject_conversational_search_api

class SearchManager:

    def __init__(
            self,
            summarize_question_agent : Annotated[QuestionsSummarizerAgent, Depends(QuestionsSummarizerAgent)],
            empty_search_response_agent: Annotated[EmptySearchResponseBuilderAgent, Depends(EmptySearchResponseBuilderAgent)],
            conversational_search_client: Annotated[ConversationalSearchClient, Depends(inject_conversational_search_api)]):
        self.summarize_question_agent = summarize_question_agent
        self.conversational_search_client = conversational_search_client
        self.empty_search_response_agent = empty_search_response_agent

    def search(self, context:SearchContext) -> SearchContext:
        no_question =  all([not request.ai_question.strip() for request in context.request_chain_results])
        too_many_questions = any([message.type == "ai" for message in context.message_thread])
        
        if no_question or too_many_questions:
            # Launch the search
            items = []
            for product in context.request_chain_results:
                api_response:SearchApiResponse = self.conversational_search_client.search_products(
                    attribute_set=product.attribute_set_name,
                    filters=product.detected_filters
                )
                items.extend(api_response.items)
            
            # Create an answer calling to the right agent (no products, or products)

            if len(items) == 0:
                empty_search_answer = self.empty_search_response_agent.invoke(context.requests)
                context.ai_answer = empty_search_answer
                context.search_result = []
            
            else:
                # TODO (agent)
                context.ai_answer = "Here you have a list of products corresponding to your search constraints:",
                context.search_result = items

        else:
            # Summarize the set of questions
            summarized_question = self.summarize_question_agent.invoke(
                last_exchange=context.message_thread[:4],
                questions=context.request_chain_results
            )
            context.ai_answer = summarized_question
            context.search_result = []
        
        return context