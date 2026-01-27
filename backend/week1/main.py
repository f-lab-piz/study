"""
1주차: FastAPI 기본
- 백엔드가 뭔지 감 잡기
- 첫 API 만들어보기
- CRUD 맛보기 (DB 없이 dict로)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# FastAPI 앱 생성
app = FastAPI(
    title="1주차 - FastAPI 기본",
    description="백엔드 첫 걸음",
    version="0.1.0",
)


# ===========================================
# 기본 API
# ===========================================


@app.get("/")
def root():
    """루트 경로 - 서버가 살아있는지 확인"""
    return {"message": "Hello, Backend!"}


@app.get("/health")
def health_check():
    """헬스체크 API - 서버 상태 확인용"""
    return {"status": "ok"}


# ===========================================
# CRUD 실습 - 유저 관리 (DB 없이 dict 사용)
# ===========================================

# 가짜 데이터베이스 (메모리에 저장, 서버 재시작하면 초기화됨)
fake_db: dict[int, dict] = {
    1: {"id": 1, "name": "김철수", "email": "kim@example.com"},
    2: {"id": 2, "name": "이영희", "email": "lee@example.com"},
}

# 다음에 생성할 유저의 ID
next_id = 3


# 요청 Body를 검증할 Pydantic 모델
class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


# -------------------------------------------
# Create - POST /users
# -------------------------------------------
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    """새 유저 생성"""
    global next_id

    new_user = {
        "id": next_id,
        "name": user.name,
        "email": user.email,
    }
    fake_db[next_id] = new_user
    next_id += 1

    return new_user


# -------------------------------------------
# Read - GET /users, GET /users/{user_id}
# -------------------------------------------
@app.get("/users")
def get_users():
    """모든 유저 조회"""
    return list(fake_db.values())


@app.get("/users/{user_id}")
def get_user(user_id: int):
    """특정 유저 조회 (Path Parameter 사용)"""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    return fake_db[user_id]


# -------------------------------------------
# Update - PUT /users/{user_id}
# -------------------------------------------
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    """유저 정보 수정"""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    # 기존 데이터 가져오기
    existing_user = fake_db[user_id]

    # 전달된 값만 업데이트
    if user.name is not None:
        existing_user["name"] = user.name
    if user.email is not None:
        existing_user["email"] = user.email

    return existing_user


# -------------------------------------------
# Delete - DELETE /users/{user_id}
# -------------------------------------------
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """유저 삭제"""
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    deleted_user = fake_db.pop(user_id)
    return {"message": "삭제 완료", "deleted": deleted_user}
