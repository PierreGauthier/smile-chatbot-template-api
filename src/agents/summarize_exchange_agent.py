from typing import List, Annotated
from fastapi import Depends
from config import Settings

from config import Settings, get_settings
from agents import LlmAgent, AzureOpenAiLlmAgent
from models import ChatMessage
from prompts import PromptProvider, ContextualizePromptProvider

class SummarizeExchangeAgent:

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmAgent, Depends(AzureOpenAiLlmAgent)],
            prompt_provider: Annotated[PromptProvider, Depends(ContextualizePromptProvider)]):
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
