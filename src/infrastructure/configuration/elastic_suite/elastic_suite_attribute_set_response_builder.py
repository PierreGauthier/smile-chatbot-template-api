import re
import uuid
from requests import Response
from typing import List

from domain.api_client import ApiResponseBuilder
from domain.models import (
    ApiResponse, 
    AttributeSetApiResponse, 
    AttributeSetApiParam, 
    AttributeSetDto, 
    AttributeFilterDto,
    FilterOptionDto
)

class ElasticSuiteAttributeSetResponseBuilder(ApiResponseBuilder):

    def __init__(self):
        super().__init__("We can't find information about the attribute set.")

    def build_response(self, params: AttributeSetApiParam, response: Response) -> ApiResponse:
        if response.status_code == 200:
            return self.build_from_api_response(response.json(), params)
        else:
            error_message = self.messages.get(response.status_code, "Unknown error.")
            return ApiResponse(response.status_code, message=error_message)

    def build_from_api_response(self, response:dict, params:AttributeSetApiParam):
        if response:
            attributes:List[AttributeSetDto] = []
            for attribute_set in response:
                attributes.append(self._build_attribute_set_from_response(attribute_set))
            return AttributeSetApiResponse(
                code=200,
                message="Success",
                query=params.query,
                attributes=attributes
            )
        else:
            return ApiResponse(
                code=200,
                message="No attribute set",
                query=params.query
            )
        
    def _extract_name_and_code(self, text: str):
        match = re.match(r'^Pim(?:\s\[\d+\])?\s(.+?)\s\((.+?)\)$', text)
        if match:
            return (match.group(1), match.group(2))
        return (None, None)

    def _build_attribute_set_from_response(self, response:dict):
        attribute_set_id = response.get("attribute_set_id", 0)
        original_name = response.get("attribute_set_name", "-unknown-")
        
        matches = self._extract_name_and_code(original_name)
        name = matches[0] or original_name
        code = matches[1] or name
        
        description = response.get("attribute_set_description", "-")
        
        filters_dicts = response.get("filters", None)
        filters:List[AttributeFilterDto] = []
        if filters_dicts:
            for filters_dict in filters_dicts:
                filters.append(self._build_filter_from_response(filters_dict, attribute_set_id))

        object =  AttributeSetDto(
            id=str(uuid.uuid4()),
            attribute_set_id=attribute_set_id,
            name = name,
            code = code,
            description=description,
            filters=filters
        )
        return object
    
    def _build_filter_from_response(self, response:dict, attribute_id:int):
        label = response.get("attribute_label", None)
        code = response.get("attribute_code", None)
        atr_type = response.get("attribute_type", None)
        description = response.get("filter_description", None)
        
        options = response.get("attribute_options", None)
        options_type = None if not options else type(options[0]).__name__
        
        return AttributeFilterDto(
            id=str(uuid.uuid4()),
            attribute_id=attribute_id,
            label=label,
            code=code,
            type=atr_type,
            description=description,
            options_type=options_type,
            options=options
        )
    
    # def _build_builder_option_from_response(self, response:dict):
    #     return FilterOptionDto(
    #         key=response.get("key", None),
    #         value=response.get("value", None)
    #     )