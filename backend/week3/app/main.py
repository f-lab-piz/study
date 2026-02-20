"""
3주차: FastAPI User CRUD (테스트용)
- Week2의 코드를 패키지 구조로 재구성
- SQLAlchemy 2.x 호환 (text() 사용)
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .database import engine, get_db, Base
from .models import User

# 앱 시작 시 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="3주차 - 테스트 대상 CRUD API",
    description="pytest + Locust 테스트를 위한 User CRUD",
    version="0.3.0",
)


# ===========================================
# Pydantic 스키마
# ===========================================


class UserCreate(BaseModel):
    """유저 생성 요청 스키마"""

    name: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "김철수",
                "email": "kim@example.com",
            }
        }


class UserUpdate(BaseModel):
    """유저 수정 요청 스키마 (모두 선택적)"""

    name: str | None = None
    email: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "김영희",
                "email": "kim.new@example.com",
            }
        }


class UserResponse(BaseModel):
    """유저 응답 스키마"""

    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


# ===========================================
# 헬스체크
# ===========================================


@app.get("/")
def root():
    """루트 경로 - 서버 상태 확인"""
    return {"message": "Week3 - Testing CRUD API", "status": "running"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """헬스체크 - DB 연결 확인"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


# ===========================================
# CRUD API
# ===========================================


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """새 유저 생성"""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")

    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.get("/users", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """모든 유저 조회 (페이지네이션)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """특정 유저 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """유저 정보 수정 (부분 업데이트)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    if user.name is not None:
        db_user.name = user.name
    if user.email is not None:
        existing = (
            db.query(User)
            .filter(User.email == user.email, User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")
        db_user.email = user.email

    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """유저 삭제"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    db.delete(db_user)
    db.commit()

    return {"message": "삭제 완료", "deleted_id": user_id}


# ===========================================
# 통계 API
# ===========================================


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """전체 유저 수 조회"""
    total_users = db.query(User).count()
    return {"total_users": total_users}
