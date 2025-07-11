from typing import List
from models import ElasticSuiteApiResponse, AttributeSetResponse, AttributeSetApiParam

class AttributeSetApiResponse(ElasticSuiteApiResponse):
    def __init__(self, attributes:List[AttributeSetResponse], code:int, message:str = "", query:str = ""):
        super().__init__(code=code, message=message, query=query)
        self.attributes = attributes

    def build_from_api_response(response:dict, params:AttributeSetApiParam):
        if response:
            attributes:List[AttributeSetResponse] = []
            for attribute_set in response:
                attributes.append(AttributeSetResponse.build_from_api_response(attribute_set))
                return AttributeSetApiResponse(
                    code=200,
                    message="Success",
                    query=params.query,
                    attributes=attributes
                )
        else:
            return ElasticSuiteApiResponse(
                code=200,
                message="No attribute set",
                query=params.query
            )