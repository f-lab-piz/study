"""
유닛 테스트 - Pydantic 스키마 + SQLAlchemy ORM 직접 테스트

유닛 테스트란?
- HTTP 요청 없이 개별 구성 요소를 독립적으로 테스트
- Pydantic 모델의 유효성 검증 로직
- SQLAlchemy ORM의 DB 작업 로직
- 가장 빠르고 가장 많이 작성해야 하는 테스트

AAA 패턴:
- Arrange (준비): 테스트 데이터 준비
- Act (실행): 테스트 대상 코드 실행
- Assert (검증): 결과가 기대와 일치하는지 확인
"""

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.main import UserCreate, UserUpdate, UserResponse
from app.models import User


# ===========================================
# 1. Pydantic 스키마 테스트
# ===========================================


class TestPydanticSchemas:
    """Pydantic 모델의 유효성 검증 테스트"""

    def test_user_create_valid(self):
        """정상적인 유저 생성 데이터"""
        # Arrange
        data = {"name": "김철수", "email": "kim@example.com"}

        # Act
        user = UserCreate(**data)

        # Assert
        assert user.name == "김철수"
        assert user.email == "kim@example.com"

    def test_user_create_name_required(self):
        """name 필드 누락 시 ValidationError 발생"""
        # Arrange
        data = {"email": "kim@example.com"}

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)

        # 에러 메시지에 'name' 필드가 포함되어 있는지 확인
        assert "name" in str(exc_info.value)

    def test_user_create_email_required(self):
        """email 필드 누락 시 ValidationError 발생"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(name="김철수")

        assert "email" in str(exc_info.value)

    def test_user_response_from_orm(self, test_db):
        """ORM 객체 → UserResponse 자동 변환 (from_attributes=True)"""
        # Arrange: DB에 유저 생성
        db_user = User(name="김철수", email="kim@example.com")
        test_db.add(db_user)
        test_db.commit()
        test_db.refresh(db_user)

        # Act: ORM 객체를 Pydantic 모델로 변환
        response = UserResponse.model_validate(db_user)

        # Assert
        assert response.id == db_user.id
        assert response.name == "김철수"
        assert response.email == "kim@example.com"

    def test_user_update_all_optional(self):
        """
        TODO: UserUpdate는 모든 필드가 선택적

        힌트:
        1. UserUpdate()를 빈 인자로 생성
        2. name과 email이 모두 None인지 확인
        """
        pass

    def test_user_update_partial_name(self):
        """
        TODO: name만 제공해도 유효

        힌트:
        1. UserUpdate(name="새이름")으로 생성
        2. name은 "새이름", email은 None인지 확인
        """
        pass


# ===========================================
# 2. SQLAlchemy ORM 테스트
# ===========================================


class TestSQLAlchemyORM:
    """SQLAlchemy 모델의 DB 동작 테스트"""

    def test_create_user_in_db(self, test_db):
        """유저 생성 후 ID가 자동 할당되는지 확인"""
        # Arrange
        user = User(name="김철수", email="kim@example.com")

        # Act
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Assert
        assert user.id is not None
        assert user.id > 0
        assert user.name == "김철수"
        assert user.email == "kim@example.com"

    def test_user_created_at_auto_set(self, test_db):
        """created_at이 자동으로 설정되는지 확인"""
        user = User(name="김철수", email="kim@example.com")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.created_at is not None

    def test_query_user_by_id(self, test_db, sample_user_in_db):
        """ID로 유저 조회"""
        # Act: sample_user_in_db 픽스처가 이미 DB에 유저를 생성함
        found = test_db.query(User).filter(User.id == sample_user_in_db.id).first()

        # Assert
        assert found is not None
        assert found.name == sample_user_in_db.name
        assert found.email == sample_user_in_db.email

    def test_email_uniqueness_constraint(self, test_db):
        """같은 이메일로 두 번 생성 시 IntegrityError 발생"""
        # Arrange
        user1 = User(name="김철수", email="same@example.com")
        test_db.add(user1)
        test_db.commit()

        # Act & Assert
        user2 = User(name="이영희", email="same@example.com")
        test_db.add(user2)

        with pytest.raises(IntegrityError):
            test_db.commit()

        # 롤백 (IntegrityError 이후 세션 정리)
        test_db.rollback()

    def test_update_user_name(self, test_db, sample_user_in_db):
        """
        TODO: 유저 이름 수정

        힌트:
        1. sample_user_in_db.name을 "새이름"으로 변경
        2. test_db.commit() 후 test_db.refresh()
        3. 이름이 "새이름"으로 변경되었는지 확인
        """
        pass

    def test_delete_user_from_db(self, test_db, sample_user_in_db):
        """
        TODO: 유저 삭제 후 조회 시 None 반환

        힌트:
        1. test_db.delete(sample_user_in_db) 실행
        2. test_db.commit()
        3. 같은 ID로 query → .first() 결과가 None인지 확인
        """
        pass

    def test_query_all_users(self, test_db):
        """
        TODO: 여러 유저 생성 후 전체 조회

        힌트:
        1. 3명의 유저 생성 (이메일 다르게!)
        2. test_db.add_all([user1, user2, user3])
        3. test_db.commit()
        4. test_db.query(User).all()의 길이가 3인지 확인
        """
        pass


# ===========================================
# 3. 파라미터화 테스트
# ===========================================


class TestParametrize:
    """@pytest.mark.parametrize로 여러 케이스를 한 번에 테스트"""

    @pytest.mark.parametrize(
        "name, email, should_succeed",
        [
            ("김철수", "kim@example.com", True),       # 정상
            ("a" * 100, "max@example.com", True),      # 이름 100자 (최대)
            ("A", "short@example.com", True),           # 이름 1자 (최소)
            ("홍길동 Jr.", "hong.jr@example.com", True), # 특수문자 포함
        ],
    )
    def test_user_create_various_data(self, name, email, should_succeed):
        """다양한 입력값으로 UserCreate 테스트"""
        if should_succeed:
            user = UserCreate(name=name, email=email)
            assert user.name == name
            assert user.email == email

    @pytest.mark.parametrize(
        "name, email",
        [
            ("유저1", "user1@test.com"),
            ("유저2", "user2@test.com"),
            ("유저3", "user3@test.com"),
        ],
    )
    def test_create_multiple_users_in_db(self, test_db, name, email):
        """
        TODO: 파라미터화로 여러 유저 DB 생성 테스트

        힌트:
        1. User(name=name, email=email)로 유저 생성
        2. test_db에 추가, 커밋, 리프레시
        3. id가 None이 아닌지 확인
        4. 이름과 이메일이 입력값과 같은지 확인
        """
        pass
