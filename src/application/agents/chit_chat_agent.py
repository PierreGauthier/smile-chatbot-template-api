from typing import List, Annotated
from fastapi import Depends
from config import Settings

from langchain_core.output_parsers.pydantic import PydanticOutputParser

from domain.ai import LlmProvider
from domain.models import ChatMessage
from domain.fields import ChitChatField

from application.prompts import StaticPromptProvider

from dependencies import inject_deep_llm_provider, inject_chit_chat_prompt
from config import Settings, get_settings

class ChitChatAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_deep_llm_provider)],
            prompt_provider: Annotated[StaticPromptProvider, Depends(inject_chit_chat_prompt)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, exchange: List[ChatMessage]):

        output_parser = PydanticOutputParser(pydantic_object=ChitChatField)
        format_instructions = output_parser.get_format_instructions()
        prompt_template = self.prompt_provider.get_prompt()
        
        exchange_list = []
        for message in exchange:
            message_type = "Assistant" if message.type == "ai" else "User"
            exchange_list.append(f"- {message_type}: {message.data.content}")

        new_message = ("human", '\n'.join(exchange_list))
        prompt_template.append(new_message)

        messages = prompt_template.format_messages(question=new_message, format_instructions=format_instructions)
        output = self.llm_agent.invoke(messages)
        
        response = output_parser.parse(output.content)
        return response
