from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True)
    published_at = Column(String)
    source = Column(String, index=True)
    click_count = Column(Integer, default=0)

class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, index=True)
    searched_at = Column(DateTime, server_default=func.now())