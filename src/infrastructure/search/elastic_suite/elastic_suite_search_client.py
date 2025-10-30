import json
import re
from typing import Annotated, List
from fastapi import Depends
from urllib.parse import urlparse, urlunparse

from domain.models import (
    FilteredSearchApiResponse,
    SearchApiResponse, 
    AttributeFilterValue, 
    ProductFilterDetectionResult, 
    AttributeFilterDto,
    BaseContext
)
from domain.api_client import ConversationalSearchClient
from domain.logger import ContextLogger
from infrastructure.search.elastic_suite import (
    ElasticSuiteSearchResponseBuilder, 
    OneFilterSelectionStrategy,
    ElasticSuiteGraphqlQueryFactory
)
from config import Settings, get_settings

class ElasticSuiteSearchClient(ConversationalSearchClient):
    def __init__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        search_response_builder: Annotated[ElasticSuiteSearchResponseBuilder, Depends(ElasticSuiteSearchResponseBuilder)],
        logger: Annotated[ContextLogger, Depends(ContextLogger)],
    ):
        super().__init__(settings.elastic_suite_search_api_base_url)
        self.settings = settings
        self.search_response_builder = search_response_builder
        self.logger = logger
        self.url = self.__insert_credentials(
            url=self.api_base_url,
            credentials=self.settings.elastic_suite_search_api_credentials,
        )
        (x_correlation_id_key, x_correlation_id_value) = self.create_x_correlation_id()
        (content_type_key, content_type_value) = self.create_json_content_type()
        self.headers = {
            x_correlation_id_key: x_correlation_id_value,
            content_type_key: content_type_value,
            "Store": "lamaison",
        }
        self.graphql_factory = ElasticSuiteGraphqlQueryFactory()

    def search(self, 
            filter_detection_result:ProductFilterDetectionResult,
            filters_dto:List[AttributeFilterDto],
            context:BaseContext,
            page_size: int = 10) -> FilteredSearchApiResponse:
        valued_detected_filters = [f for f in filter_detection_result.detected_filters if f.value]

        # Searching only with 'term'
        if not valued_detected_filters:
            response = self.search_products(
                valued_detected_filters, 
                filters_dto, 
                filter_detection_result.search_term, 
                context,
                page_size)
            return FilteredSearchApiResponse.build_from_search_api_response(
                response=response,
                filter_name=None,
                is_filter_included=False
            )
        
        # Search with all
        response = self.search_products(
            valued_detected_filters, 
            filters_dto, 
            filter_detection_result.search_term, 
            context,
            page_size)
        
        # TODO: manage search error (no total_count)
        if response.total_count > 0:
            return FilteredSearchApiResponse.build_from_search_api_response(
                response=response,
                filter_name=None,
                is_filter_included=False
            )
        
        best_response = None
        best_score = -1

        filter_selection_strategy = OneFilterSelectionStrategy(valued_detected_filters)
        
        while filter_selection_strategy.has_next():
            not_selected_filters, selected_filters = filter_selection_strategy.next() # invert result so we want all the rest filters
            response = self.search_products(
                detected_filters=selected_filters,
                filters_dto=filters_dto,
                search_term=filter_detection_result.search_term,
                context=context,
                page_size=page_size,
            )
            score = response.total_count
            if (best_response is None or score > best_score) and response.total_count > 0:
                best_response = FilteredSearchApiResponse.build_from_search_api_response(
                    response=response,
                    filter_name=not_selected_filters[0].label,
                    is_filter_included=False
                )
                best_score = score
        
        if best_score > 0:
            return best_response
        
        filter_selection_strategy.reset()

        while filter_selection_strategy.has_next():
            selected_filters, _ = filter_selection_strategy.next()
            response = self.search_products(
                detected_filters=selected_filters,
                filters_dto=filters_dto,
                search_term=filter_detection_result.search_term,
                context=context,
                page_size=page_size,
            )
            score = response.total_count
            if (best_response is None or score > best_score) and response.total_count > 0:
                best_response = FilteredSearchApiResponse.build_from_search_api_response(
                    response=response,
                    filter_name=selected_filters[0].label,
                    is_filter_included=True
                )
                best_score = score
        
        if best_score <= 0:
            response = self.search_products(
                [], 
                filters_dto, 
                filter_detection_result.search_term, 
                context,
                page_size)
            return FilteredSearchApiResponse.build_from_search_api_response(
                response=response,
                filter_name=None,
                is_filter_included=False
            )
        else:
            return best_response

    def search_products(
            self,
            detected_filters:List[AttributeFilterValue],
            filters_dto:List[AttributeFilterDto], #attribute_set: str, term:str, filters: List[AttributeFilterValue],
            search_term:str, 
            context:BaseContext,
            page_size: int = 10) -> SearchApiResponse:
        
        json_data = self.graphql_factory.build_data(
            detected_filters=detected_filters, 
            filters_dto=filters_dto,
            search_term=search_term,
            page_size=page_size
        )

        # Log a compact, single-line payload
        log_payload = {
            "query": re.sub(r"\s+", " ", json_data["query"]).strip(),
            "variables": json_data["variables"],
        }
        self.logger.debug_context(message=json.dumps(log_payload, ensure_ascii=False), context=context)

        response = self.post(url=self.url, headers=self.headers, json_data=json_data)
        return self.search_response_builder.build_response(response)
        
    def __insert_credentials(self, url: str, credentials: str) -> str:
        parsed = urlparse(url)
        netloc = f"{credentials}@{parsed.hostname}" + (f":{parsed.port}" if parsed.port else "")
        return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
