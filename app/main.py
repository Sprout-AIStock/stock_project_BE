from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app import crud
from app.core import stock_info, insight_generator, news_fetcher
from app.database import SessionLocal, engine, Base
from app.services.scheduler import start_scheduler
from app.models.schemas import (
    NewsArticle, StockDetail, InsightResponse, TopKeyword, ChatbotQuery
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI 금융 정보 서비스")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/news/macro", response_model=List[NewsArticle])
def get_macro_news(db: Session = Depends(get_db)):
    return crud.get_articles_by_source(db=db, source="macro", limit=5)

@app.get("/api/news/popular", response_model=List[NewsArticle])
def get_popular_news(db: Session = Depends(get_db)):
    return crud.get_top_articles_by_click(db=db, limit=5)

@app.get("/api/themes", response_model=List[str])
def get_available_themes():
    themes = news_fetcher.get_investment_themes()
    if not themes:
        return ["반도체", "2차전지", "인공지능", "바이오/제약"]
    return themes

@app.get("/api/news/theme/{theme_name}", response_model=List[NewsArticle])
def get_news_by_theme(theme_name: str, db: Session = Depends(get_db)):
    MAIN_THEMES = ["반도체", "2차전지", "인공지능"]
    if theme_name in MAIN_THEMES:
        return crud.get_articles_by_source(db=db, source=theme_name, limit=5)
    else:
        articles = news_fetcher.get_articles_by_theme(theme_name=theme_name, limit=5)
        if articles is None:
            raise HTTPException(status_code=404, detail="해당 테마의 기사를 가져올 수 없습니다.")
        return articles

@app.post("/api/articles/{article_id}/click", status_code=204)
def record_article_click(article_id: int, db: Session = Depends(get_db)):
    article = crud.increment_article_click(db=db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return

@app.get("/api/keywords/top", response_model=List[TopKeyword])
def get_top_search_keywords(db: Session = Depends(get_db)):
    return crud.get_top_keywords(db=db, limit=10)

@app.get("/api/stock/search/{stock_code}", response_model=StockDetail)
def search_stock_details(stock_code: str, db: Session = Depends(get_db)):
    details = stock_info.get_stock_details_from_naver(stock_code)
    if not details:
        raise HTTPException(status_code=404, detail="종목 정보를 가져올 수 없습니다.")
    crud.insert_search_keyword(db=db, keyword=details.name)
    return details

@app.get("/api/insight/{stock_code}", response_model=InsightResponse)
def get_full_ai_pipeline(stock_code: str):
    stock = stock_info.get_stock_details_from_naver(stock_code)
    if not stock:
        raise HTTPException(status_code=404, detail="종목 정보를 찾을 수 없습니다.")
    
    clova_conclusion, clova_reason = insight_generator.get_clova_insight(stock.name)
    gpt_report_text = insight_generator.get_gpt_report(stock.name, clova_conclusion, clova_reason)
    report_id = insight_generator.save_report_to_file(gpt_report_text)
    
    return InsightResponse(quick_insight=clova_conclusion, report_id=report_id)

@app.post("/api/chatbot/query")
def handle_chatbot_query(query: ChatbotQuery):
    answer = insight_generator.query_document_chatbot(
        report_id=query.report_id,
        user_question=query.user_question
    )
    return {"answer": answer}