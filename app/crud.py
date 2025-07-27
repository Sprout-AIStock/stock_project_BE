# app/crud.py

from sqlalchemy.orm import Session
from . import db_models
from .models import schemas
from datetime import datetime

def create_news_articles(db: Session, articles: list[schemas.NewsArticle], source: str):
    """
    여러 개의 뉴스 기사를 DB에 저장합니다. 중복된 URL은 건너뜁니다.
    """
    new_articles_count = 0
    for article in articles:
        # 동일한 URL을 가진 기사가 이미 DB에 있는지 확인
        db_article = db.query(db_models.NewsArticle).filter(db_models.NewsArticle.url == article.url).first()
        
        # DB에 없다면 새로 추가
        if not db_article:
            db_article_to_add = db_models.NewsArticle(
                title=article.title,
                url=article.url,
                published_at=article.published_at,
                source=source
            )
            db.add(db_article_to_add)
            new_articles_count += 1
            
    db.commit() # 변경사항을 DB에 최종 반영
    return new_articles_count


def get_articles_by_source(db: Session, source: str, skip: int = 0, limit: int = 10):
    """
    출처(source)를 기준으로 기사를 조회합니다.
    """
    return db.query(db_models.NewsArticle).filter(db_models.NewsArticle.source == source).order_by(db_models.NewsArticle.id.desc()).offset(skip).limit(limit).all()


def insert_search_keyword(db: Session, keyword: str):
    """
    검색어를 로그 테이블에 저장합니다.
    """
    search_log = db_models.SearchLog(keyword=keyword, searched_at=datetime.utcnow())
    db.add(search_log)
    db.commit()
    db.refresh(search_log)
    return search_log

def get_top_keywords(db: Session, limit: int = 10):
    """
    최근 하루 기준 인기 검색어 TOP N을 조회합니다.
    """
    from sqlalchemy import func
    from datetime import timedelta
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)

    result = (
        db.query(db_models.SearchLog.keyword, func.count(db_models.SearchLog.keyword).label("count"))
        .filter(db_models.SearchLog.searched_at >= one_day_ago)
        .group_by(db_models.SearchLog.keyword)
        .order_by(func.count(db_models.SearchLog.keyword).desc())
        .limit(limit)
        .all()
    )
    return result