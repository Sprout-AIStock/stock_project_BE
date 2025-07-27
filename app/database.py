# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 데이터베이스 접속 주소 설정 (SQLite 사용)
# 프로젝트 루트 폴더에 sql_app.db 라는 파일로 DB가 생성됩니다.
SQLALCHEMY_DATABASE_URL = "sqlite:///../sql_app.db"

# 2. 데이터베이스 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. 데이터베이스와 통신하는 세션(Session) 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. DB 모델의 기본이 될 Base 클래스 생성
Base = declarative_base()