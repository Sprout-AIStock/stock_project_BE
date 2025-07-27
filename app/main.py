# app/main.py (기존 코드에 엔드포인트 추가)

# ... (기존 import 및 app 설정)
from http.client import HTTPException
from app.core import news_fetcher # news_fetcher 추가

# ... (기존 엔드포인트들)

@app.get("/api/themes", response_model=List[str])
def get_available_themes():
    """
    DeepSearch에서 제공하는 투자 테마 목록 전체를 반환합니다.
    """
    themes = news_fetcher.get_investment_themes()
    if themes is None:
        # API 호출 실패 시, 미리 정의해 둔 기본 테마 목록을 대신 반환
        return ["반도체", "2차전지", "인공지능", "바이오/제약"]
    return themes


@app.get("/api/news/theme/{theme_name}", response_model=List[NewsArticleSchema])
def get_news_by_theme(theme_name: str, db: Session = Depends(get_db)):
    """
    특정 테마에 대한 최신 기사를 반환합니다.
    메인 테마의 경우 DB에서, 그 외 테마는 API로 실시간 조회합니다.
    """
    # 메인 테마 목록 (스케줄러와 동일하게 유지)
    MAIN_THEMES = ["반도체", "2차전지", "인공지능"]

    if theme_name in MAIN_THEMES:
        # 메인 테마는 DB에 캐시된 데이터를 우선적으로 반환
        print(f"DB에서 '{theme_name}' 테마 기사를 조회합니다.")
        articles = crud.get_articles_by_source(db=db, source=theme_name, limit=5)
        return articles
    else:
        # 그 외 테마는 실시간으로 API를 호출하여 반환
        print(f"API로 '{theme_name}' 테마 기사를 실시간 조회합니다.")
        articles = news_fetcher.get_articles_by_theme(theme_name=theme_name, limit=5)
        if articles is None:
            raise HTTPException(status_code=404, detail="해당 테마의 기사를 가져올 수 없습니다.")
        return articles