from pydantic import BaseModel, Field

class AttributeField(BaseModel):
    products:list[str] = Field(description="the list of the products that the user searches")
    is_intent:bool = Field(description="whether the user's request is about searching for a product or not")
    chain_of_thoughts:str = Field(description="An explanation why you chose the value for `product` and `is_intent`")