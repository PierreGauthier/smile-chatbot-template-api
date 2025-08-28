from dataclasses import dataclass

from models import AttributeSetDefinition

@dataclass
class AttributeSetValue(AttributeSetDefinition):
    value:str