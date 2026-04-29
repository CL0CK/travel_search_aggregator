import uuid
from datetime import datetime
from typing import TypedDict
from pydantic import BaseModel, ConfigDict


class TripDTO(TypedDict):
    destination: str
    price: float
    rating: float
    provider: str


class TripCreate(BaseModel):
    destination: str
    price: float
    rating: float
    provider: str


class TripRead(BaseModel):
    id: uuid.UUID
    destination: str
    price: float
    rating: float
    provider: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)