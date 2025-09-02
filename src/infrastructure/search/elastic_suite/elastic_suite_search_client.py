from api_clients import BaseClient
from typing import Annotated, List
from fastapi import Depends
from urllib.parse import urlparse, urlunparse

from config import Settings, get_settings
from models import SearchApiResponse, AttributeFilterValue
from api_clients import ConversationalSearchClient
from infrastructure.search.elastic_suite import ElasticSuiteSearchResponseBuilder

class ElasticSuiteSearchClient(ConversationalSearchClient):

    def __init__(
            self, 
            settings: Annotated[Settings, Depends(get_settings)],
            search_response_builder: Annotated[ElasticSuiteSearchResponseBuilder, Depends(ElasticSuiteSearchResponseBuilder)]):
        super().__init__(settings.elastic_suite_search_api_base_url)
        self.settings = settings
        self.search_response_builder = search_response_builder

    def search_products(self, attribute_set:str, filters:List[AttributeFilterValue], page_size:int = 10) -> SearchApiResponse:
        url = self.__insert_credentials(url=self.api_base_url, credentials=self.settings.elastic_suite_search_api_credentials)
        # query =
        (x_correlation_id_key, x_correlation_id_value) = self.create_x_correlation_id()
        (content_type_key, content_type_value) = self.create_json_content_type()
        
        headers = {
            x_correlation_id_key: x_correlation_id_value,
            content_type_key: content_type_value,
            "Store": "lamaison"
        }
        # print(url)
        json_data = self.__build_data(product_name=attribute_set, filters=filters, page_size=page_size)
        response = self.post(url=url, headers=headers, json_data=json_data)
        return self.search_response_builder.build_response(response)

    def __build_data(self, product_name:str, filters:List[AttributeFilterValue], page_size):
        filter_param_definition = " ".join([f"{self.__build_param(f)}" for f in filters])
        query_header = f"query ($term: String!, {filter_param_definition} $pageSize: Int = 1)"
        filter_value_definition = ", ".join([self.__build_param_definition(f) for f in filters])
        query_products = f"products(search: $term filter: {{ {filter_value_definition} }} pageSize: $pageSize)"
        query_tale = """
        {
            total_count
            items {
                id
                sku
                name
                brand_name
                price_range {
                    minimum_price {
                        final_price {
                            value
                            currency
                        }
                    }
                }
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
                options {
                    label
                    value
                }
            }
        }
        """
        query = f"{query_header} {{ {query_products} {query_tale} }}"
        variables  = {}
        for f in filters:
            if f.type == "price":
                variables["min_price"] = f.value["min_price"]
                variables["max_price"] = f.value["max_price"]
            else:
                variables[f.code] = f.value
        variables["term"] = product_name
        variables["pageSize"] = page_size
        data = { "query": query, "variables": variables }
        return data
    
    def __build_param(self, filter:AttributeFilterValue):
        if not filter.value:
            return ""
        return "$min_price: String!, $max_price: String!," if filter.type == "price" else f"${filter.code}:String!,"
        
    
    def __build_param_definition(self, filter:AttributeFilterValue):
        if not filter.value:
            return ""
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
        """
        Insert credentials (username:password) into a given URL.
        Args:
            url (str): The base URL (e.g. https://example.com/path)
            credentials (str): The credentials in format username:password        
        Returns:
            str: The URL with credentials inserted
        """
        parsed = urlparse(url)
        # Build netloc: user:pass@host[:port]
        if parsed.port:
            netloc = f"{credentials}@{parsed.hostname}:{parsed.port}"
        else:
            netloc = f"{credentials}@{parsed.hostname}"
        
        # Rebuild the full URL
        new_url = urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        return new_url