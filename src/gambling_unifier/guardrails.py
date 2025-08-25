from typing import List, Optional
from pydantic import BaseModel, Field


class ProductRecord(BaseModel):
    site: str = Field(..., description="Source site identifier, e.g., polymarket")
    product_id: str = Field(..., description="Site-specific market/product id or slug")
    name: str = Field(..., description="Canonical product/market name")
    price: Optional[float] = Field(None, description="Price/YES price/last traded price if available")
    url: Optional[str] = Field(None, description="Source URL")


class ScrapeResult(BaseModel):
    products: List[ProductRecord] = Field(default_factory=list)


class UnifiedProduct(BaseModel):
    name: str
    aliases: List[str]
    entries: List[ProductRecord]
    confidence: float


