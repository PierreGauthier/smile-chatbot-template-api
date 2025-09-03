from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate

from config import Settings, get_settings
from ai import LlmProvider
from models import UserRequestDto, SearchResponseItem
from prompts import StaticPromptProvider
from dependencies import inject_llm_provider, inject_search_response_prompt, inject_empty_search_response_prompt

class SearchResponseBuilderAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            empty_search_prompt_provider: Annotated[StaticPromptProvider, Depends(inject_empty_search_response_prompt)],
            not_empty_search_prompt_provider: Annotated[StaticPromptProvider, Depends(inject_search_response_prompt)]):
        self.settings = settings
        self.empty_search_prompt_provider = empty_search_prompt_provider
        self.not_empty_search_prompt_provider = not_empty_search_prompt_provider
        self.llm_agent = llm_agent
    
    def invoke_empty(self, requests: List[UserRequestDto]):
        request_items = []
        for request in requests:
            request_items.extend([
                f"- {key}={self.__build_filter_value(request, key)}" for key in request.data.keys()
            ])        
        new_message = '\n'.join(request_items)
        return self.__invoke(message=new_message, prompt_template=self.empty_search_prompt_provider.get_prompt())
    
    def invoke_not_empty(self, requests: List[UserRequestDto], search_result:List[SearchResponseItem], total_count:int):
        search_items_str = "Search Result:\n" '\n'.join([
            f"* {self.__build_product(item)}" for item in search_result[:5]
        ])
        request_items = []
        for request in requests:
            request_items.extend([
                f"- {key}={self.__build_filter_value(request, key)}" for key in request.data.keys()
            ])
        request_items_str = "Filters:\n" '\n'.join(request_items)
        new_message = '\n'.join([search_items_str, request_items_str, f"Total Results:{total_count}"])
        return self.__invoke(message=new_message, prompt_template=self.not_empty_search_prompt_provider.get_prompt())


    def __invoke(self, message:str, prompt_template:ChatPromptTemplate):
        
        new_message = ("human", message)

        messages = prompt_template.format_messages(question=new_message)
        output = self.llm_agent.invoke(messages)
        return output.content
    
    def __build_filter_value(self, request:UserRequestDto, filter:str):
        if filter == "price":
            min_price = request.data[filter]["min_price"]
            max_price = request.data[filter]["max_price"]
            return f"{min_price}-{max_price}"
        else:
            return request.data[filter]
        
    def __build_product(self, product:SearchResponseItem):
        return f"{product.name} - {product.brand_name} - {product.price}"