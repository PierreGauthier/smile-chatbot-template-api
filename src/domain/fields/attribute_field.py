from pydantic import BaseModel, Field

class AttributeField(BaseModel):
    products:list[str] = Field(description="the list of the products that the user searches")
    terms:list[str] = Field(description="for each product in the `products` list, a short search term (1 to 3 words, **in French**) that best represents what the user is searching for. This list must be aligned with the `products` list in order and length.")
    is_intent:bool = Field(description="whether the user's request is about searching for a product or not")
    chain_of_thoughts:str = Field(description="An explanation why you chose the value for `product` and `is_intent`")