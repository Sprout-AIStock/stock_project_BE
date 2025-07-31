import requests
from typing import List, Optional

from app.models import schemas
from app.config import settings

DEEPSEARCH_API_BASE_URL = "https://api-v2.deepsearch.com"

def get_trending_macro_topics(limit: int = 10) -> Optional[List[schemas.NewsArticle]]:
    api_url = f"{DEEPSEARCH_API_BASE_URL}/v1/global-articles/topics/trending"
    params = {"api_key": settings.DEEPSEARCH_API_KEY, "page_size": limit, "order": "rank"}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = []
        for topic in data.get("data", []):
            article_data = {
                "id": 0, # 임시값, DB에 저장되며 실제 id 할당됨
                "title": topic.get("title_ko", topic.get("title")),
                "url": f"https://www.deepsearch.com/contents/news/topics/{topic.get('id')}",
                "published_at": topic.get("date", ""),
                "click_count": 0, # 임시값
            }
            articles.append(schemas.NewsArticle.model_validate(article_data))
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Request failed for macro topics: {e}")
        return None

# app/core/news_fetcher.py 파일에서 get_investment_themes 함수를 아래와 같이 수정

def get_investment_themes() -> Optional[List[str]]:
    """
    DeepSearch API에서 제공하는 '투자 테마 태그' 목록을 가져옵니다.
    (현재 API 키 권한 문제로 임시 비활성화)
    """
    print("NOTE: get_investment_themes API call is temporarily disabled due to plan restrictions.")
    return None # 👈 API 호출 대신 None을 반환하도록 수정

def get_articles_by_theme(theme_name: str, limit: int = 10) -> Optional[List[schemas.NewsArticle]]:
    api_url = f"{DEEPSEARCH_API_BASE_URL}/v1/articles"
    params = {"api_key": settings.DEEPSEARCH_API_KEY, "keyword": theme_name, "page_size": limit, "order": "published_at"}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = []
        for item in data.get("data", []):
            article_data = {
                "id": 0,
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "published_at": item.get("published_at", ""),
                "click_count": 0,
            }
            articles.append(schemas.NewsArticle.model_validate(article_data))
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Request failed for theme articles: {e}")
        return None