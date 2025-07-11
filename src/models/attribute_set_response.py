from typing import List

from models import AttributeFilterResponse

class AttributeSetResponse:

    def __init__(self, id:int, name:str, description:str, filters: List[AttributeFilterResponse]):
        self.id = id
        self.name = name
        self.description = description
        self.filters = filters

    def build_from_api_response(response:dict):
        id = response.get("attribute_set_id", 0)
        name = response.get("attribute_set_name", "-unknown-")
        description = response.get("attribute_set_description", "-")

        filters_dicts = response.get("filters", None)
        filters:List[AttributeFilterResponse] = []
        if filters_dicts:
            for filters_dict in filters_dicts:
                filters.append(AttributeFilterResponse.build_from_api_response(filters_dict))

        return AttributeSetResponse(
            id=id,
            name=name,
            description=description,
            filters=filters
        )
