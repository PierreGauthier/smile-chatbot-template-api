import json, sys, types, re
from dataclasses import dataclass
from pathlib import Path

if "pydantic" not in sys.modules:
    pydantic_stub = types.ModuleType("pydantic")

    class BaseModel:
        pass

    def Field(*args, **kwargs):
        return None

    def create_model(name, __base__=object, **fields):
        attributes = {key: None for key in fields}
        return type(name, (__base__,), attributes)

    pydantic_stub.BaseModel = BaseModel
    pydantic_stub.Field = Field
    pydantic_stub.create_model = create_model
    sys.modules["pydantic"] = pydantic_stub

sys.path.append(str(Path(__file__).resolve().parents[3] / "src"))

from domain.tools.json_tools import repair_llm_pydantic_answer

@dataclass
class SchemaStub:
    name: str
    field_type: type
    required: bool = False
    description: str = ""


EXAMPLE_JSON = (
    '```json\n{"key_01": "", "key_02": 0, "key_03": 0, '
    '"key_to_test": 0, '
    '"ai_question": "This is an AI question"}```'
)


def test_repair_llm_pydantic_answer_converts_zero_to_empty_string():
    schemas = [SchemaStub(name="key_to_test", field_type=str)]

    result = repair_llm_pydantic_answer(EXAMPLE_JSON, schemas)

    assert result != EXAMPLE_JSON
    cleaned = re.sub(r'^```(?:json)?\n?|```$', '', result.strip(), flags=re.MULTILINE)
    parsed = json.loads(cleaned)
    assert parsed["key_to_test"] == ""


def test_repair_llm_pydantic_answer_leaves_int_zero_unchanged():
    schemas = [SchemaStub(name="key_02", field_type=int)]
    result = repair_llm_pydantic_answer(EXAMPLE_JSON, schemas)
    assert result == EXAMPLE_JSON

# pytest tests/domain/tools/test_json_tools.py 