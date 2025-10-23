from langchain_core.output_parsers.pydantic import PydanticOutputParser

from domain.ai import LlmProvider
from application.prompts import StaticPromptProvider

from config import Settings

class BasicPydanticChain:
    """Wraps a prompt template, LLM provider, and Pydantic parser to run structured chats."""

    def __init__(self, 
            settings: Settings, 
            llm_agent: LlmProvider,
            prompt_provider: StaticPromptProvider,
            pydantic_object: type):
        """Store the objects required to invoke the chain.

        Args:
            settings: Global application configuration.
            llm_agent: LLM provider used to execute the chat completion.
            prompt_provider: Prompt template that seeds the conversation.
            pydantic_object: Pydantic model used to validate the response.
        """
        self.settings = settings
        self.llm_agent = llm_agent
        self.prompt_provider = prompt_provider
        self.pydantic_object = pydantic_object

    def invoke(self, user_message: str):
        """Execute the chain and parse the response into the target Pydantic model.

        Args:
            user_message: Latest human message to feed into the prompt template.

        Returns:
            Parsed Pydantic model instance produced by the LLM response.
        """
        output_parser = PydanticOutputParser(pydantic_object=self.pydantic_object)
        format_instructions = output_parser.get_format_instructions()
        prompt_template = self.prompt_provider.get_prompt()

        prompt_template.append(message=("human", "{question}"))

        messages = prompt_template.format_messages(question=user_message, format_instructions=format_instructions)
        output = self.llm_agent.invoke(messages)

        response = output_parser.parse(output.content)
        return response
