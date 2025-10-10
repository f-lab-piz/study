# FastAPI 초보자 가이드

## 목차
1. [핵심 개념 소개](#1-핵심-개념-소개)
2. [프로젝트 셋업 (uv 사용)](#2-프로젝트-셋업-uv-사용)
3. [간단한 FastAPI 애플리케이션 만들기](#3-간단한-fastapi-애플리케이션-만들기)
4. [코드 상세 설명](#4-코드-상세-설명)
5. [실행 및 테스트](#5-실행-및-테스트)

---

## 1. 핵심 개념 소개

### FastAPI란?

**FastAPI**는 Python으로 빠르고 현대적인 웹 API를 만들기 위한 웹 프레임워크입니다.

**주요 특징:**
- ⚡ **빠름**: Node.js, Go와 대등한 성능
- 🚀 **빠른 개발**: 기능 개발 속도 약 200~300% 향상
- 🐛 **적은 버그**: 개발자 실수 약 40% 감소
- 💡 **직관적**: 훌륭한 IDE 지원 (자동완성)
- 📝 **자동 문서화**: Swagger UI 자동 생성
- 🔍 **타입 체크**: Python 타입 힌트 기반

**비유로 이해하기:**
```
Django = 종합병원 (모든 기능 포함, 무겁지만 완전함)
Flask  = 동네 병원 (가볍고 간단, 확장 가능)
FastAPI = 최신 스마트 병원 (빠르고, 현대적이고, 자동화됨)
```

---

### uv란?

**uv**는 Python 패키지 및 프로젝트 관리 도구입니다. Rust로 작성되어 매우 빠릅니다.

**기존 도구와 비교:**

| 도구 | 역할 | 속도 | 특징 |
|-----|------|------|------|
| **pip** | 패키지 설치 | 보통 | 기본 도구 |
| **poetry** | 의존성 + 가상환경 관리 | 느림 | 인기 있음 |
| **uv** | 패키지 + 프로젝트 + 가상환경 | 매우 빠름 | 차세대 도구 |

**uv가 해결하는 문제:**
- ❌ pip + venv 조합의 복잡함
- ❌ poetry의 느린 속도
- ❌ 의존성 충돌 해결의 어려움

**uv로 할 수 있는 것:**
```bash
uv init myproject        # 프로젝트 초기화
uv add fastapi          # 패키지 설치 (자동으로 pyproject.toml 업데이트)
uv run python main.py   # 가상환경에서 실행
uv sync                 # 의존성 동기화
```

**비유로 이해하기:**
```
pip     = 수동 자동차 (직접 다 해야 함)
poetry  = 자동 자동차 (편하지만 느림)
uv      = 전기차 (빠르고 현대적)
```

---

### uvicorn이란?

**uvicorn**은 ASGI 서버입니다. FastAPI 애플리케이션을 실제로 실행시키는 엔진입니다.

**역할:**
```
FastAPI (프레임워크) + uvicorn (서버) = 실행되는 웹 애플리케이션
```

**비유로 이해하기:**
```
FastAPI = 자동차 설계도
uvicorn = 엔진

설계도만 있어도 자동차는 안 움직임
엔진이 있어야 실제로 주행 가능
```

**실행 방법:**
```bash
# 기본 실행
uvicorn main:app

# 개발 모드 (코드 변경 시 자동 재시작)
uvicorn main:app --reload

# 포트 변경
uvicorn main:app --port 8080
```

---

### Pydantic이란?

**Pydantic**은 Python 타입 힌트를 사용한 데이터 검증 라이브러리입니다.

**핵심 기능:**

1. **자동 타입 검증**
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# 정상
user = User(name="홍길동", age=25)

# 에러! (age는 int여야 함)
user = User(name="홍길동", age="25")  # ValidationError
```

2. **자동 타입 변환**
```python
user = User(name="홍길동", age="25")  # 문자열 "25"
print(user.age)  # 25 (int로 자동 변환!)
```

3. **IDE 자동완성**
```python
user = User(name="홍길동", age=25)
user.name  # IDE가 자동완성 지원
user.age   # 타입 체크 가능
```

**FastAPI에서의 역할:**
```python
@app.post("/users/")
def create_user(user: User):  # Pydantic 모델
    # FastAPI가 자동으로:
    # 1. 요청 JSON을 검증
    # 2. User 객체로 변환
    # 3. 타입 에러 시 자동으로 400 응답
    return user
```

**비유로 이해하기:**
```
일반 dict = 봉투 (안에 뭐가 들었는지 열어봐야 알 수 있음)
Pydantic  = 투명 상자 (안에 뭐가 있는지 보임, 잘못된 것 넣으면 거부)
```

---

### Dependency Injection (DI)란?

**의존성 주입(DI)**은 함수나 클래스가 필요로 하는 것을 외부에서 주입받는 패턴입니다.

**DI 없이 작성한 코드:**
```python
def get_user():
    # 함수 내부에서 직접 DB 연결
    db = Database()  # 강결합!
    return db.query("SELECT * FROM users")

# 문제점:
# 1. 테스트 어려움 (실제 DB 필요)
# 2. 코드 재사용 어려움
# 3. DB 변경 시 모든 함수 수정 필요
```

**DI를 사용한 코드:**
```python
def get_user(db: Database = Depends(get_db)):
    # DB를 외부에서 주입받음
    return db.query("SELECT * FROM users")

# 장점:
# 1. 테스트 시 Mock DB 주입 가능
# 2. DB 변경 시 get_db 함수만 수정
# 3. 코드 재사용 용이
```

**FastAPI의 Depends:**
```python
from fastapi import Depends

def get_current_user(token: str = Depends(get_token)):
    # token을 자동으로 주입받음
    return verify_token(token)

@app.get("/me")
def read_users_me(user: User = Depends(get_current_user)):
    # current_user를 자동으로 주입받음
    return user
```

**비유로 이해하기:**
```
DI 없음 = 요리사가 재료를 직접 시장에서 사옴 (강결합)
DI 있음 = 요리사가 준비된 재료를 받아서 요리만 함 (느슨한 결합)
```

**DI의 이점:**

| 항목 | DI 없음 | DI 있음 |
|-----|---------|---------|
| **테스트** | 어려움 (실제 의존성 필요) | 쉬움 (Mock 주입) |
| **유지보수** | 어려움 (강결합) | 쉬움 (느슨한 결합) |
| **재사용성** | 낮음 | 높음 |

---

### 전체 구조 한눈에 보기

```
┌─────────────────────────────────────────────────────────┐
│                      uv (프로젝트 관리)                  │
│  - 패키지 설치/관리                                      │
│  - 가상환경 생성                                         │
│  - 의존성 해결                                           │
└─────────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (웹 프레임워크)               │
│  - 라우팅 (@app.get, @app.post)                         │
│  - 요청/응답 처리                                        │
│  - 자동 문서화                                           │
└─────────────────────────────────────────────────────────┘
         │                                      │
         ↓                                      ↓
┌──────────────────────┐            ┌──────────────────────┐
│   Pydantic (검증)     │            │   Depends (DI)       │
│  - 타입 검증          │            │  - 의존성 주입       │
│  - 자동 변환          │            │  - 재사용 가능 로직  │
│  - 문서 자동 생성     │            │  - 테스트 용이       │
└──────────────────────┘            └──────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────┐
│                  uvicorn (ASGI 서버)                     │
│  - FastAPI 앱 실행                                       │
│  - HTTP 요청 처리                                        │
│  - Hot reload (개발 모드)                                │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 프로젝트 셋업 (uv 사용)

### uv 설치

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**설치 확인:**
```bash
uv --version
```

---

### 프로젝트 생성

```bash
# 1. 새 프로젝트 생성
uv init todo-api
cd todo-api

# 2. FastAPI 및 의존성 설치
uv add fastapi
uv add "uvicorn[standard]"

# 3. 프로젝트 구조 확인
tree .
```

**생성된 구조:**
```
todo-api/
├── .python-version        # Python 버전
├── pyproject.toml         # 프로젝트 설정 및 의존성
├── uv.lock               # 의존성 잠금 파일
├── .venv/                # 가상환경 (자동 생성)
└── hello.py              # 기본 생성 파일
```

**pyproject.toml 내용:**
```toml
[project]
name = "todo-api"
version = "0.1.0"
description = "Simple TODO API with FastAPI"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.6",
    "uvicorn[standard]>=0.34.0",
]
```

---

## 3. 간단한 FastAPI 애플리케이션 만들기

### 프로젝트 구조

```
todo-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 진입점
│   ├── models.py            # Pydantic 모델
│   ├── dependencies.py      # DI 함수들
│   └── routers/
│       ├── __init__.py
│       └── todos.py         # TODO API 라우터
├── pyproject.toml
└── README.md
```

---

### 1. Pydantic 모델 정의

**app/models.py**
```python
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
```

---

### 2. Dependency Injection 함수

**app/dependencies.py**
```python
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
```

---

### 3. TODO 라우터

**app/routers/todos.py**
```python
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
```

---

### 4. 메인 애플리케이션

**app/main.py**
```python
"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from app.routers import todos

# FastAPI 앱 생성
app = FastAPI(
    title="TODO API",
    description="FastAPI로 만든 간단한 TODO 관리 API",
    version="1.0.0",
)

# 라우터 등록
app.include_router(todos.router)


@app.get("/")
def root():
    """
    루트 엔드포인트
    API 상태 확인용
    """
    return {
        "message": "TODO API에 오신 것을 환영합니다!",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    헬스 체크 엔드포인트
    서버 상태 모니터링용
    """
    return {"status": "healthy"}
```

---

### 5. 초기화 파일

**app/__init__.py**
```python
"""
app 패키지 초기화
"""
```

**app/routers/__init__.py**
```python
"""
routers 패키지 초기화
"""
```

---

## 4. 코드 상세 설명

### Pydantic 모델의 역할

```python
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: bool = Field(False)
```

**각 부분 설명:**

| 코드 | 의미 |
|-----|------|
| `BaseModel` | Pydantic 기본 클래스 |
| `Field(...)` | 필수 필드 (반드시 입력해야 함) |
| `Field(None)` | 선택적 필드 (입력 안 해도 됨) |
| `min_length=1` | 최소 길이 검증 |
| `max_length=100` | 최대 길이 검증 |
| `description=` | API 문서에 표시될 설명 |

**Pydantic이 자동으로 해주는 것:**

1. **타입 검증**
```python
# 요청: {"title": 123}
# 결과: ValidationError (title은 str이어야 함)
```

2. **자동 변환**
```python
# 요청: {"completed": "true"}
# 결과: completed=True (bool로 자동 변환)
```

3. **문서 생성**
```python
# Swagger UI에 자동으로:
# - 필드 목록
# - 필드 타입
# - 필수/선택 여부
# - 예시 데이터
```

---

### Depends (의존성 주입)의 동작

```python
@router.get("/")
def list_todos(db: Dict[int, dict] = Depends(get_todo_storage)):
    return list(db.values())
```

**실행 흐름:**

```
1. 클라이언트 요청: GET /todos/

2. FastAPI가 Depends 발견
   ↓
3. get_todo_storage() 함수 실행
   ↓
4. 반환값 (fake_db)을 db 파라미터에 주입
   ↓
5. list_todos(db=fake_db) 실행
   ↓
6. 응답 반환
```

**이점:**

```python
# 테스트 시
def test_list_todos():
    mock_db = {1: {"id": 1, "title": "Test"}}
    # mock_db를 주입 가능!
    result = list_todos(db=mock_db)
    assert len(result) == 1
```

---

### FastAPI 라우터 데코레이터

```python
@router.get("/", response_model=List[TodoResponse])
def list_todos(...):
    pass
```

**각 부분 설명:**

| 코드 | 의미 |
|-----|------|
| `@router.get` | HTTP GET 메서드 |
| `"/"` | 경로 (prefix와 합쳐져 /todos/) |
| `response_model` | 응답 데이터 형식 (Pydantic 모델) |

**response_model의 역할:**

1. **응답 검증**: 반환 데이터가 TodoResponse 형식인지 확인
2. **문서 생성**: Swagger UI에 응답 예시 표시
3. **불필요한 필드 제거**: 모델에 없는 필드 자동 필터링

---

### 경로 파라미터와 요청 바디

```python
@router.put("/{todo_id}")
def update_todo(
    todo_id: int,              # 경로 파라미터
    todo_update: TodoUpdate,   # 요청 바디
    db: Dict = Depends(...)    # 의존성
):
    pass
```

**FastAPI의 자동 파싱:**

```
요청: PUT /todos/1
바디: {"title": "새 제목"}

FastAPI가 자동으로:
1. todo_id=1 파싱 (경로에서)
2. todo_update=TodoUpdate(title="새 제목") 파싱 (바디에서)
3. db 주입 (Depends에서)
4. 함수 실행
```

---

### 에러 처리

```python
def get_todo_by_id(todo_id: int, db: Dict) -> dict:
    todo = db.get(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {todo_id}인 TODO를 찾을 수 없습니다."
        )
    return todo
```

**HTTPException의 효과:**

```
요청: GET /todos/999 (존재하지 않는 ID)

자동 응답:
{
  "detail": "ID 999인 TODO를 찾을 수 없습니다."
}
HTTP 상태 코드: 404
```

---

## 5. 실행 및 테스트

### 서버 실행

```bash
# 프로젝트 루트에서
cd todo-api

# 개발 모드로 실행 (Hot reload)
uv run uvicorn app.main:app --reload

# 또는 포트 지정
uv run uvicorn app.main:app --reload --port 8000
```

**실행 성공 시 출력:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

### API 문서 확인

**Swagger UI (자동 생성):**
```
http://127.0.0.1:8000/docs
```

**ReDoc (대체 문서):**
```
http://127.0.0.1:8000/redoc
```

**Swagger UI에서 할 수 있는 것:**
- 📖 모든 엔드포인트 확인
- 🧪 직접 API 테스트 ("Try it out" 버튼)
- 📝 요청/응답 스키마 확인
- 💡 예시 데이터 확인

---

### curl로 테스트

#### 1. 루트 엔드포인트
```bash
curl http://127.0.0.1:8000/
```

**응답:**
```json
{
  "message": "TODO API에 오신 것을 환영합니다!",
  "docs": "/docs",
  "version": "1.0.0"
}
```

#### 2. TODO 생성
```bash
curl -X POST http://127.0.0.1:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FastAPI 공부하기",
    "description": "Pydantic과 DI 개념 학습",
    "completed": false
  }'
```

**응답:**
```json
{
  "id": 1,
  "title": "FastAPI 공부하기",
  "description": "Pydantic과 DI 개념 학습",
  "completed": false
}
```

#### 3. TODO 목록 조회
```bash
curl http://127.0.0.1:8000/todos/
```

**응답:**
```json
[
  {
    "id": 1,
    "title": "FastAPI 공부하기",
    "description": "Pydantic과 DI 개념 학습",
    "completed": false
  }
]
```

#### 4. 특정 TODO 조회
```bash
curl http://127.0.0.1:8000/todos/1
```

**응답:**
```json
{
  "id": 1,
  "title": "FastAPI 공부하기",
  "description": "Pydantic과 DI 개념 학습",
  "completed": false
}
```

#### 5. TODO 수정
```bash
curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

**응답:**
```json
{
  "id": 1,
  "title": "FastAPI 공부하기",
  "description": "Pydantic과 DI 개념 학습",
  "completed": true
}
```

#### 6. TODO 삭제
```bash
curl -X DELETE http://127.0.0.1:8000/todos/1
```

**응답:**
```
HTTP 204 No Content
(응답 바디 없음)
```

#### 7. 존재하지 않는 TODO 조회 (에러)
```bash
curl http://127.0.0.1:8000/todos/999
```

**응답:**
```json
{
  "detail": "ID 999인 TODO를 찾을 수 없습니다."
}
```

---

### Python으로 테스트

```python
# test_api.py
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. TODO 생성
response = requests.post(
    f"{BASE_URL}/todos/",
    json={
        "title": "장보기",
        "description": "우유, 계란, 빵"
    }
)
print("생성:", response.json())
todo_id = response.json()["id"]

# 2. TODO 조회
response = requests.get(f"{BASE_URL}/todos/{todo_id}")
print("조회:", response.json())

# 3. TODO 수정
response = requests.put(
    f"{BASE_URL}/todos/{todo_id}",
    json={"completed": True}
)
print("수정:", response.json())

# 4. TODO 목록
response = requests.get(f"{BASE_URL}/todos/")
print("목록:", response.json())

# 5. TODO 삭제
response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
print("삭제:", response.status_code)
```

---

## 부록: 자주 묻는 질문

### Q1: FastAPI vs Flask, 어떤 걸 선택해야 하나요?

| 상황 | 추천 |
|-----|------|
| 새 프로젝트 시작 | FastAPI |
| 빠른 성능 필요 | FastAPI |
| 자동 문서화 필요 | FastAPI |
| 타입 안정성 중요 | FastAPI |
| 레거시 코드 유지 | Flask |
| 간단한 웹 앱 | Flask |

---

### Q2: uv vs poetry, 어떤 걸 사용해야 하나요?

| 상황 | 추천 |
|-----|------|
| 새 프로젝트 | uv (빠르고 현대적) |
| 기존 poetry 프로젝트 | poetry 유지 (마이그레이션 고려) |
| 속도가 중요 | uv |
| 안정성이 최우선 | poetry (더 오래됨) |

---

### Q3: Pydantic V1 vs V2?

현재는 **Pydantic V2**를 사용하세요.

**주요 차이점:**
```python
# V1
class User(BaseModel):
    class Config:
        orm_mode = True

# V2
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

---

### Q4: 비동기 (async/await)는 언제 사용하나요?

**동기 함수 (일반):**
```python
@app.get("/users")
def get_users():
    return db.query()  # DB 작업
```

**비동기 함수 (추천):**
```python
@app.get("/users")
async def get_users():
    return await db.query()  # 비동기 DB 작업
```

**사용 기준:**
- 🟢 비동기 사용: I/O 작업 (DB, 외부 API 호출 등)
- 🔴 동기 사용: CPU 작업 (계산, 이미지 처리 등)

---

### Q5: 실제 프로젝트에서는 어떻게 구성하나요?

```
production-app/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── users.py
│   │       │   └── items.py
│   │       └── api.py
│   ├── core/
│   │   ├── config.py      # 환경 설정
│   │   └── security.py    # 인증/인가
│   ├── db/
│   │   ├── database.py    # DB 연결
│   │   └── models.py      # SQLAlchemy 모델
│   ├── schemas/           # Pydantic 모델
│   │   ├── user.py
│   │   └── item.py
│   └── main.py
├── tests/
├── alembic/              # DB 마이그레이션
├── pyproject.toml
└── .env
```

---

## 다음 단계

이 가이드를 완료했다면:

1. ✅ **DB 연결 학습**
   - SQLAlchemy + PostgreSQL
   - MongoDB + Motor

2. ✅ **인증/인가**
   - JWT 토큰
   - OAuth2

3. ✅ **테스트 작성**
   - pytest
   - httpx (비동기 클라이언트)

4. ✅ **배포**
   - Docker
   - AWS/GCP/Azure

---

## 참고 자료

- **FastAPI 공식 문서**: https://fastapi.tiangolo.com/
- **Pydantic 공식 문서**: https://docs.pydantic.dev/
- **uv 공식 문서**: https://docs.astral.sh/uv/
- **uvicorn 공식 문서**: https://www.uvicorn.org/

---

## 요약

### 핵심 개념 정리

| 도구/개념 | 역할 | 비유 |
|----------|------|------|
| **uv** | 프로젝트 관리 | 전기차 (빠르고 현대적) |
| **FastAPI** | 웹 프레임워크 | 자동차 설계도 |
| **uvicorn** | ASGI 서버 | 엔진 |
| **Pydantic** | 데이터 검증 | 투명 상자 (타입 안전) |
| **Depends** | 의존성 주입 | 재료를 받아서 요리 |

### 개발 워크플로우

```
1. uv init project        # 프로젝트 생성
2. uv add fastapi         # 패키지 설치
3. 코드 작성              # Pydantic 모델 + 라우터
4. uv run uvicorn ...     # 서버 실행
5. http://localhost:8000/docs  # 테스트
```

### 성공적인 FastAPI 개발의 핵심

1. ✅ **Pydantic 모델 먼저 설계** - 데이터 구조가 명확해짐
2. ✅ **Depends로 로직 분리** - 테스트와 재사용 용이
3. ✅ **자동 문서 활용** - /docs로 API 확인
4. ✅ **타입 힌트 사용** - IDE 지원 + 버그 감소
