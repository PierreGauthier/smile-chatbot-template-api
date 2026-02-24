from typing import Annotated
from fastapi import Depends

from langchain_core.output_parsers.pydantic import PydanticOutputParser

from config import Settings, get_settings
from domain.ai import LlmProvider
from domain.models import SearchContext
from domain.fields import ChitChatField
from application.prompts import StaticPromptProvider
from dependencies import inject_deep_llm_provider, inject_chit_chat_prompt

class ChitChatAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_deep_llm_provider)],
            prompt_provider: Annotated[StaticPromptProvider, Depends(inject_chit_chat_prompt)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, context: SearchContext):
        """
        Detect chit-chat and generate response in the detected language.
        
        Args:
            context: SearchContext containing message thread and detected language
            
        Returns:
            ChitChatField: Parsed response with is_chit_chat flag and answer
        """
        output_parser = PydanticOutputParser(pydantic_object=ChitChatField)
        format_instructions = output_parser.get_format_instructions()
        
        # Pass context to get language-aware prompt
        prompt_template = self.prompt_provider.get_prompt(context)
        
        # Build exchange list
        exchange_list = []
        for message in context.message_thread:
            message_type = "Assistant" if message.type == "ai" else "User"
            exchange_list.append(f"- {message_type}: {message.data.content}")

        new_message = ("human", '\n'.join(exchange_list))
        prompt_template.append(new_message)

        messages = prompt_template.format_messages(
            question=new_message,
            format_instructions=format_instructions
        )
        
        output = self.llm_agent.invoke(messages)
        response = output_parser.parse(output.content)
        return response
