from typing import Annotated, List
from fastapi import Depends
from functools import partial

from domain.models import SearchContext, UserRequestDto, ProductFilterDetectionResult, AttributeFilterDto, AttributeFilterValue
from domain.services.database import DatabaseRequestService
from domain.logger import ContextLogger

from application.agents import FilterExtractionAgent

from dependencies import inject_request_db_service, inject_logger

class RequestManager:
    """Coordinates retrieval, enrichment, and persistence of conversational search requests."""

    def __init__(
            self, 
            filters_extraction_agent: Annotated[FilterExtractionAgent, Depends(FilterExtractionAgent)],
            request_db_service: Annotated[DatabaseRequestService, Depends(inject_request_db_service)],
            logger: Annotated[ContextLogger, Depends(partial(inject_logger, module_name="RequestManager"))]):
        """Persist injected dependencies used to process conversational requests."""
        self.request_db_service = request_db_service
        self.filters_extraction_agent = filters_extraction_agent
        self.logger = logger

    def get_requests(self, context:SearchContext) -> SearchContext:
        """Populate the context with stored requests for the current user session."""
        requests:List[UserRequestDto] = self.request_db_service.get_requests(
            user_id=context.user_id, 
            session_id=context.session_id
        ) if not context.is_first_call else []
        context.requests = requests
        self.logger.debug_context(
            message=f"Got {len(requests)} requests." if not context.is_first_call else "No requests yet.",
            context=context
        )
        return context
    
    def upsert_requests(self, context:SearchContext):
        """Persist the latest request payloads tracked on the context."""
        for request in context.requests:
            self.request_db_service.update_request(request)
        self.logger.debug_context(
            message=f"Upsert {len(context.requests)} requests.",
            context=context
        )
    
    def build_requests(self, context:SearchContext) -> SearchContext:
        """
        Derive detected filter values for each attribute set and update request objects.

        Returns the context after attaching `request_chain_results` and updating request data.
        """
        request_chain_results:List[ProductFilterDetectionResult] = [] # (attribute-set,ai-question)
        for i in range(len(context.detected_attribute_sets.products)):
            product =  context.detected_attribute_sets.products[i]
            term = context.detected_attribute_sets.terms[i]
            # Get the filter list of the product
            attribute_set = next((attr for attr in context.attribute_sets if attr.code == product), None)
            if attribute_set:
                filters:List[AttributeFilterDto] = attribute_set.filters
                detected_filters = self.filters_extraction_agent.invoke(exchange=context.exchange, filters=filters, context=context)
                detected_result = ProductFilterDetectionResult(
                    attribute_set_name=attribute_set.name,
                    attribute_set_code=product,
                    attribute_set_id = attribute_set.attribute_set_id,
                    search_term=term,
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

                filters_log = ",  ".join([f"{f.code}:{f.value}" for f in detected_result.detected_filters])
                self.logger.debug_context(
                    message=f"Filters for attribute-set '{product}': [{filters_log}]",
                    context=context
                )
        
        context.request_chain_results = request_chain_results
        return context
