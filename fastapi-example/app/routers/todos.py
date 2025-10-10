"""
TODO API 라우터
TODO 관련 엔드포인트를 정의합니다.
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, status
from app.models import TodoCreate, TodoUpdate, TodoResponse
from app.dependencies import (
    get_todo_storage,
    get_todo_by_id,
    get_next_id
)

# APIRouter 생성 (라우트 그룹화)
router = APIRouter(
    prefix="/todos",
    tags=["todos"],  # Swagger 문서에서 그룹으로 표시
)


@router.get("/", response_model=List[TodoResponse])
def list_todos(db: Dict[int, dict] = Depends(get_todo_storage)):
    """
    모든 TODO 목록 조회

    - **db**: TODO 저장소 (DI로 주입)
    """
    return list(db.values())


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """
    특정 TODO 조회

    - **todo_id**: 조회할 TODO의 ID
    - **db**: TODO 저장소 (DI로 주입)
    """
    return get_todo_by_id(todo_id, db)


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED
)
def create_todo(
    todo: TodoCreate,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """
    새 TODO 생성

    - **todo**: 생성할 TODO 데이터 (Pydantic이 자동 검증)
    - **db**: TODO 저장소 (DI로 주입)
    """
    new_id = get_next_id()
    new_todo = {
        "id": new_id,
        **todo.model_dump()
    }
    db[new_id] = new_todo
    return new_todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """
    TODO 수정

    - **todo_id**: 수정할 TODO의 ID
    - **todo_update**: 수정할 데이터 (일부만 가능)
    - **db**: TODO 저장소 (DI로 주입)
    """
    existing_todo = get_todo_by_id(todo_id, db)

    # 업데이트 데이터 적용 (None이 아닌 값만)
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        existing_todo[key] = value

    return existing_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """
    TODO 삭제

    - **todo_id**: 삭제할 TODO의 ID
    - **db**: TODO 저장소 (DI로 주입)
    """
    get_todo_by_id(todo_id, db)  # 존재 여부 확인
    del db[todo_id]
    return None
