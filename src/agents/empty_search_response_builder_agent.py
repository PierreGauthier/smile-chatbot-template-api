from typing import List, Annotated
from fastapi import Depends
from config import Settings

from config import Settings, get_settings
from ai import LlmProvider
from models import UserRequestDto
from prompts import PromptProvider, EmptySearchResponseBuilderPromptProvider
from dependencies import inject_llm_provider

class EmptySearchResponseBuilderAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[PromptProvider, Depends(EmptySearchResponseBuilderPromptProvider)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, requests: List[UserRequestDto]):

        request_items = []

        for request in requests:
            request_items.extend([
                f"- {key}={self.__build_filter_value(request, key)}" for key in request.data.keys()
            ])

        prompt_template = self.prompt_provider.get_prompt()
        
        new_message = ("human", '\n'.join(request_items))
        prompt_template.append(new_message)

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