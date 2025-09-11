import json
from pydantic import BaseModel, Field, create_model
from typing import Any, List

from domain.fields import PriceRangeField, PydanticSchema

def build_pydantic_model(schemas: List[PydanticSchema]) -> type[BaseModel]:
    """
    Turn a Pydantic schema into a live Pydantic model class.
    """
    model_name = "DynamicModel"
    field_defs: dict[str, tuple[type, Any]] = {}

    for schema in schemas:
        description = schema.description or f"The {schema.name} of the product"
        py_type = PriceRangeField if schema.type == "price" else str
        default  = ... if schema.required else None
        field_defs[schema.name] = (
            py_type,
            Field(default, description=description)
        )

    # Pydantic does all the leg-work (validators, schema generation, etc.)
    return create_model(model_name, __base__=BaseModel, **field_defs)
