from pydantic import BaseModel


class RecommendRequest(BaseModel):
    query: str


class RecommendResponse(BaseModel):
    destination: str
    budget: float | None
    results: list
