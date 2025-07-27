from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import db_models, schemas
from datetime import datetime, timedelta

def create_news_articles(db: Session, articles: list[schemas.NewsArticle], source: str):
    new_articles_count = 0
    for article in articles:
        db_article = db.query(db_models.NewsArticle).filter(db_models.NewsArticle.url == article.url).first()
        if not db_article:
            db_article_to_add = db_models.NewsArticle(
                title=article.title,
                url=article.url,
                published_at=article.published_at,
                source=source
            )
            db.add(db_article_to_add)
            new_articles_count += 1
    db.commit()
    return new_articles_count

def get_articles_by_source(db: Session, source: str, skip: int = 0, limit: int = 10):
    return db.query(db_models.NewsArticle).filter(db_models.NewsArticle.source == source).order_by(db_models.NewsArticle.id.desc()).offset(skip).limit(limit).all()

def insert_search_keyword(db: Session, keyword: str):
    search_log = db_models.SearchLog(keyword=keyword)
    db.add(search_log)
    db.commit()
    db.refresh(search_log)
    return search_log

def get_top_keywords(db: Session, limit: int = 10):
    one_day_ago = datetime.now() - timedelta(days=1)
    result = (
        db.query(db_models.SearchLog.keyword, func.count(db_models.SearchLog.keyword).label("count"))
        .filter(db_models.SearchLog.searched_at >= one_day_ago)
        .group_by(db_models.SearchLog.keyword)
        .order_by(func.count(db_models.SearchLog.keyword).desc())
        .limit(limit)
        .all()
    )
    return result

def increment_article_click(db: Session, article_id: int):
    article = db.query(db_models.NewsArticle).filter(db_models.NewsArticle.id == article_id).first()
    if article:
        article.click_count += 1
        db.commit()
        db.refresh(article)
    return article

def get_top_articles_by_click(db: Session, limit: int = 10):
    return db.query(db_models.NewsArticle).order_by(db_models.NewsArticle.click_count.desc()).limit(limit).all()