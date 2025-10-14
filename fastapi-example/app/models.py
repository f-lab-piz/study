"""
Pydantic 모델 및 SQLAlchemy ORM 모델 정의
- Pydantic: API의 요청/응답 데이터 검증
- SQLAlchemy: 데이터베이스 테이블 매핑
"""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base


# ==================== SQLAlchemy ORM 모델 ====================

class TodoDB(Base):
    """
    TODO 테이블 ORM 모델
    데이터베이스의 'todos' 테이블과 매핑됩니다.
    """
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ==================== Pydantic 스키마 ====================

class TodoBase(BaseModel):
    """TODO 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목")
    description: Optional[str] = Field(None, max_length=500, description="할 일 설명")
    completed: bool = Field(False, description="완료 여부")


class TodoCreate(TodoBase):
    """TODO 생성 요청 스키마"""
    pass


class TodoUpdate(BaseModel):
    """TODO 수정 요청 스키마 (모든 필드 선택적)"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None


class TodoResponse(TodoBase):
    """TODO 응답 스키마"""
    id: int = Field(..., description="TODO ID")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")

    # Pydantic v2 설정
    model_config = ConfigDict(
        from_attributes=True,  # ORM 모델에서 데이터 읽기 허용
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "FastAPI 공부하기",
                "description": "FastAPI 기초 개념 학습",
                "completed": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )
