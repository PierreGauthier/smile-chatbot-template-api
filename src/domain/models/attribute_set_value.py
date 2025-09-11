from dataclasses import dataclass

from domain.models import AttributeSetDefinition

@dataclass
class AttributeSetValue(AttributeSetDefinition):
    value:str