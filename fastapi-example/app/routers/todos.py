"""
TODO API 라우터
TODO 관련 엔드포인트를 정의합니다.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TodoCreate, TodoUpdate, TodoResponse, TodoDB
from app.dependencies import get_todo_by_id

# APIRouter 생성 (라우트 그룹화)
router = APIRouter(
    prefix="/todos",
    tags=["todos"],  # Swagger 문서에서 그룹으로 표시
)


@router.get("/", response_model=List[TodoResponse])
def list_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    모든 TODO 목록 조회

    - **skip**: 건너뛸 레코드 수 (페이지네이션)
    - **limit**: 가져올 최대 레코드 수
    - **db**: 데이터베이스 세션 (DI로 주입)
    """
    todos = db.query(TodoDB).offset(skip).limit(limit).all()
    return todos


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    특정 TODO 조회

    - **todo_id**: 조회할 TODO의 ID
    - **db**: 데이터베이스 세션 (DI로 주입)
    """
    return get_todo_by_id(todo_id, db)


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED
)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """
    새 TODO 생성

    - **todo**: 생성할 TODO 데이터 (Pydantic이 자동 검증)
    - **db**: 데이터베이스 세션 (DI로 주입)
    """
    # Pydantic 모델을 SQLAlchemy 모델로 변환
    db_todo = TodoDB(**todo.model_dump())

    # DB에 추가 및 커밋
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)  # DB에서 생성된 값 (id, created_at 등) 가져오기

    return db_todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db)
):
    """
    TODO 수정

    - **todo_id**: 수정할 TODO의 ID
    - **todo_update**: 수정할 데이터 (일부만 가능)
    - **db**: 데이터베이스 세션 (DI로 주입)
    """
    # 기존 TODO 조회
    db_todo = get_todo_by_id(todo_id, db)

    # 업데이트 데이터 적용 (None이 아닌 값만)
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)

    # DB에 커밋
    db.commit()
    db.refresh(db_todo)

    return db_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    TODO 삭제

    - **todo_id**: 삭제할 TODO의 ID
    - **db**: 데이터베이스 세션 (DI로 주입)
    """
    # 기존 TODO 조회
    db_todo = get_todo_by_id(todo_id, db)

    # DB에서 삭제
    db.delete(db_todo)
    db.commit()

    return None
