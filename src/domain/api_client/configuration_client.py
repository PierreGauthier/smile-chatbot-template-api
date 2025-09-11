from abc import ABC, abstractmethod
from domain.models import AttributeSetApiParam, AttributeSetApiResponse

class ConfigurationClient(ABC):

    @abstractmethod
    def get_attribute_set(self, params: AttributeSetApiParam) -> AttributeSetApiResponse:
        pass