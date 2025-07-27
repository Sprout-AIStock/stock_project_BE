# app/services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.core import news_fetcher
from app.database import SessionLocal
from app import crud

# 스케줄러가 실행할 작업들을 먼저 정의합니다.
MAIN_THEMES = ["반도체", "2차전지", "인공지능"]

def update_macro_news_job():
    """거시 경제 뉴스를 DB에 업데이트하는 스케줄링 작업."""
    print("스케줄러 실행: 거시 경제 뉴스 DB 저장을 시작합니다.")
    db = SessionLocal()
    try:
        latest_news = news_fetcher.get_trending_macro_topics(limit=10)
        if latest_news:
            count = crud.create_news_articles(db=db, articles=latest_news, source="macro")
            print(f"성공: {count}개의 새로운 거시 경제 뉴스를 DB에 저장했습니다.")
        else:
            print("가져온 뉴스가 없습니다.")
    finally:
        db.close()

def update_themed_news_job():
    """주요 테마 뉴스를 DB에 업데이트하는 스케줄링 작업."""
    print("스케줄러 실행: 테마별 뉴스 DB 저장을 시작합니다.")
    db = SessionLocal()
    try:
        for theme in MAIN_THEMES:
            latest_news = news_fetcher.get_articles_by_theme(theme_name=theme, limit=10)
            if latest_news:
                count = crud.create_news_articles(db=db, articles=latest_news, source=theme)
                print(f"성공: 테마 '{theme}'의 새로운 뉴스 {count}개를 DB에 저장했습니다.")
    finally:
        db.close()

# 작업을 모두 정의한 후에 스케줄러를 시작하는 함수를 정의합니다.
def start_scheduler():
    """스케줄러를 시작하고 작업을 등록합니다."""
    scheduler = BackgroundScheduler(daemon=True)
    
    # 거시경제 뉴스 업데이트 작업
    scheduler.add_job(update_macro_news_job, 'interval', seconds=600, id="macro_job")
    scheduler.add_job(update_macro_news_job)
    
    # 테마별 뉴스 업데이트 작업 (API 동시 호출을 피하기 위해 약간의 시간차를 둡니다)
    scheduler.add_job(update_themed_news_job, 'interval', seconds=610, id="theme_job")
    scheduler.add_job(update_themed_news_job)
    
    scheduler.start()