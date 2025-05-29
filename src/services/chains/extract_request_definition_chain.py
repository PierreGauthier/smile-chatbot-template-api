from typing import List, Annotated
from fastapi import Depends
from config import Settings

from langchain.output_parsers import PydanticOutputParser

from config import Settings, get_settings
from services import ILlmService, AzureOpenAiLlmService
from models import ChatMessage, RequestDefinitionField
from prompts import IPromptProvider, LangsmithExtractRequestPromptProvider

class ExtractRequestDefinitionChain:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)],
            prompt_provider: Annotated[IPromptProvider, Depends(LangsmithExtractRequestPromptProvider)],
            llm_service: Annotated[ILlmService, Depends(AzureOpenAiLlmService)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm = llm_service.get_llm()
        self.max_attempts = 3

    def try_build_request_definition(self, nl_request: str, previous_messages: List[ChatMessage]):
        json_request: None
        attempts = 0
        while attempts < self.max_attempts:
            if attempts > 0:
                print(f"Retry {attempts + 1}: build JSON typology request.")
            attempts += 1            
            json_request = self.__build_json_request(nl_request, previous_messages)
            if json_request:
                return json_request
        return None
    
    def __build_json_request(self, new_user_request: str, previous_messages: List[ChatMessage]):

        output_parser = PydanticOutputParser(pydantic_object=RequestDefinitionField)
        format_instructions = output_parser.get_format_instructions()
        
        prompt_template = self.prompt_provider.get_prompt(previous_messages)
        
        new_message = ChatMessage.create_human_message(message="{question}")
        prompt_template.append(message=new_message.get_tuple_for_prompt())

        messages = prompt_template.format_messages(question=new_user_request, format_instructions=format_instructions)
        output = self.llm.invoke(messages)

        response = output_parser.parse(output.content)
        return response

    
    
    
        