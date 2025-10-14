"""
데이터베이스 연결 설정
SQLAlchemy를 사용한 PostgreSQL 연결 관리
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 환경 변수에서 데이터베이스 URL 가져오기
# 기본값: PostgreSQL (Docker Compose 사용 시)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/todoapp"
)

# SQLAlchemy 엔진 생성
# echo=True: SQL 쿼리 로깅 (개발 시 유용)
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # 연결 유효성 확인
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 베이스 클래스 생성 (모든 모델이 상속)
Base = declarative_base()


# 데이터베이스 세션 의존성
def get_db():
    """
    데이터베이스 세션 생성 및 관리

    FastAPI의 Depends()와 함께 사용:
    - 요청마다 새 세션 생성
    - 요청 완료 후 자동으로 세션 종료

    Yields:
        Session: SQLAlchemy 세션 객체
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
