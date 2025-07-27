# 뉴스, 주식 정보 등 데이터의 구조(Schema)를 클래스 형태로 정의합니다.

# app/models/schemas.py
from pydantic import BaseModel
from datetime import datetime

class NewsArticle(BaseModel):
    title: str
    url: str
    published_at: datetime
