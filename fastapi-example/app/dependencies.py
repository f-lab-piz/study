"""
의존성 주입(DI) 함수들
재사용 가능한 로직을 정의합니다.
"""
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import TodoDB


def get_todo_by_id(todo_id: int, db: Session = Depends(get_db)) -> TodoDB:
    """
    ID로 TODO를 조회하는 함수

    Args:
        todo_id: TODO ID
        db: 데이터베이스 세션

    Returns:
        TodoDB: TODO ORM 객체

    Raises:
        HTTPException: TODO를 찾을 수 없을 때
    """
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {todo_id}인 TODO를 찾을 수 없습니다."
        )
    return todo
