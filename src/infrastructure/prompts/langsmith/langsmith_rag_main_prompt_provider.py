from typing import List, Annotated
from fastapi import Depends

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

from application.prompts import RagMainPromptProvider

from config import Settings, get_settings

class LangsmithRagMainPromptProvider(RagMainPromptProvider):

    def __init__(self, settings: Annotated[Settings, Depends(get_settings)]):
        self.client = Client(api_key=settings.langchain_api_key)
        self.prompt_name = settings.langsmith_rag_system_prompt_name

    def get_prompt(self, exchange:str, extra_info:List[str] = []) -> ChatPromptTemplate:
        rag_prompt:ChatPromptTemplate = self.client.pull_prompt(self.prompt_name)
        
        if extra_info:
            extra_info_text = "# Supplementary Information\n"
            extra_info_text += "The following information is to take into account as a context complement:\n"
            extra_info_text += "\n".join([f"- {info}" for info in extra_info])
            rag_prompt = rag_prompt.partial(extra_info=extra_info_text)
        else:
            rag_prompt = rag_prompt.partial(extra_info="")

        if exchange:
            extra_info_text = "# Exchange summary\n"
            extra_info_text += f"This is a summary of the exchange between the user and the assistant:\n {exchange}"
            rag_prompt = rag_prompt.partial(exchange=extra_info_text)
        else:
            rag_prompt = rag_prompt.partial(exchange="")

        return rag_prompt