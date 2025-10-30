from typing import List, Annotated
from fastapi import Depends
from config import Settings

from domain.ai import LlmProvider
from domain.models import ChatMessage, Language

from application.prompts import SummarizeExchangePromptProvider

from dependencies import inject_deep_llm_provider, inject_exchange_summarizer_prompt
from config import Settings, get_settings

class ExchangeSummarizerAgent:
    """Summarizes user and assistant messages into a concise exchange overview."""

    def __init__(self, 
            settings: Annotated[Settings, Depends(get_settings)], 
            llm_agent: Annotated[LlmProvider, Depends(inject_deep_llm_provider)],
            prompt_provider: Annotated[SummarizeExchangePromptProvider, Depends(inject_exchange_summarizer_prompt)]):
        """Initialize with configuration, language model provider, and prompt builder."""
        self.settings = settings
        self.prompt_provider = prompt_provider
        self.llm_agent = llm_agent
    
    def invoke(self, exchange: List[ChatMessage], chat_lang:Language):
        """Generate a summary for the given chat exchange in the requested language."""

        prompt_template = self.prompt_provider.get_prompt(chat_lang)
        
        exchange_list = []
        for message in exchange:
            message_type = "Assistant" if message.type == "ai" else "User"
            exchange_list.append(f"- {message_type}: {message.data.content}")

        new_message = ("human", '\n'.join(exchange_list))
        prompt_template.append(new_message)

        messages = prompt_template.format_messages(question=new_message)
        output = self.llm_agent.invoke(messages)
        return output.content
