from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

from domain.models import ChatMessage

from application.prompts import QuestionSummarizerPromptProvider

from config import Settings, get_settings

class LangsmithQuestionSummarizerPromptProvider(QuestionSummarizerPromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.prompt_name = settings.langsmith_elastic_suite_question_summarizer_prompt_name

    def get_prompt(self, exchange:List[ChatMessage]) -> ChatPromptTemplate:
        prompt: ChatPromptTemplate = hub.pull(self.prompt_name)

        exchange_list = [
            f"- {('Assistant' if message.type == 'ai' else 'User')}: {message.data.content}"
            for message in exchange
        ]
        formatted_exchange = "\n".join(exchange_list)
        prompt = prompt.partial(exchange=formatted_exchange)
        return prompt
