import json
import re
from typing import Annotated, List
from fastapi import Depends
from urllib.parse import urlparse, urlunparse

from domain.models import SearchApiResponse, AttributeFilterValue
from domain.api_client import ConversationalSearchClient
from domain.logger import ContextLogger
from infrastructure.search.elastic_suite import ElasticSuiteSearchResponseBuilder
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

    def search_products(self, attribute_set: str, filters: List[AttributeFilterValue], page_size: int = 10) -> SearchApiResponse:
        url = self.__insert_credentials(
            url=self.api_base_url,
            credentials=self.settings.elastic_suite_search_api_credentials,
        )
        (x_correlation_id_key, x_correlation_id_value) = self.create_x_correlation_id()
        (content_type_key, content_type_value) = self.create_json_content_type()

        headers = {
            x_correlation_id_key: x_correlation_id_value,
            content_type_key: content_type_value,
            "Store": "lamaison",
        }

        json_data = self.__build_data(product_name=attribute_set, filters=filters, page_size=page_size)

        # Log a compact, single-line payload
        log_payload = {
            "query": re.sub(r"\s+", " ", json_data["query"]).strip(),
            "variables": json_data["variables"],
        }
        self.logger.debug(msg=json.dumps(log_payload, ensure_ascii=False))

        response = self.post(url=url, headers=headers, json_data=json_data)
        return self.search_response_builder.build_response(response)

    def __build_data(self, product_name: str, filters: List[AttributeFilterValue], page_size: int):
        # Build variable param declarations (skip empties)
        param_decls = [self.__build_param(f) for f in filters if f.value]
        params_header = ", ".join(["$term: String!"] + param_decls + ["$pageSize: Int = 1"])

        # Build filter arguments (skip empties)
        filter_args = [self.__build_param_definition(f) for f in filters if f.value]
        filter_args_str = ", ".join(filter_args)

        query_tale = """
        {
            total_count
            items {
                id
                sku
                name
                price_range { minimum_price { final_price { value currency } } }
                image { url }
            }
            page_info {
                current_page
                page_size
                total_pages
            }
            aggregations {
                attribute_code
                frontend_input
                options { label value }
            }
        }
        """

        query_products = f"products(search: $term filter: {{ {filter_args_str} }} pageSize: $pageSize)"
        query = f"query ({params_header}) {{ {query_products} {query_tale} }}"

        variables = {}
        for f in filters:
            if not f.value:
                continue
            if f.type == "price":
                variables["min_price"] = f.value["min_price"]
                variables["max_price"] = f.value["max_price"]
            else:
                variables[f.code] = f.value

        variables["term"] = product_name
        variables["pageSize"] = page_size

        return {"query": query, "variables": variables}

    def __build_param(self, filter: AttributeFilterValue) -> str:
        if filter.type == "price":
            return "$min_price: String!, $max_price: String!"
        return f"${filter.code}: String!"

    def __build_param_definition(self, filter: AttributeFilterValue) -> str:
        match filter.type:
            case "price":
                return "price: { from: $min_price, to: $max_price }"
            case "select":
                return f"{filter.code}: {{ eq: ${filter.code} }}"
            case "smile_custom_entity":
                return f"{filter.code}: {{ match: ${filter.code} }}"
            case _:
                raise ValueError(f"Unsupported filter data-type: {filter.type}")

    def __insert_credentials(self, url: str, credentials: str) -> str:
        parsed = urlparse(url)
        netloc = f"{credentials}@{parsed.hostname}" + (f":{parsed.port}" if parsed.port else "")
        return urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
