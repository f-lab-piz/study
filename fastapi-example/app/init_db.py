"""
데이터베이스 초기화 스크립트
애플리케이션 시작 시 테이블을 자동으로 생성합니다.
"""
from .database import engine, Base
from .models import TodoDB  # 모든 모델 import 필요


def init_db():
    """
    데이터베이스 테이블 생성

    주의: 프로덕션 환경에서는 Alembic을 사용하세요!
    이 방법은 개발/학습 목적으로만 사용됩니다.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
