import uuid
from datetime import datetime
from typing import TypedDict
from pydantic import BaseModel, ConfigDict


class TripDTO(TypedDict, total=False):
    destination: str
    price: float
    rating: float
    provider: str
    origin: str
    hotel_stars: int
    flight_price: float
    hotel_price: float


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
    origin: str | None = None
    hotel_stars: int | None = None
    flight_price: float | None = None
    hotel_price: float | None = None

    model_config = ConfigDict(from_attributes=True)