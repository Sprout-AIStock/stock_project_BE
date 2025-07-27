# app/db_models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class SearchLog(Base):
    __tablename__ = "search_log"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), nullable=False)
    searched_at = Column(DateTime, default=datetime.utcnow)

class StockInfo(Base):
    __tablename__ = "stock_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True)

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False, unique=True)
    published_at = Column(DateTime, nullable=False)
    source = Column(String(100), nullable=False)
    click_count = Column(Integer, default=0)