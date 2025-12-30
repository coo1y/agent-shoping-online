from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from uuid import UUID

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price_cents: int
    currency: str = "USD"
    brand: Optional[str] = None
    category: str
    image_url: Optional[str] = None
    is_active: bool = True
    
    # New fields
    aliases: List[str] = []
    specs: Dict[str, Any] = {}
    rating: Optional[float] = None
    popularity: int = 0

class ProductCreate(ProductBase):
    product_id: str

class Product(ProductBase):
    product_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
