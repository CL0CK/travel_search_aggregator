from pydantic import BaseModel


class SearchAIRequest(BaseModel):
    query: str
    mock: bool = True


class SearchAIResponse(BaseModel):
    destination: str
    origin: str | None = None
    budget: float | None = None
    results: list
