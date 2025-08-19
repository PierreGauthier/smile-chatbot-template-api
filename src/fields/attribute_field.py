from pydantic import BaseModel, Field

class AttributeField(BaseModel):
    product:str = Field(description="the name of the product that the user searches")
    is_intent:bool = Field(description="whether the user's request is about searching for a product or not")
    chain_of_thoughts:str = Field(description="An explanation why you chose the value for `product` and `is_intent`")