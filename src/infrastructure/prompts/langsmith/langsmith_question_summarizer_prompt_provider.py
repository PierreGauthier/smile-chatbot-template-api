from typing import Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from domain.models import SearchContext

from application.prompts import PromptProvider

from config import Settings, get_settings

class LangsmithQuestionSummarizerPromptProvider(PromptProvider[SearchContext]):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.langsmith_elastic_suite_question_summarizer_prompt_name

    def get_prompt(self, context:SearchContext) -> ChatPromptTemplate:
        prompt: ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)

        exchange_list = [
            f"- {('Assistant' if message.type == 'ai' else 'User')}: {message.data.content}"
            for message in context.message_thread
        ]
        formatted_exchange = "\n".join(exchange_list)
        prompt = prompt.partial(exchange=formatted_exchange)
        return prompt
