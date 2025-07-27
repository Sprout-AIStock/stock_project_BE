# region [FastAPI Application] 
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse  # 👈 1. FileResponse import 추가
from sqlalchemy.orm import Session
from typing import List

from app import crud, models
from app.core import stock_info, insight_generator, news_fetcher
from app.database import SessionLocal, engine, Base
from app.services.scheduler import start_scheduler
from app.models.schemas import (
    NewsArticle, StockDetail, Insight, TopKeyword
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

# 👇 2. 루트 경로('/') 요청 시 index.html 파일을 반환하도록 수정
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

@app.get("/api/insight/{stock_code}", response_model=Insight)
def get_ai_insight(stock_code: str, db: Session = Depends(get_db)):
    stock = stock_info.get_stock_details_from_naver(stock_code)
    if not stock:
        raise HTTPException(status_code=404, detail="종목을 찾을 수 없습니다.")
    conclusion = insight_generator.get_logical_conclusion(stock.name)
    report = insight_generator.generate_final_insight(stock.name, conclusion)
    return Insight(stock_name=stock.name, conclusion=conclusion, report=report)
#endregion

# region [Flask Application]
# from flask import Flask, jsonify, request, send_file, abort
# from sqlalchemy.orm import scoped_session
# from app import crud, models
# from app.core import stock_info, insight_generator, news_fetcher
# from app.database import SessionLocal, engine, Base
# from app.services.scheduler import start_scheduler

# app = Flask(__name__)

# # DB 초기화
# Base.metadata.create_all(bind=engine)

# # DB 세션 관리
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # 스케줄러 시작
# @app.before_first_request
# def startup_event():
#     start_scheduler()

# # 루트 경로 (index.html 반환)
# @app.route("/", methods=["GET"])
# def read_root():
#     return send_file("static/index.html")

# # macro 뉴스
# @app.route("/api/news/macro", methods=["GET"])
# def get_macro_news():
#     db = next(get_db())
#     articles = crud.get_articles_by_source(db=db, source="macro", limit=5)
#     return jsonify([a.to_dict() for a in articles])

# # 인기 뉴스
# @app.route("/api/news/popular", methods=["GET"])
# def get_popular_news():
#     db = next(get_db())
#     articles = crud.get_top_articles_by_click(db=db, limit=5)
#     return jsonify([a.to_dict() for a in articles])

# # 투자 테마 목록
# @app.route("/api/themes", methods=["GET"])
# def get_available_themes():
#     themes = news_fetcher.get_investment_themes()
#     if not themes:
#         themes = ["반도체", "2차전지", "인공지능", "바이오/제약"]
#     return jsonify(themes)

# # 테마별 뉴스
# @app.route("/api/news/theme/<string:theme_name>", methods=["GET"])
# def get_news_by_theme(theme_name):
#     db = next(get_db())
#     MAIN_THEMES = ["반도체", "2차전지", "인공지능"]
#     if theme_name in MAIN_THEMES:
#         articles = crud.get_articles_by_source(db=db, source=theme_name, limit=5)
#         return jsonify([a.to_dict() for a in articles])
#     else:
#         articles = news_fetcher.get_articles_by_theme(theme_name=theme_name, limit=5)
#         if articles is None:
#             abort(404, "해당 테마의 기사를 가져올 수 없습니다.")
#         return jsonify([a.to_dict() for a in articles])

# # 클릭 수 증가
# @app.route("/api/articles/<int:article_id>/click", methods=["POST"])
# def record_article_click(article_id):
#     db = next(get_db())
#     article = crud.increment_article_click(db=db, article_id=article_id)
#     if not article:
#         abort(404, "Article not found")
#     return ('', 204)

# # 인기 키워드 조회
# @app.route("/api/keywords/top", methods=["GET"])
# def get_top_search_keywords():
#     db = next(get_db())
#     keywords = crud.get_top_keywords(db=db, limit=10)
#     return jsonify([k.to_dict() for k in keywords])

# # 종목 상세 검색
# @app.route("/api/stock/search/<string:stock_code>", methods=["GET"])
# def search_stock_details(stock_code):
#     db = next(get_db())
#     details = stock_info.get_stock_details_from_naver(stock_code)
#     if not details:
#         abort(404, "종목 정보를 가져올 수 없습니다.")
#     crud.insert_search_keyword(db=db, keyword=details.name)
#     return jsonify(details.dict())

# # AI 인사이트 제공
# @app.route("/api/insight/<string:stock_code>", methods=["GET"])
# def get_ai_insight(stock_code):
#     stock = stock_info.get_stock_details_from_naver(stock_code)
#     if not stock:
#         abort(404, "종목을 찾을 수 없습니다.")
#     conclusion = insight_generator.get_logical_conclusion(stock.name)
#     report = insight_generator.generate_final_insight(stock.name, conclusion)
#     return jsonify({
#         "stock_name": stock.name,
#         "conclusion": conclusion,
#         "report": report
#     })
# endregion