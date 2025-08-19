from typing import List, Annotated
from fastapi import Depends
from config import Settings

from config import Settings, get_settings
from ai import LlmProvider
from models import ChatMessage
from prompts import PromptProvider, SummaryPromptProvider
from dependencies import inject_llm_provider

class SummarizeExchangeAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_llm_provider)],
            prompt_provider: Annotated[PromptProvider, Depends(SummaryPromptProvider)]):
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, exchange: List[ChatMessage]):

        prompt_template = self.prompt_provider.get_prompt()
        
        exchange_list = []
        for message in exchange:
            message_type = "Assistant" if message.type == "ai" else "User"
            exchange_list.append(f"- {message_type} : {message.data.content}")

        new_message = ("human", '\n'.join(exchange_list))
        prompt_template.append(new_message)

        messages = prompt_template.format_messages(question=new_message)
        output = self.llm_agent.invoke(messages)
        return output.content
