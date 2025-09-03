from langchain.output_parsers import PydanticOutputParser

from config import Settings
from ai import LlmProvider
from prompts import StaticPromptProvider

class BasicPydanticChain:

    def __init__(self, 
            settings: Settings, 
            llm_agent: LlmProvider,
            prompt_provider: StaticPromptProvider,
            pydantic_object: type):
        self.settings = settings
        self.llm_agent = llm_agent
        self.prompt_provider = prompt_provider
        self.pydantic_object = pydantic_object

    def invoke(self, user_message: str):
        output_parser = PydanticOutputParser(pydantic_object=self.pydantic_object)
        format_instructions = output_parser.get_format_instructions()
        prompt_template = self.prompt_provider.get_prompt()

        prompt_template.append(message=("human", "{question}"))

        messages = prompt_template.format_messages(question=user_message, format_instructions=format_instructions)
        output = self.llm_agent.invoke(messages)

        response = output_parser.parse(output.content)
        return response