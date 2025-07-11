from typing import List

from models import FilterOptionResponse

class AttributeFilterResponse:
    def __init__(self, label:str, code:str, type:str, description:str, options:List[FilterOptionResponse]):
        self.label = label
        self.code = code
        self.type = type
        self.description = description
        self.options = options

    def build_from_api_response(response:dict):
        label = response.get("attribute_label", None)
        code = response.get("attribute_code", None)
        type = response.get("attribute_type", None)
        description = response.get("filter_description", None)
        
        options_dicts = response.get("attribute_options", None)
        options:List[FilterOptionResponse] = []
        if options_dicts:
            for option_dict in options_dicts:
                options.append(FilterOptionResponse.build_from_api_response(option_dict))
        return AttributeFilterResponse(
            label=label,
            code=code,
            type=type,
            description=description,
            options=options
        )