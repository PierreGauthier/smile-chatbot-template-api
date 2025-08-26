from pydantic import BaseModel, Field

class PriceRangeField(BaseModel):
    """
    Represents a price range with lower and upper bounds.
    Useful for filtering, validation, or constraining values within a specific monetary range.
    """
    min_price: float = Field(description="The minimum price allowed or applicable in this range.")
    max_price: float = Field(description="The maximum price allowed or applicable in this range.")