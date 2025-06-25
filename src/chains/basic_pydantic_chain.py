from langchain.output_parsers import PydanticOutputParser

from config import Settings
from services import LlmService
from prompts import PromptProvider

class BasicPydanticChain:

    def __init__(self, 
            settings: Settings, 
            llm_service: LlmService,
            prompt_provider: PromptProvider,
            pydantic_object: type):
        self.settings = settings
        self.llm = llm_service.get_llm()
        self.prompt_provider = prompt_provider
        self.pydantic_object = pydantic_object

    def invoke(self, user_message: str):
        output_parser = PydanticOutputParser(pydantic_object=self.pydantic_object)
        format_instructions = output_parser.get_format_instructions()
        prompt_template = self.prompt_provider.get_prompt()

        prompt_template.append(message=("human", "{question}"))

        messages = prompt_template.format_messages(question=user_message, format_instructions=format_instructions)
        output = self.llm.invoke(messages)

        response = output_parser.parse(output.content)
        return response