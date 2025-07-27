# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# 내부 모듈 import
from app import crud
# 'stock_info'와 'insight_generator'는 특정 함수를 직접 호출하므로 그대로 둡니다.
from app.core import stock_info, insight_generator
from app.database import SessionLocal, engine, Base
from app.services.scheduler import start_scheduler
# 👇 아래 import 구문을 수정합니다.
from app.models.schemas import StockInfo, Insight, NewsArticle, StockDetail, TopSearchedStock

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

@app.get("/")
def read_root():
    return {"message": "AI 금융 정보 서버에 오신 것을 환영합니다!"}

@app.get("/api/news/macro", response_model=List[NewsArticle]) # 👈 NewsArticleSchema -> NewsArticle
def get_macro_news(db: Session = Depends(get_db)):
    articles = crud.get_articles_by_source(db=db, source="macro", limit=5)
    return articles

@app.get("/api/themes", response_model=List[str])
def get_available_themes():
    themes = stock_info.get_investment_themes()
    if themes is None:
        return ["반도체", "2차전지", "인공지능", "바이오/제약"]
    return themes

@app.get("/api/news/theme/{theme_name}", response_model=List[NewsArticle]) # 👈 NewsArticleSchema -> NewsArticle
def get_news_by_theme(theme_name: str, db: Session = Depends(get_db)):
    MAIN_THEMES = ["반도체", "2차전지", "인공지능"]

    if theme_name in MAIN_THEMES:
        articles = crud.get_articles_by_source(db=db, source=theme_name, limit=5)
        return articles
    else:
        articles = stock_info.get_articles_by_theme(theme_name=theme_name, limit=5)
        if articles is None:
            raise HTTPException(status_code=404, detail="해당 테마의 기사를 가져올 수 없습니다.")
        return articles

@app.get("/api/stock/search/{stock_code}", response_model=StockDetail)
def search_stock_details(stock_code: str, db: Session = Depends(get_db)):
    details = stock_info.get_stock_details_from_naver(stock_code)
    if not details:
        raise HTTPException(status_code=404, detail="종목 정보를 가져올 수 없습니다.")
    crud.log_stock_search(db=db, stock_code=stock_code, stock_name=details.name)
    return details

@app.get("/api/stocks/top-searched", response_model=List[TopSearchedStock])
def get_top_stocks(db: Session = Depends(get_db)):
    top_stocks = crud.get_top_searched_stocks(db=db, limit=10)
    return top_stocks

@app.get("/api/insight/{stock_code}", response_model=Insight)
def get_ai_insight(stock_code: str):
    stock = stock_info.get_stock_details_from_naver(stock_code)
    if not stock:
        raise HTTPException(status_code=404, detail="종목을 찾을 수 없습니다.")

    conclusion = insight_generator.get_logical_conclusion(stock.name)
    report = insight_generator.generate_final_insight(stock.name, conclusion)

    return Insight(
        stock_name=stock.name,
        conclusion=conclusion,
        report=report
    )