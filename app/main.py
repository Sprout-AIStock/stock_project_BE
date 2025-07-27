# app/main.py (수정)
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# 내부 모듈 import
from app import crud, models
from app.database import SessionLocal, engine, Base
from app.services.scheduler import start_scheduler
# (다른 import 구문들은 이전과 동일)
from app.models.schemas import StockInfo, Insight, NewsArticle # API 모델은 그대로 사용

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI 금융 정보 서비스")

# DB 세션을 얻기 위한 Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    start_scheduler()

# ( / , /api/stock/info/{...}, /api/insight/{...} 엔드포인트는 이전과 동일)
# ...

@app.get("/api/news/macro", response_model=List[NewsArticle])
def get_macro_news(db: Session = Depends(get_db)):
    """DB에서 거시 경제 메인 이슈 목록을 조회하여 반환합니다."""
    articles = crud.get_articles_by_source(db=db, source="macro", limit=5)
    return articles