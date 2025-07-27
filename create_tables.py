# ./create_tables.py
from app.database import engine, Base
import app.db_models  # ✅ 테이블 정의를 실제로 메모리에 로딩
import os

# 모든 테이블 생성
Base.metadata.create_all(bind=engine)

# 실제 DB 경로 출력
db_url = str(engine.url)

# SQLite라면 파일 경로 추출
if db_url.startswith("sqlite:///"):
    db_path = db_url.replace("sqlite:///", "")
    abs_path = os.path.abspath(db_path)
    print(f"✅ 테이블 생성 완료 → DB 경로: {abs_path}")
else:
    print("✅ 테이블 생성 완료 (NOT SQLite)")
