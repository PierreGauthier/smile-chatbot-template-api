import json
from pydantic import BaseModel, Field, create_model
from typing import Any

# 1. Map the strings you expect in the JSON → real Python / typing types
TYPE_LOOKUP: dict[str, Any] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list[str]": list[str],     # Python 3.9+ syntax
    "list[int]": list[int],
    # add other shapes such as "Optional[str]" etc. as needed
}

def build_pydantic_model(schema: dict) -> type[BaseModel]:
    """
    Turn the JSON schema above into a live Pydantic model class.
    """
    model_name = schema.get("model_name", "DynamicModel")
    field_defs: dict[str, tuple[type, Any]] = {}

    for f in schema["fields"]:
        py_type = TYPE_LOOKUP[f["type"]]         # resolve the string → real type
        default  = ... if f.get("required", True) else None
        field_defs[f["name"]] = (
            py_type,
            Field(default, description=f.get("description"))
        )

    # Pydantic does all the leg-work (validators, schema generation, etc.)
    return create_model(model_name, __base__=BaseModel, **field_defs)
