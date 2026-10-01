from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    rooms: list[str] = Field(default_factory=list)
    style: str = "modern"
    notes: str = ""
    quantities: dict[str, int] = Field(default_factory=dict)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0, le=10000)
    event_type: str = "birthday"
    venue: str = ""
    city: str = ""
    notes: str = ""

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0)
    occasion: str = "wedding"
    style: str = "elegant"
    outfit_description: str = ""
    notes: str = ""

class RecommendationItem(BaseModel):
    category: str
    title: str
    description: str
    estimated_price: float
    platform: str
    url: str
    why: str

class RecommendationResponse(BaseModel):
    planner: str
    budget: float
    currency: str = "INR"
    allocation: dict[str, float] = Field(default_factory=dict)
    summary: str
    recommendations: list[RecommendationItem]
    tips: list[str] = Field(default_factory=list)
    ai_generated: bool = False
    model: Optional[str] = None
