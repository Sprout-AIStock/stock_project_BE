# app/core/news_fetcher.py (기존 코드 아래에 추가)
import json
import requests
from typing import List, Optional

from app.models.schemas import NewsArticle
from app.config import settings
DEEPSEARCH_API_BASE_URL = "https://api-v2.deepsearch.com"

def get_investment_themes() -> Optional[List[str]]:
    """
    DeepSearch API에서 제공하는 '투자 테마 태그' 목록을 가져옵니다.
    """
    api_url = f"{DEEPSEARCH_API_BASE_URL}/v2/markets/invest_tags"
    params = {
        "api_key": settings.DEEPSEARCH_API_KEY,
        "country_code": "kr" # 한국 시장 테마
    }
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            # API 응답 형식에 맞게 실제 테마 이름 필드를 확인해야 합니다.
            # 예시: theme['name'] 또는 theme['tag'] 등
            # 여기서는 응답이 {'data': [{'tag_name': '반도체'}, ...]} 형태라고 가정합니다.
            themes = [item['tag_name'] for item in data.get('data', [])]
            return themes
        else:
            print(f"Error fetching themes: {response.status_code} {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed for themes: {e}")
        return None


def get_articles_by_theme(theme_name: str, limit: int = 10) -> Optional[List[NewsArticle]]:
    """
    특정 테마에 대한 최신 뉴스를 검색합니다.
    """
    api_url = f"{DEEPSEARCH_API_BASE_URL}/v1/articles"
    params = {
        "api_key": settings.DEEPSEARCH_API_KEY,
        "keyword": theme_name,
        "page_size": limit,
        "order": "published_at" # 최신순 정렬
    }
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = []
            for item in data.get("data", []):
                # 뉴스 기사 응답 구조에 맞춰 필드명을 사용해야 합니다.
                article = NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    published_at=item.get("published_at", "")
                )
                articles.append(article)
            return articles
        else:
            print(f"Error fetching articles for theme '{theme_name}': {response.status_code} {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed for theme articles: {e}")
        return None