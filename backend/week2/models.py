"""
SQLAlchemy 모델 정의
- DB 테이블 구조를 Python 클래스로 표현
- ORM을 통해 객체로 DB를 다룸
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """
    users 테이블
    - id: 기본 키 (자동 증가)
    - name: 유저 이름 (필수)
    - email: 이메일 (필수, 중복 불가)
    - created_at: 생성 시각 (자동 설정)
    - updated_at: 수정 시각 (자동 업데이트)
    """

    __tablename__ = "users"

    # 기본 키 (자동 증가)
    id = Column(Integer, primary_key=True, index=True)

    # 유저 이름 (최대 100자, NULL 불가)
    name = Column(String(100), nullable=False)

    # 이메일 (최대 255자, NULL 불가, 중복 불가, 인덱스)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # 생성 시각 (DB 기본값: 현재 시각)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 수정 시각 (업데이트 시 자동 갱신)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        """객체를 문자열로 표현 (디버깅용)"""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
