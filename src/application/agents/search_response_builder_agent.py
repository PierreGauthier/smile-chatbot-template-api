from abc import ABC, abstractmethod
from typing import List

from langchain_core.prompts import ChatPromptTemplate

from domain.ai import LlmProvider
from domain.models import UserRequestDto, SearchResponseItem, SearchContext, AttributeFilterDto

from application.prompts import StaticPromptProvider

from config import Settings

class SearchResponseBuilderAgent(ABC):
    """Base agent responsible for crafting LLM-ready messages from search context data."""

    def __init__(self, 
            settings: Settings,
            llm_provider: LlmProvider,
            empty_search_prompt_provider: StaticPromptProvider,
            not_empty_search_prompt_provider: StaticPromptProvider):
        """Store dependencies needed for preparing prompts and invoking the LLM."""
        self.settings = settings
        self.empty_search_prompt_provider = empty_search_prompt_provider
        self.not_empty_search_prompt_provider = not_empty_search_prompt_provider
        self.llm_provider = llm_provider
    
    def invoke_empty(self, context: SearchContext):
        """Generate a response when search results are empty."""
        request_items = []
        exchange_list = []
        for message in context.message_thread:
            message_type = "Assistant" if message.type == "ai" else "User"
            exchange_list.append(f"- {message_type}: {message.data.content}")

        for request in context.requests:
            request_items.extend([
                f"- {self.build_filter_value_expression(request, self.__find_filter(key, request, context))}" 
                for key in request.data.keys()
            ])

        result_components = [
            "Filters:\n" + '\n'.join(request_items),
            "Exchange:\n" + '\n'.join(exchange_list),
            f"Output Language: {context.chat_lang.lang_name}"
        ]
        
        new_message = '\n'.join(result_components)
        return self.invoke(message=new_message, prompt_template=self.empty_search_prompt_provider.get_prompt())
    
    def invoke_not_empty(
            self, 
            context: SearchContext, 
            search_result:List[SearchResponseItem], 
            filter_name:str,
            is_included: bool,
            total_count:int):
 
        search_items_str = "Search Result:\n" '\n'.join([
            f"* {self.build_product(item)}" 
            for item in search_result[:5]
        ])
        request_items = []
        for request in context.requests:
            request_items.extend([
                f"- {self.build_filter_value_expression(request, self.__find_filter(key, request, context))}" 
                for key in request.data.keys()
            ])
        request_items_str = "Filters:\n" '\n'.join(request_items)
        new_message = '\n'.join([
            search_items_str, request_items_str, 
            f"Total Results:{total_count}",
            f"Output Language: {context.chat_lang.lang_name}",
            f"Relevant Filter: {filter_name}",
            f"Is Included: {is_included}"
        ])
        return self.invoke(message=new_message, prompt_template=self.not_empty_search_prompt_provider.get_prompt())

    def invoke(self, message:str, prompt_template:ChatPromptTemplate):
        """Invoke the configured LLM with the provided message and prompt template."""
        
        new_message = ("human", message)

        messages = prompt_template.format_messages(question=new_message)
        output = self.llm_provider.invoke(messages)
        return output.content
    
    def __find_filter(self, filter_code:str, request:UserRequestDto, context:SearchContext):
        """Locate the filter metadata matching a request attribute."""
        attribute_set = next((attr for attr in context.attribute_sets if attr.attribute_set_id == request.attribute_id), None)
        if attribute_set:
            filter = next((f for f in attribute_set.filters if f.code == filter_code), None)
            return filter
        raise KeyError(f"No filter found ({filter_code})")
    
    @abstractmethod
    def build_filter_value_expression(self, request:UserRequestDto, filter:AttributeFilterDto):
        """Return a string describing the request/filter pair for LLM consumption."""
        pass
        
    @abstractmethod
    def build_product(self, product:SearchResponseItem):
        """Return a string representation of a product suitable for the LLM prompt."""
        pass
