from pydantic import BaseModel
from typing import List, Optional

class NewsArticle(BaseModel):
    id: int
    title: str
    url: str
    published_at: str
    click_count: int

    class Config:
        from_attributes = True

class StockDetail(BaseModel):
    code: str
    name: str
    price: str
    market_cap: str
    per: str
    pbr: str

class TopKeyword(BaseModel):
    keyword: str
    count: int

class Insight(BaseModel):
    stock_name: str
    conclusion: str
    report: str