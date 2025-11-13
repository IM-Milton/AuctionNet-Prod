from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from typing import Literal


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class ProductSchema(BaseModel):
    title: str
    description: str
    category: str
    images: List[str] = [] # paths relative to /data/media or external URLs
    condition: Literal["new", "used"]

class AuctionCreateSchema(BaseModel):
    product_id: str
    start_price: float
    start_at: str # ISO8601 with timezone, e.g. 2025-11-10T12:00:00Z
    end_at: str
    min_increment: float = 50.0


class BidSchema(BaseModel):
    amount: float