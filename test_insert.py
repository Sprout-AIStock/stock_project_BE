from app.database import SessionLocal
from app.crud import insert_search_keyword, get_top_keywords

# DB 세션 생성
db = SessionLocal()

# ✅ Step 1: 검색 키워드 삽입
insert_search_keyword(db, "삼성전자")
insert_search_keyword(db, "카카오")
insert_search_keyword(db, "삼성전자")

# ✅ Step 2: 인기 키워드 TOP N 출력
print("🔥 인기 검색어 TOP 10:")
for i, (keyword, count) in enumerate(get_top_keywords(db), 1):
    print(f"{i}. {keyword} - {count}회 검색")

# DB 세션 종료
db.close()
