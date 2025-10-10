"""
의존성 주입(DI) 함수들
재사용 가능한 로직을 정의합니다.
"""
from typing import Dict, List
from fastapi import HTTPException, status


# 메모리 DB (실제로는 PostgreSQL, MongoDB 등 사용)
fake_db: Dict[int, dict] = {}
next_id: int = 1


def get_todo_storage() -> Dict[int, dict]:
    """
    TODO 저장소를 반환하는 의존성

    실제 프로젝트에서는:
    - DB 세션 객체 반환
    - Redis 클라이언트 반환
    등으로 대체됩니다.
    """
    return fake_db


def get_todo_by_id(todo_id: int, db: Dict[int, dict]) -> dict:
    """
    ID로 TODO를 조회하는 함수

    Args:
        todo_id: TODO ID
        db: TODO 저장소

    Returns:
        dict: TODO 데이터

    Raises:
        HTTPException: TODO를 찾을 수 없을 때
    """
    todo = db.get(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {todo_id}인 TODO를 찾을 수 없습니다."
        )
    return todo


def get_next_id() -> int:
    """
    다음 ID를 반환하는 함수
    (실제로는 DB의 auto-increment 사용)
    """
    global next_id
    current_id = next_id
    next_id += 1
    return current_id
