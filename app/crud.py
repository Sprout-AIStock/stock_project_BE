# app/crud.py
from sqlalchemy.orm import Session
from .models import db_models, schemas # DB 모델과 API 스키마를 둘 다 import

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