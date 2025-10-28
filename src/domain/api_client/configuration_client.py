from abc import ABC, abstractmethod
from domain.models import AttributeSetApiParam, AttributeSetApiResponse

class ConfigurationClient(ABC):
    """Defines the contract for fetching configuration attribute sets from the API."""

    @abstractmethod
    def get_attribute_set(self, params: AttributeSetApiParam) -> AttributeSetApiResponse:
        pass
