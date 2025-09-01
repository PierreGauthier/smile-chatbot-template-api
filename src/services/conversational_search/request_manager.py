from typing import Annotated, List
from fastapi import Depends

from models import SearchContext, UserRequestDto, ProductFilterDetectionResult, AttributeFilterDto, AttributeFilterValue
from services import DatabaseRequestService, DatabaseAttributesSetupService
from agents import FilterExtractionAgent
from dependencies import inject_request_service, inject_attribute_database_service

class RequestManager:

    def __init__(
            self, 
            attribute_set_db_service : Annotated[DatabaseAttributesSetupService, Depends(inject_attribute_database_service)],
            filters_extraction_agent: Annotated[FilterExtractionAgent, Depends(FilterExtractionAgent)],
            request_db_service: Annotated[DatabaseRequestService, Depends(inject_request_service)]):
        self.request_db_service = request_db_service
        self.attribute_set_db_service = attribute_set_db_service
        self.filters_extraction_agent = filters_extraction_agent

    def get_requests(self, context:SearchContext) -> SearchContext:
        requests:List[UserRequestDto] = self.request_db_service.get_requests(
            user_id=context.user_id, 
            session_id=context.session_id
        ) if not context.is_first_call else []
        context.requests = requests
        return context
    
    def upsert_requests(self, context:SearchContext):
        for request in context.requests:
            self.request_db_service.update_request(request)
    
    def build_requests(self, context:SearchContext) -> SearchContext:
        request_chain_results:List[ProductFilterDetectionResult] = [] # (attribute-set,ai-question)
        for product in context.detected_attribute_sets.products:
            # Get the filter list of the product
            attribute_set = next((attr for attr in context.attribute_sets if attr.name == product), None)
            if attribute_set:
                filters:List[AttributeFilterDto] = self.attribute_set_db_service.get_filters(attribute_set.attribute_set_id)
                detected_filters = self.filters_extraction_agent.invoke(exchange=context.exchange, filters=filters)
                detected_result = ProductFilterDetectionResult(
                    attribute_set_name=product,
                    attribute_set_id = attribute_set.attribute_set_id,
                    ai_question=detected_filters.ai_question,
                    detected_filters=[]
                )
                request_chain_results.append(detected_result)
            # Find request corresponding to the attribute_set (or create it)
            corresponding_request = next((req for req in context.requests if req.attribute_id == attribute_set.attribute_set_id), None)
            if not corresponding_request:
                corresponding_request = self.request_db_service.create_request(
                    user_id=context.user_id,
                    session_id=context.session_id,
                    attribute_id=attribute_set.attribute_set_id,
                    data={}
                )
                context.requests.append(corresponding_request)                
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
        
        context.request_chain_results = request_chain_results
        return context