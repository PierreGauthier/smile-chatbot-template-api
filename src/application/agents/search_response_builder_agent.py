from abc import ABC, abstractmethod
from typing import List

from langchain_core.prompts import ChatPromptTemplate

from domain.ai import LlmProvider
from domain.models import UserRequestDto, SearchResponseItem

from application.prompts import StaticPromptProvider

from config import Settings

class SearchResponseBuilderAgent(ABC):

    def __init__(self, 
            settings: Settings, 
            llm_provider: LlmProvider,
            empty_search_prompt_provider: StaticPromptProvider,
            not_empty_search_prompt_provider: StaticPromptProvider):
        self.settings = settings
        self.empty_search_prompt_provider = empty_search_prompt_provider
        self.not_empty_search_prompt_provider = not_empty_search_prompt_provider
        self.llm_provider = llm_provider
    
    def invoke_empty(self, requests: List[UserRequestDto]):
        request_items = []
        for request in requests:
            request_items.extend([
                f"- {key}={self.build_filter_value(request, key)}" 
                for key in request.data.keys()
            ])        
        new_message = '\n'.join(request_items)
        return self.invoke(message=new_message, prompt_template=self.empty_search_prompt_provider.get_prompt())
    
    def invoke_not_empty(self, requests: List[UserRequestDto], search_result:List[SearchResponseItem], total_count:int):
        search_items_str = "Search Result:\n" '\n'.join([
            f"* {self.build_product(item)}" 
            for item in search_result[:5]
        ])
        request_items = []
        for request in requests:
            request_items.extend([
                f"- {key}={self.build_filter_value(request, key)}" 
                for key in request.data.keys()
            ])
        request_items_str = "Filters:\n" '\n'.join(request_items)
        new_message = '\n'.join([search_items_str, request_items_str, f"Total Results:{total_count}"])
        return self.invoke(message=new_message, prompt_template=self.not_empty_search_prompt_provider.get_prompt())


    def invoke(self, message:str, prompt_template:ChatPromptTemplate):
        
        new_message = ("human", message)

        messages = prompt_template.format_messages(question=new_message)
        output = self.llm_provider.invoke(messages)
        return output.content
    
    @abstractmethod
    def build_filter_value(self, request:UserRequestDto, filter:str):
        pass
        
    @abstractmethod
    def build_product(self, product:SearchResponseItem):
        pass