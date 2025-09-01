from typing import Annotated, List
from fastapi import Depends
from config import Settings, get_settings

from langchain_core.globals import set_verbose, set_debug

from agents import (
    SummarizeExchangeAgent,
    BasicPydanticChain,
    AttributeSetExtractionAgent,
    FilterExtractionAgent,
    QuestionsSummarizerAgent,
    EmptySearchResponseBuilderAgent
)
from services import (
    DatabaseHistoryService, 
    SearchService, 
    DatabaseAttributesSetupService, 
    DatabaseRequestService
)
from models import (
    SearchServiceResult, 
    AttributeSetDto,
    ElasticSuiteAttributeSet,
    AttributeFilterDto,
    ChatMessage,
    UserRequestDto,
    ProductFilterDetectionResult,
    AttributeFilterValue,
    SearchApiResponse
)
from fields import AttributeField
from api_clients import ConversationalSearchClient
from dependencies import (
    inject_history_service, 
    inject_attribute_database_service, 
    inject_request_service,
    inject_conversational_search_api
)

class ConversationalSearchService(SearchService):
    def __init__(
            self,
            settings: Annotated[Settings, Depends(get_settings)],
            attribute_set_db_service : Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            attribute_set_extraction_agent: Annotated[AttributeSetExtractionAgent, Depends(AttributeSetExtractionAgent)],
            filters_extraction_agent: Annotated[FilterExtractionAgent, Depends(FilterExtractionAgent)],
            summarize_exchange_agent : Annotated[BasicPydanticChain, Depends(SummarizeExchangeAgent)],
            summarize_question_agent : Annotated[QuestionsSummarizerAgent, Depends(QuestionsSummarizerAgent)],
            empty_search_response_agent: Annotated[EmptySearchResponseBuilderAgent, Depends(EmptySearchResponseBuilderAgent)],
            history_db_service: Annotated[DatabaseHistoryService, Depends(inject_history_service)],
            request_db_service: Annotated[DatabaseRequestService, Depends(inject_request_service)],
            conversational_search_client: Annotated[ConversationalSearchClient, Depends(inject_conversational_search_api)]):
        self.settings = settings
        self.attribute_set_db_service = attribute_set_db_service
        self.attribute_set_extraction_agent = attribute_set_extraction_agent
        self.history_db_service = history_db_service
        self.summarize_exchange_agent = summarize_exchange_agent
        self.filters_extraction_agent = filters_extraction_agent
        self.request_db_service = request_db_service
        self.summarize_question_agent = summarize_question_agent
        self.conversational_search_client = conversational_search_client
        self.empty_search_response_agent = empty_search_response_agent

        # Set the verbosity level based on the DEBUG environment variable
        set_verbose(settings.debug)
        set_debug(settings.debug)

    def invoke(self, input_message: str, user_id: str, session_id: str = None) -> SearchServiceResult:

        # Insert user message and get the message history
        current_session_id, message_thread = self.__get_history_thread(
            input_message=input_message,
            user_id=user_id, 
            session_id=session_id
        )

        # Summarize exchange
        exchange = self.__summarize_exchange(input_message=input_message, message_thread=message_thread)
        
        # Get requests
        requests:List[UserRequestDto] = self.request_db_service.get_requests(
            user_id=user_id, 
            session_id=current_session_id
        ) if session_id else []

        # Get attribute set list
        attribute_sets:List[AttributeSetDto] = self.attribute_set_db_service.list_attribute_sets()

        # Detect product (attribute set)
        detected_attribute_sets:AttributeField = self.attribute_set_extraction_agent.invoke(
            user_message=exchange,
            attribute_set=[ElasticSuiteAttributeSet(name=attr.name, description=attr.description) for attr in attribute_sets],
            product_counter_example="bicycle" # TODO
        )
        print(f"[{detected_attribute_sets.is_intent}]: {detected_attribute_sets.chain_of_thoughts}")

        # Build a request for each product that the user is searching for
        request_chain_results = self.__build_requests(
            user_id=user_id, 
            session_id=current_session_id,
            attribute_sets=attribute_sets, 
            detected_attribute_sets=detected_attribute_sets,
            exchange=exchange,
            requests=requests
        )        

        # Upsert the requests
        for request in requests:
            self.request_db_service.update_request(request)
            
        if not request_chain_results:
            return SearchServiceResult(
                user_id=user_id,
                session_id=session_id,
                answer="Sorry, I couldn't find the product(s) you are searching for.",
                products=[]
            )

        # Search OR ask for filters
        result = self.__handle_search_request(
            user_id=user_id,
            session_id=current_session_id,
            requests=requests,
            request_chain_results=request_chain_results,
            message_thread=message_thread
        )

        # Insert the AI message in the DB
        self.history_db_service.upsert_message(message=ChatMessage.build_ai_message(
            user_id=user_id,
            session_id=current_session_id,
            content=result.answer
        ))

        # filters:List[AttributeFilterDto] = self.attribute_set_db_service.get_filters(attribute_set_name.attribute_set_id)
        # result = self.filters_extraction_agent.invoke(exchange=exchange, filters=filters)

        return result
    
    # PRIVATE

    def __handle_search_request(
            self, 
            user_id:str,
            session_id:str,
            requests:List[UserRequestDto],
            request_chain_results:List[ProductFilterDetectionResult],
            message_thread:List[ChatMessage]) -> SearchServiceResult:
        no_question =  all([not request.ai_question.strip() for request in request_chain_results])
        too_many_questions = any([message.type == "ai" for message in message_thread])
        if no_question or too_many_questions:
            # Launch the search
            items = []
            for product in request_chain_results:
                api_response:SearchApiResponse = self.conversational_search_client.search_products(
                    attribute_set=product.attribute_set_name,
                    filters=product.detected_filters
                )
                items.extend(api_response.items)
            
            # Create an answer calling to the right agent (no products, or products)

            if len(items) == 0:
                empty_search_answer = self.empty_search_response_agent.invoke(requests)
                return SearchServiceResult(
                    user_id=user_id,
                    session_id=session_id,
                    answer= empty_search_answer,
                    products=[]
                )


            # TODO (agent)
            return SearchServiceResult(
                user_id=user_id,
                session_id=session_id,
                answer= "Here you have a list of products corresponding to your search constraints:",
                products=items
            ) 

        else:
            # Summarize the set of questions
            summarized_question = self.summarize_question_agent.invoke(
                last_exchange=message_thread[:4],
                questions=request_chain_results
            )
            return SearchServiceResult(
                user_id=user_id,
                session_id=session_id,
                answer= summarized_question,#str(detected_attribute_sets.products),#f"Found {len(filters)} filters",
                products=[]
            ) 

    def __summarize_exchange(self, input_message:str, message_thread:List[ChatMessage]):
        exchange = input_message
        if len(message_thread) > 1:
            # DEBUG
            for msg in message_thread:
                print(f"---{msg.data.content}")

            exchange = self.summarize_exchange_agent.invoke(message_thread)
            print(exchange)
        return exchange

    def __get_history_thread(self, input_message:str, user_id:str, session_id):
        current_session_id = session_id
        if current_session_id:
            new_message = ChatMessage.build_human_message(
                session_id=current_session_id,
                user_id=user_id, 
                content=input_message
            )
            self.history_db_service.upsert_message(new_message)
        else:
            new_message:ChatMessage = self.history_db_service.create_message_thread(user_id=user_id, message=input_message)
            current_session_id = new_message.session_id
        message_thread:List[ChatMessage] = self.history_db_service.get_message_thread(user_id=user_id, session_id=current_session_id)
        return current_session_id, message_thread

    def __build_requests(
            self, 
            user_id, 
            session_id,
            attribute_sets:List[AttributeSetDto], 
            detected_attribute_sets:AttributeField,
            exchange:str,
            requests:List[UserRequestDto]) -> List[ProductFilterDetectionResult]:
        
        request_chain_results:List[ProductFilterDetectionResult] = [] # (attribute-set,ai-question)
        for product in detected_attribute_sets.products:
            # Get the filter list of the product
            attribute_set = next((attr for attr in attribute_sets if attr.name == product), None)
            if attribute_set:
                filters:List[AttributeFilterDto] = self.attribute_set_db_service.get_filters(attribute_set.attribute_set_id)
                detected_filters = self.filters_extraction_agent.invoke(exchange=exchange, filters=filters)
                detected_result = ProductFilterDetectionResult(
                    attribute_set_name=product,
                    attribute_set_id = attribute_set.attribute_set_id,
                    ai_question=detected_filters.ai_question,
                    detected_filters=[]
                )
                request_chain_results.append(detected_result)
            # Find request corresponding to the attribute_set (or create it)
            corresponding_request = next((req for req in requests if req.attribute_id == attribute_set.attribute_set_id), None)
            if not corresponding_request:
                corresponding_request = self.request_db_service.create_request(
                    user_id=user_id,
                    session_id=session_id,
                    attribute_id=attribute_set.attribute_set_id,
                    data={}
                )
                requests.append(corresponding_request)                
            # Update the request with detected values
            if attribute_set:
                for filter in filters:
                    result_dump = detected_filters.model_dump()
                    if filter.type == "price":
                        detected_filter_value = { 
                            "min_price": result_dump.get("price")["min_price"],
                            "max_price": result_dump.get("price")["max_price"]
                        }
                    else:
                        detected_filter_value = result_dump.get(filter.code)
                    detected_result.detected_filters.append(AttributeFilterValue(
                        attribute_id=filter.attribute_id,
                        label=filter.label,
                        code=filter.code,
                        type=filter.type,
                        description=filter.description,
                        value=detected_filter_value
                    ))
                    if detected_filter_value:
                        corresponding_request.data[filter.code] = detected_filter_value
        return request_chain_results