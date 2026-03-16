from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from application.prompts import StaticPromptProvider
from domain.models.search_context import SearchContext

class LangsmithPromptProvider(StaticPromptProvider):

    def __init__(self, langchain_api_key: str, prompt_name: str):
        self.client = Client(api_key=langchain_api_key)
        self._prompt_name = prompt_name

    @property
    def prompt_name(self) -> str:
        return self._prompt_name

    def get_prompt(self) -> ChatPromptTemplate:
        return self.client.pull_prompt(self.prompt_name)