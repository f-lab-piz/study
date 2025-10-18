"""
유닛 테스트 (Unit Tests)

유닛 테스트란?
- 개별 함수나 클래스의 동작을 독립적으로 테스트
- 외부 의존성(DB, API 등)을 최소화하거나 모킹(Mocking)
- 빠르고 단순한 테스트

이 파일에서는:
- Pydantic 모델 검증
- 개별 함수의 로직
- 간단한 데이터 변환
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models import TodoCreate, TodoUpdate, TodoResponse, TodoDB


class TestPydanticModels:
    """Pydantic 모델 검증 테스트"""

    def test_todo_create_valid(self):
        """
        유효한 데이터로 TodoCreate 생성 테스트

        테스트 패턴:
        1. Arrange (준비): 테스트 데이터 준비
        2. Act (실행): 테스트 대상 실행
        3. Assert (검증): 결과 검증
        """
        # Arrange
        data = {
            "title": "FastAPI 공부",
            "description": "테스트 작성법 배우기",
            "completed": False
        }

        # Act
        todo = TodoCreate(**data)

        # Assert
        assert todo.title == "FastAPI 공부"
        assert todo.description == "테스트 작성법 배우기"
        assert todo.completed is False

    def test_todo_create_title_required(self):
        """
        title 필드 필수 검증 테스트

        Pydantic이 필수 필드 누락 시 ValidationError를 발생시키는지 확인
        """
        # Arrange
        data = {
            "description": "제목 없음",
            "completed": False
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(**data)

        # 에러 메시지에 'title' 필드 관련 내용이 있는지 확인
        assert "title" in str(exc_info.value)

    def test_todo_create_title_too_long(self):
        """
        title 길이 제한 검증 테스트

        max_length=100 제약이 제대로 동작하는지 확인
        """
        # Arrange
        data = {
            "title": "a" * 101,  # 101자 (최대 100자 초과)
            "completed": False
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            TodoCreate(**data)

        assert "title" in str(exc_info.value)

    # TODO: 다음 테스트를 작성해보세요
    def test_todo_create_default_completed(self):
        """
        TODO: completed 기본값이 False인지 테스트

        힌트:
        - title만 제공하고 completed는 제공하지 않음
        - 생성된 객체의 completed가 False인지 확인
        """
        pass

    def test_todo_update_partial(self):
        """
        TODO: TodoUpdate는 모든 필드가 선택적(Optional)인지 테스트

        힌트:
        - 빈 딕셔너리 {}로도 TodoUpdate 생성 가능해야 함
        - 일부 필드만 제공해도 에러가 나지 않아야 함
        """
        pass


class TestSQLAlchemyModels:
    """SQLAlchemy ORM 모델 테스트"""

    def test_create_todo_in_db(self, test_db):
        """
        DB에 TODO 생성 테스트

        test_db 픽스처 사용:
        - conftest.py에 정의된 테스트용 DB 세션
        - 각 테스트마다 깨끗한 DB 제공
        """
        # Arrange
        todo_data = {
            "title": "DB 테스트",
            "description": "SQLAlchemy 모델 테스트",
            "completed": False
        }

        # Act
        todo = TodoDB(**todo_data)
        test_db.add(todo)
        test_db.commit()
        test_db.refresh(todo)

        # Assert
        assert todo.id is not None  # ID가 자동 생성되었는지
        assert todo.title == "DB 테스트"
        assert todo.created_at is not None  # 생성 시간이 자동 설정되었는지
        assert todo.updated_at is not None

    def test_todo_default_values(self, test_db):
        """
        TODO 기본값 테스트

        completed, created_at, updated_at 기본값이 올바르게 설정되는지 확인
        """
        # Arrange & Act
        todo = TodoDB(title="기본값 테스트")
        test_db.add(todo)
        test_db.commit()
        test_db.refresh(todo)

        # Assert
        assert todo.completed is False  # 기본값 False
        assert isinstance(todo.created_at, datetime)  # datetime 객체
        assert isinstance(todo.updated_at, datetime)

    def test_query_todo_by_id(self, test_db, sample_todo_in_db):
        """
        ID로 TODO 조회 테스트

        sample_todo_in_db 픽스처 사용:
        - 테스트 시작 전에 미리 TODO가 DB에 저장되어 있음
        """
        # Arrange
        todo_id = sample_todo_in_db.id

        # Act
        found_todo = test_db.query(TodoDB).filter(TodoDB.id == todo_id).first()

        # Assert
        assert found_todo is not None
        assert found_todo.id == todo_id
        assert found_todo.title == sample_todo_in_db.title

    # TODO: 다음 테스트를 작성해보세요
    def test_update_todo_in_db(self, test_db, sample_todo_in_db):
        """
        TODO: DB에서 TODO 수정 테스트

        힌트:
        1. sample_todo_in_db의 completed를 True로 변경
        2. test_db.commit()
        3. test_db.refresh()
        4. completed가 True로 변경되었는지 확인
        """
        pass

    def test_delete_todo_in_db(self, test_db, sample_todo_in_db):
        """
        TODO: DB에서 TODO 삭제 테스트

        힌트:
        1. test_db.delete(sample_todo_in_db)
        2. test_db.commit()
        3. 다시 조회했을 때 None인지 확인
        """
        pass

    def test_query_all_todos(self, test_db):
        """
        TODO: 모든 TODO 조회 테스트

        힌트:
        1. 여러 개의 TODO를 먼저 생성
        2. test_db.query(TodoDB).all()로 조회
        3. 생성한 개수와 조회된 개수가 같은지 확인
        """
        pass


class TestDependencies:
    """의존성 함수 테스트"""

    def test_get_todo_by_id_success(self, test_db, sample_todo_in_db):
        """
        get_todo_by_id 함수 성공 케이스 테스트

        의존성 함수를 직접 호출하여 테스트
        """
        from app.dependencies import get_todo_by_id

        # Arrange
        todo_id = sample_todo_in_db.id

        # Act
        # 의존성 함수에 직접 값 전달 (DI 없이)
        result = get_todo_by_id(todo_id, test_db)

        # Assert
        assert result.id == todo_id
        assert result.title == sample_todo_in_db.title

    def test_get_todo_by_id_not_found(self, test_db):
        """
        get_todo_by_id 함수 실패 케이스 테스트

        존재하지 않는 ID로 조회 시 HTTPException 발생하는지 확인
        """
        from fastapi import HTTPException
        from app.dependencies import get_todo_by_id

        # Arrange
        non_existent_id = 99999

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_todo_by_id(non_existent_id, test_db)

        # 404 에러인지 확인
        assert exc_info.value.status_code == 404

    # TODO: 다음 테스트를 작성해보세요
    def test_get_todo_by_id_error_message(self, test_db):
        """
        TODO: HTTPException의 에러 메시지 검증 테스트

        힌트:
        - exc_info.value.detail에 에러 메시지가 있음
        - 메시지에 TODO ID가 포함되어 있는지 확인
        """
        pass


# 파라미터화 테스트 예시
class TestParametrizedTests:
    """
    pytest.mark.parametrize를 사용한 테스트

    같은 로직을 여러 입력값으로 반복 테스트할 때 유용
    """

    @pytest.mark.parametrize("title,expected_valid", [
        ("정상 제목", True),
        ("a" * 100, True),  # 최대 길이
        ("", False),  # 빈 문자열
        ("a" * 101, False),  # 길이 초과
    ])
    def test_todo_title_validation(self, title, expected_valid):
        """
        다양한 title 값으로 검증 테스트

        @pytest.mark.parametrize:
        - 하나의 테스트 함수로 여러 케이스 테스트
        - 각 파라미터 조합마다 개별 테스트로 실행됨
        """
        if expected_valid:
            # 유효한 경우: 에러 없이 생성되어야 함
            todo = TodoCreate(title=title, completed=False)
            assert todo.title == title
        else:
            # 유효하지 않은 경우: ValidationError 발생해야 함
            with pytest.raises(ValidationError):
                TodoCreate(title=title, completed=False)

    # TODO: 다음 파라미터화 테스트를 작성해보세요
    @pytest.mark.parametrize("description,expected_valid", [
        # TODO: description 필드의 다양한 케이스 추가
        # 힌트: None, 빈 문자열, 정상 문자열, max_length 초과 등
    ])
    def test_todo_description_validation(self, description, expected_valid):
        """
        TODO: description 필드 검증 파라미터화 테스트
        """
        pass
