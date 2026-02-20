"""
pytest 픽스처 설정

핵심 전략:
- SQLite 인메모리 DB로 PostgreSQL 대체 (테스트 속도 + 격리)
- app.dependency_overrides로 get_db를 테스트용 세션으로 교체
- 각 테스트 함수마다 새로운 DB 생성 (완벽한 격리)
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User

# SQLite 인메모리 DB (파일 생성 없이 메모리에서만 동작)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """
    각 테스트 함수마다 새로운 인메모리 DB 생성

    scope="function":
    - 테스트 함수마다 새 DB → 완벽한 격리
    - 느리지만 안전 (테스트 간 데이터 오염 없음)

    흐름:
    1. 엔진 생성 (SQLite 인메모리)
    2. 테이블 생성 (create_all)
    3. 세션 생성 → yield (테스트에서 사용)
    4. 세션 닫기 + 테이블 삭제 (정리)
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI TestClient (HTTP 요청 시뮬레이션)

    핵심: app.dependency_overrides로 get_db를 교체
    → 모든 API 엔드포인트가 테스트용 SQLite DB를 사용
    """

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ===========================================
# 데이터 픽스처
# ===========================================


@pytest.fixture
def sample_user_data():
    """테스트용 유저 데이터 (dict)"""
    return {"name": "김철수", "email": "kim@example.com"}


@pytest.fixture
def second_user_data():
    """두 번째 테스트용 유저 데이터"""
    return {"name": "이영희", "email": "lee@example.com"}


@pytest.fixture
def sample_user_in_db(test_db, sample_user_data):
    """
    DB에 미리 생성된 유저 (ORM 객체 반환)

    통합 테스트에서 "이미 데이터가 있는 상태"를 테스트할 때 사용
    """
    user = User(name=sample_user_data["name"], email=sample_user_data["email"])
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def multiple_users_in_db(test_db):
    """
    TODO: 여러 유저를 미리 DB에 생성하는 픽스처

    힌트:
    1. 5~10명의 유저 데이터를 리스트로 만들기
    2. for 루프로 User 객체 생성 후 test_db.add()
    3. test_db.commit()
    4. 생성된 유저 리스트 반환

    예시:
        users_data = [
            {"name": "유저1", "email": "user1@test.com"},
            {"name": "유저2", "email": "user2@test.com"},
            ...
        ]
    """
    pass
