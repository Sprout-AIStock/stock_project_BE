from apscheduler.schedulers.background import BackgroundScheduler
from app.core import news_fetcher
from app.core import economic_indicator_fetcher # 👈 1. 경제 지표 fetcher import
from app.database import SessionLocal
from app import crud

# --- 캐시 영역 ---
# 2. 최신 경제 지표를 저장할 전역 변수(캐시) 생성
indicator_cache = {}

# --- 스케줄러 작업 정의 ---
MAIN_THEMES = ["반도체", "2차전지", "인공지능"]

def update_macro_news_job():
    """거시 경제 뉴스를 DB에 업데이트하는 스케줄링 작업 (10분마다)."""
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
    """주요 테마 뉴스를 DB에 업데이트하는 스케줄링 작업 (10분마다)."""
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

# 👇 3. 매일 경제 지표를 업데이트하는 새로운 작업 함수 추가
def update_economic_indicators_job():
    """매일 한 번 최신 경제 지표를 FRED와 DeepSearch에서 가져와 캐시에 저장합니다."""
    print("스케줄러 실행: 일일 경제 지표 업데이트를 시작합니다.")
    us_indicators = economic_indicator_fetcher.get_us_economic_indicators()
    trade_news = news_fetcher.get_latest_trade_policy_news()

    if us_indicators:
        indicator_cache.update(us_indicators)
        indicator_cache['latest_trade_policy'] = trade_news
        print(f"성공: 경제 지표 업데이트 완료. 데이터: {indicator_cache}")
    else:
        print("실패: 경제 지표 업데이트 실패.")

# --- 스케줄러 시작 함수 ---
def start_scheduler():
    """스케줄러를 시작하고 모든 작업을 등록합니다."""
    scheduler = BackgroundScheduler(daemon=True)
    
    # 작업 1: 거시경제 뉴스 업데이트 (10분 주기)
    scheduler.add_job(update_macro_news_job, 'interval', seconds=600, id="macro_job")
    
    # 작업 2: 테마별 뉴스 업데이트 (10분 주기, 10초 딜레이)
    scheduler.add_job(update_themed_news_job, 'interval', seconds=610, id="theme_job")
    
    # 👇 4. 작업 3: 경제 지표 업데이트 (매일 아침 8시)
    scheduler.add_job(update_economic_indicators_job, 'cron', hour=8, id="indicator_job")
    
    # 앱 시작 시 모든 작업 즉시 1회 실행
    scheduler.add_job(update_economic_indicators_job)
    scheduler.add_job(update_macro_news_job)
    scheduler.add_job(update_themed_news_job)
    
    scheduler.start()