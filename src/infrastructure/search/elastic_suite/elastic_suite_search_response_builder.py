from requests import Response
from typing import List

from api_clients import ApiResponseBuilder
from models import SearchApiResponse, ApiResponse, SearchResponseItem

class ElasticSuiteSearchResponseBuilder(ApiResponseBuilder):
    def __init__(self):
        super().__init__("We can't find products with your criteria.")

    def build_response(self, response: Response) -> SearchApiResponse:
        if response.status_code == 200:
            return self.build_from_api_response(response.json())
        else:
            error_message = self.messages.get(response.status_code, "Unknown error.")
            return SearchApiResponse(response.status_code, message=error_message)

    def build_from_api_response(self, response:dict) -> SearchApiResponse:
        if response:
            product = response["data"]["products"]
            total_count = product["total_count"] 
            items:List[SearchResponseItem] = []
            for item in response:
                items.append(self._build_search_result_from_response(item))
            return SearchApiResponse(
                code=200,
                message="Success",
                query="",
                items=item,
                total_count=total_count
            )
        else:
            return ApiResponse(
                code=200,
                message="No attribute set",
                query=""
            )
        
    def _build_search_result_from_response(self, item:dict) -> SearchResponseItem:
        return SearchResponseItem(
            id=item["id"],
            sku=item["sku"],
            name=item["name"],
            brand_name=item["brand_name"],
            price=item["price_range"]["minimum_price"]["final_price"]["value"],
            image_url=item["image"]["url"]
        )