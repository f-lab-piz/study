"""
pytest 설정 및 픽스처 정의

픽스처(Fixture)란?
- 테스트에서 반복적으로 사용하는 설정이나 데이터를 미리 준비해두는 것
- @pytest.fixture 데코레이터로 정의
- 테스트 함수의 파라미터로 주입받아 사용
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import TodoDB


# 테스트용 데이터베이스 URL (SQLite 사용)
# 실제 PostgreSQL을 사용하지 않고 메모리 DB로 빠르게 테스트
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def test_db():
    """
    테스트용 데이터베이스 세션 픽스처

    scope="function": 각 테스트 함수마다 새로운 DB 생성
    - 테스트 간 격리 보장
    - 각 테스트는 독립적으로 실행
    """
    # 테스트용 엔진 생성
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}  # SQLite용 설정
    )

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    # 세션 팩토리 생성
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 세션 생성
    db = TestingSessionLocal()

    try:
        yield db  # 테스트에 세션 제공
    finally:
        db.close()  # 테스트 후 세션 종료
        Base.metadata.drop_all(bind=engine)  # 테이블 삭제 (정리)


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI TestClient 픽스처

    TestClient: FastAPI 앱을 실제 서버 없이 테스트할 수 있게 해주는 도구
    - HTTP 요청을 시뮬레이션
    - 실제 서버를 띄우지 않아도 됨
    """
    # get_db 의존성을 test_db로 오버라이드
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # TestClient 생성
    with TestClient(app) as test_client:
        yield test_client

    # 의존성 오버라이드 정리
    app.dependency_overrides.clear()


@pytest.fixture
def sample_todo_data():
    """
    샘플 TODO 데이터 픽스처

    여러 테스트에서 동일한 샘플 데이터를 사용할 때 편리
    """
    return {
        "title": "테스트 할일",
        "description": "pytest로 테스트 작성하기",
        "completed": False
    }


@pytest.fixture
def sample_todo_in_db(test_db, sample_todo_data):
    """
    DB에 저장된 샘플 TODO 픽스처

    테스트 시작 전에 미리 DB에 TODO를 생성해두는 픽스처
    GET, PUT, DELETE 테스트에서 유용
    """
    todo = TodoDB(**sample_todo_data)
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    return todo


# 추가 픽스처 예시 (멘티가 필요에 따라 작성)

@pytest.fixture
def multiple_todos_in_db(test_db):
    """
    TODO: 여러 개의 TODO를 DB에 미리 생성하는 픽스처

    힌트: 리스트 페이지네이션 테스트에 유용
    예시:
    todos = []
    for i in range(5):
        todo = TodoDB(title=f"할일 {i}", completed=False)
        test_db.add(todo)
    test_db.commit()
    return todos
    """
    pass


@pytest.fixture
def completed_todos_in_db(test_db):
    """
    TODO: 완료된 TODO들만 미리 생성하는 픽스처

    힌트: 필터링 기능 테스트에 유용
    """
    pass
