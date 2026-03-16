from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

from application.prompts import PromptProvider
from domain.models.search_context import SearchContext

class LocalPromptProvider(PromptProvider[SearchContext]):

    def __init__(self, local_prompts_dir: str, prompt_name: str):
        self._prompts_dir = Path(local_prompts_dir)
        self._prompt_name = prompt_name

    @property
    def prompt_name(self) -> str:
        return self._prompt_name

    def get_prompt(self) -> ChatPromptTemplate:
        file_name = self.prompt_name.replace('-', '_') + '.md'
        file_path = self._prompts_dir / file_name

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        messages = self._parse_prompt_content(content)
        return ChatPromptTemplate.from_messages(messages)

    def _parse_prompt_content(self, content: str) -> list[tuple[str, str]]:
        messages = []

        sections = content.split("---")

        system_content = sections[0].strip()
        messages.append(("system", system_content))

        current_type = None
        for section in sections[1:]:
            section = section.strip()
            if not section:
                continue

            if section.startswith("HUMAN"):
                current_type = "human"
                content_text = section.replace("HUMAN", "").strip()
            elif section.startswith("AI"):
                current_type = "ai"
                content_text = section.replace("AI", "").strip()
            else:
                content_text = section

            if current_type and content_text:
                messages.append((current_type, content_text))

        return messages