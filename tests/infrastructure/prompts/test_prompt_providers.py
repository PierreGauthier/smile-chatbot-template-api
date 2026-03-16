import pytest
from langchain_core.prompts import ChatPromptTemplate

from infrastructure.prompts.langsmith import LangsmithPromptProvider
from infrastructure.prompts.local import LocalPromptProvider
from config import get_settings, Settings

@pytest.fixture
def settings() -> Settings:
    """Load real settings from environment"""
    return get_settings()

def test_local_provider_raises_on_missing_file(settings: Settings):
    """Test that LocalPromptTemplateProvider raises FileNotFoundError for missing prompts"""
    local_provider = LocalPromptProvider(settings.local_prompts_dir, "non-existent-prompt")
    with pytest.raises(FileNotFoundError):
        local_provider.get_prompt()

@pytest.mark.parametrize("prompt_name_attr", [
    "prompt_name_chit_chat",
    # "langsmith_contextualize_question_prompt_name",
    # "langsmith_extract_request_definition_prompt_name",
    # "langsmith_rag_system_prompt_name",
    # "langsmith_intent_extraction_prompt_name",
    # "langsmith_attribute_set_extraction_prompt_name",
    # "langsmith_filters_extraction_prompt_name",
    "prompt_name_empty_search_response_builder",
    "prompt_name_filters_detection",
    "prompt_name_filters_value_extraction",
    "prompt_name_language_detector",
    "prompt_name_question_summarizer",
    # "langsmith_not_empty_search_response_builder_prompt_name",
    "prompt_name_search_summary",
    "prompt_name_search_response_builder",
    "prompt_name_search_term_extraction",
    "prompt_name_summary_exchange",
])
def test_providers_return_equivalent_prompts(
    settings: Settings,
    prompt_name_attr: str
):
    """Test that both providers return equivalent ChatPromptTemplate objects"""

    # Récupérer la valeur réelle du prompt depuis settings
    prompt_name = getattr(settings, prompt_name_attr)

    langsmith_provider = LangsmithPromptProvider(settings.langchain_api_key, prompt_name)
    local_provider = LocalPromptProvider(settings.local_prompts_dir, prompt_name)

    langsmith_prompt = langsmith_provider.get_prompt()
    local_prompt = local_provider.get_prompt()

    assert isinstance(langsmith_prompt, ChatPromptTemplate)
    assert isinstance(local_prompt, ChatPromptTemplate)

    assert langsmith_prompt.input_variables == local_prompt.input_variables

    dummy_data = {var: f"dummy_{var}" for var in langsmith_prompt.input_variables}
    langsmith_formatted = langsmith_prompt.format_messages(**dummy_data)
    local_formatted = local_prompt.format_messages(**dummy_data)

    for langsmith_msg, local_msg in zip(langsmith_formatted, local_formatted):
        assert _normalize_text(langsmith_msg.text) == _normalize_text(local_msg.text)

# Normalize whitespace: remove extra blank lines, trailing spaces, and leading indentation
def _normalize_text(text) -> str:
    lines = text.split("\n")
    normalized_lines = []
    for line in lines:
        # Remove leading whitespace (indentation) and trailing whitespace
        stripped = line.strip()
        if stripped:  # Only keep non-empty lines
            normalized_lines.append(stripped)
    return "\n".join(normalized_lines)