# app/models/db_models.py
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True) # 중복 저장을 막기 위해 URL은 고유값으로 설정
    published_at = Column(String)
    source = Column(String, index=True) # 'macro', 'themed' 등 출처 구분