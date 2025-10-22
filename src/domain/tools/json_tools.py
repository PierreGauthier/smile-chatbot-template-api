import json as json_module
import re
from typing import Any, Dict, List, Union

from domain.fields import PydanticSchema

def repair_llm_pydantic_answer(json: Union[str, Dict[str, Any]], schemas: List[PydanticSchema]) -> str:
    # Assume 'json' is a string
    cleaned = re.sub(r'^```(?:json)?\n?|```$', '', json.strip(), flags=re.MULTILINE)
    try:
        parsed: Dict[str, Any] = json_module.loads(cleaned)
    except (TypeError, ValueError):
        return json
    original_json = json

    schema_by_name = {schema.name: schema for schema in schemas}
    changed = False

    for key, value in parsed.items():
        schema = schema_by_name.get(key)
        if not schema:
            continue

        expected_type = schema.field_type
        if expected_type not in (int, str):
            continue

        if isinstance(value, expected_type):
            continue

        if value in ("", 0):
            replacement = "" if expected_type is str else 0
            if value != replacement:
                parsed[key] = replacement
                changed = True
            continue

        if isinstance(value, int) and expected_type is str:
            parsed[key] = str(value)
            changed = True
            continue

        if isinstance(value, str) and expected_type is int:
            stripped_value = value.strip()
            if stripped_value:
                try:
                    parsed[key] = int(stripped_value)
                    changed = True
                except ValueError:
                    pass

    return f'```json\n{json_module.dumps(parsed)}```' if changed else original_json
