"""
Pydantic 모델 정의
API의 요청/응답 데이터 구조를 정의합니다.
"""
from pydantic import BaseModel, Field
from typing import Optional


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

    class Config:
        # 예시 데이터 (API 문서에 표시됨)
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "FastAPI 공부하기",
                "description": "FastAPI 기초 개념 학습",
                "completed": False
            }
        }
