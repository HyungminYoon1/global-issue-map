from typing import List, Optional
from pydantic import BaseModel


class NewsBase(BaseModel):
    id: str
    title: str
    source: str
    published_at: str
    summary: str
    country: str
    continent: str
    region: str
    category: str
    keywords: List[str] = []
    lat: float
    lng: float
    importance: int
    pin_size: str
    pin_color: str


class AiAnalysis(BaseModel):
    article_id: str
    interpretation: str
    prediction: str
    impact: dict
