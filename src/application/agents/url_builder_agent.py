from typing import Dict
from urllib.parse import urlencode, urlparse, urlunparse

from domain.models import SearchContext, AttributeFilterValue
from domain.fields import PriceRangeField


class UrlBuilderAgent:
    """Agent responsible for building Magento search URLs with filters."""

    def build_search_url(self, context: SearchContext) -> str:
        """
        Build a Magento search URL from the search context.
        
        Args:
            context: Search context containing base URL, search term, and filters
            
        Returns:
            Complete URL with search term and filter parameters, or None if no search term
        """
        if not context.url:
            return None
        
        # Get search term from the first request chain result
        if not context.request_chain_results or not context.request_chain_results[0].search_term:
            return None
            
        search_term = context.request_chain_results[0].search_term
        
        # Build query parameters
        params = self._build_query_params(context, search_term)
        
        # Construct final URL
        return self._construct_url(context.url, params)
    
    def _build_query_params(self, context: SearchContext, search_term: str) -> Dict[str, str]:
        """Build query parameters from context filters."""
        params = {"q": search_term}
        
        # Add filters that were actually used in the search
        for filter_value in context.search_used_filters:
            if filter_value.value:
                param_value = self._format_filter_value(filter_value)
                if param_value:
                    params[filter_value.code] = param_value
        
        return params
    
    def _format_filter_value(self, filter_value: AttributeFilterValue) -> str:
        """Format a filter value for URL parameter."""
        value = filter_value.value
        
        # Handle PriceRangeField (can be object or dict)
        if isinstance(value, PriceRangeField):
            min_price = value.min_price
            max_price = value.max_price
        elif isinstance(value, dict) and ('min_price' in value or 'max_price' in value):
            min_price = value.get('min_price', 0)
            max_price = value.get('max_price', 0)
        else:
            # Simple string value
            return str(value)
        
        # Format price range: "150-" or "50-150" or "-150"
        if min_price and max_price:
            return f"{int(min_price)}-{int(max_price)}"
        elif min_price:
            return f"{int(min_price)}-"
        elif max_price:
            return f"-{int(max_price)}"
        
        return None
    
    def _construct_url(self, base_url: str, params: Dict[str, str]) -> str:
        """Construct final URL with query parameters."""
        parsed = urlparse(base_url)
        query_string = urlencode(params)
        
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            query_string,
            parsed.fragment
        ))