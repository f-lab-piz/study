"""
데이터베이스 연결 설정
- SQLAlchemy 엔진 생성
- 세션 관리
- Base 클래스 정의

Week2에서 가져온 코드를 테스트 환경에 맞게 수정:
- load_dotenv() 제거 (테스트에서는 SQLite 사용)
- SQLite 호환 connect_args 조건부 처리
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 데이터베이스 URL (환경 변수 또는 기본값)
# 테스트 시에는 conftest.py에서 SQLite로 오버라이드됨
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app.db",
)

# SQLite는 check_same_thread=False 필요 (FastAPI가 멀티스레드로 동작하므로)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# 엔진 생성 (DB와의 연결 풀 관리)
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

# 세션 팩토리 (DB 작업 단위)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 베이스 클래스 (모든 모델이 상속받음)
Base = declarative_base()


def get_db():
    """
    FastAPI 의존성 주입용 함수
    요청마다 DB 세션을 생성하고, 요청 종료 시 자동으로 닫음
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
