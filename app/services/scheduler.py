# app/services/scheduler.py (수정)
from app.core import news_fetcher
from app.database import SessionLocal
from app import crud

def update_macro_news_job():
    """거시 경제 뉴스를 DB에 업데이트하는 스케줄링 작업."""
    print("스케줄러 실행: 거시 경제 뉴스 DB 저장을 시작합니다.")
    
    # DB 세션을 스케줄러 내에서 직접 생성하고 닫아줍니다.
    db = SessionLocal()
    try:
        latest_news = news_fetcher.get_trending_macro_topics(limit=10) # 좀 더 넉넉하게 가져오기
        
        if latest_news:
            count = crud.create_news_articles(db=db, articles=latest_news, source="macro")
            print(f"성공: {count}개의 새로운 거시 경제 뉴스를 DB에 저장했습니다.")
        else:
            print("가져온 뉴스가 없습니다.")
    finally:
        db.close() # 작업이 끝나면 반드시 세션을 닫아줍니다.

# start_scheduler 함수는 이전과 동일합니다.
from apscheduler.schedulers.background import BackgroundScheduler
def start_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(update_macro_news_job, 'interval', seconds=600)
    scheduler.add_job(update_macro_news_job)
    scheduler.start()