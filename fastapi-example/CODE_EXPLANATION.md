# FastAPI 예제 코드 상세 설명

이 문서는 TODO API 예제의 각 코드 파일을 라인별로 설명합니다.

## 목차
1. [models.py - Pydantic 모델](#1-modelspy---pydantic-모델)
2. [dependencies.py - 의존성 주입](#2-dependenciespy---의존성-주입)
3. [routers/todos.py - API 라우터](#3-routerstodospy---api-라우터)
4. [main.py - 메인 애플리케이션](#4-mainpy---메인-애플리케이션)

---

## 1. models.py - Pydantic 모델

### 전체 흐름

```
TodoBase (기본 필드)
    ↓
TodoCreate (생성 시 사용)
TodoUpdate (수정 시 사용)
TodoResponse (응답 시 사용, id 추가)
```

### 코드 분석

#### Import 구문

```python
from pydantic import BaseModel, Field
from typing import Optional
```

**설명:**
- `BaseModel`: Pydantic의 기본 클래스. 모든 모델은 이것을 상속
- `Field`: 필드에 추가 검증 규칙과 메타데이터를 지정
- `Optional`: 선택적 필드 표시 (값이 None일 수 있음)

---

#### TodoBase 클래스

```python
class TodoBase(BaseModel):
    """TODO 기본 스키마"""
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목")
    description: Optional[str] = Field(None, max_length=500, description="할 일 설명")
    completed: bool = Field(False, description="완료 여부")
```

**라인별 설명:**

| 코드 | 설명 |
|-----|------|
| `class TodoBase(BaseModel)` | Pydantic 모델 정의 |
| `title: str` | title 필드는 문자열 타입 |
| `Field(...)` | 필수 필드 (반드시 값이 있어야 함) |
| `min_length=1` | 최소 1자 이상 |
| `max_length=100` | 최대 100자 이하 |
| `description="..."` | API 문서에 표시될 설명 |
| `Optional[str]` | 선택적 문자열 (None 가능) |
| `Field(None)` | 기본값 None |
| `completed: bool` | boolean 타입 |
| `Field(False)` | 기본값 False |

**동작 예시:**

```python
# ✅ 정상 - 필수 필드 title 존재
todo = TodoBase(title="공부하기")
# 결과: title="공부하기", description=None, completed=False

# ❌ 에러 - title 누락
todo = TodoBase(description="설명만")
# ValidationError: field required

# ❌ 에러 - title이 너무 김
todo = TodoBase(title="a" * 101)
# ValidationError: ensure this value has at most 100 characters

# ✅ 정상 - 자동 타입 변환
todo = TodoBase(title="공부", completed="true")
# 결과: completed=True (문자열 → bool 자동 변환)
```

---

#### TodoCreate 클래스

```python
class TodoCreate(TodoBase):
    """TODO 생성 요청 스키마"""
    pass
```

**설명:**
- `TodoBase`를 그대로 상속
- 추가 필드 없음
- API 문서에서 "생성 요청"과 "응답"을 구분하기 위해 분리
- 나중에 생성 시 특정 검증 규칙 추가 가능

**사용 예시:**

```python
@app.post("/todos/")
def create_todo(todo: TodoCreate):  # TodoCreate 타입 명시
    # FastAPI가 자동으로:
    # 1. 요청 JSON 파싱
    # 2. TodoCreate로 검증
    # 3. 에러 시 400 응답
    pass
```

---

#### TodoUpdate 클래스

```python
class TodoUpdate(BaseModel):
    """TODO 수정 요청 스키마 (모든 필드 선택적)"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None
```

**왜 모든 필드가 Optional일까?**

수정(UPDATE) 시에는 **일부 필드만 변경**할 수 있어야 합니다.

```python
# ✅ title만 수정
update_data = TodoUpdate(title="새 제목")

# ✅ completed만 수정
update_data = TodoUpdate(completed=True)

# ✅ 여러 필드 수정
update_data = TodoUpdate(title="새 제목", completed=True)
```

**실제 동작:**

```python
# 기존 TODO
existing = {"id": 1, "title": "공부", "description": "열심히", "completed": False}

# 수정 요청
update = TodoUpdate(completed=True)  # title은 변경 안 함

# model_dump(exclude_unset=True) 사용
update_data = update.model_dump(exclude_unset=True)
# 결과: {"completed": True}
# title, description은 포함 안 됨 → 기존 값 유지!
```

---

#### TodoResponse 클래스

```python
class TodoResponse(TodoBase):
    """TODO 응답 스키마"""
    id: int = Field(..., description="TODO ID")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "FastAPI 공부하기",
                "description": "FastAPI 기초 개념 학습",
                "completed": False
            }
        }
```

**설명:**

| 부분 | 역할 |
|-----|------|
| `id: int` | 응답에만 포함되는 ID 필드 (생성 시는 서버가 할당) |
| `class Config` | Pydantic 설정 클래스 |
| `json_schema_extra` | API 문서(Swagger)에 표시될 예시 데이터 |

**API 문서에서 어떻게 보이나요?**

Swagger UI (`/docs`)에서:
```json
{
  "id": 1,
  "title": "FastAPI 공부하기",
  "description": "FastAPI 기초 개념 학습",
  "completed": false
}
```
이 예시가 자동으로 표시됩니다.

---

## 2. dependencies.py - 의존성 주입

### 전체 흐름

```
FastAPI 엔드포인트
    ↓
Depends(get_todo_storage)
    ↓
fake_db 반환
    ↓
엔드포인트 함수 실행
```

### 코드 분석

#### 전역 변수

```python
fake_db: Dict[int, dict] = {}
next_id: int = 1
```

**설명:**
- `fake_db`: 메모리에 TODO 저장 (실제로는 DB 사용)
- `next_id`: 다음에 생성될 TODO의 ID
- 서버 재시작 시 데이터 소실 (메모리 기반)

**실제 프로젝트에서는:**

```python
# PostgreSQL 예시
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

#### get_todo_storage 함수

```python
def get_todo_storage() -> Dict[int, dict]:
    """TODO 저장소를 반환하는 의존성"""
    return fake_db
```

**왜 함수로 감싸나요?**

```python
# ❌ 직접 사용 (DI 없음)
@app.get("/todos/")
def list_todos():
    return list(fake_db.values())  # fake_db에 강하게 결합

# ✅ DI 사용
@app.get("/todos/")
def list_todos(db = Depends(get_todo_storage)):
    return list(db.values())  # db는 주입됨 → 테스트 시 교체 가능
```

**테스트 예시:**

```python
# 테스트 시 Mock DB 주입
def test_list_todos():
    mock_db = {1: {"id": 1, "title": "Test"}}
    result = list_todos(db=mock_db)  # 실제 DB 없이 테스트!
    assert len(result) == 1
```

---

#### get_todo_by_id 함수

```python
def get_todo_by_id(todo_id: int, db: Dict[int, dict]) -> dict:
    """ID로 TODO를 조회하는 함수"""
    todo = db.get(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {todo_id}인 TODO를 찾을 수 없습니다."
        )
    return todo
```

**HTTPException이 하는 일:**

```python
# 요청: GET /todos/999

# get_todo_by_id(999, fake_db) 실행
# fake_db.get(999) → None
# HTTPException 발생

# FastAPI가 자동으로 응답:
{
  "detail": "ID 999인 TODO를 찾을 수 없습니다."
}
# HTTP 상태 코드: 404
```

**왜 함수를 분리했나요?**

```python
# 여러 엔드포인트에서 재사용
@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, db = Depends(get_todo_storage)):
    return get_todo_by_id(todo_id, db)  # 재사용

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, db = Depends(get_todo_storage)):
    existing = get_todo_by_id(todo_id, db)  # 재사용
    # 수정 로직...
```

---

#### get_next_id 함수

```python
def get_next_id() -> int:
    """다음 ID를 반환하는 함수"""
    global next_id
    current_id = next_id
    next_id += 1
    return current_id
```

**동작:**

```python
get_next_id()  # 1 반환, next_id=2
get_next_id()  # 2 반환, next_id=3
get_next_id()  # 3 반환, next_id=4
```

**실제 DB에서는:**

```python
# PostgreSQL의 SERIAL 타입 (자동 증가)
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,  # 자동으로 1, 2, 3, ...
    title VARCHAR(100),
    ...
);
```

---

## 3. routers/todos.py - API 라우터

### 전체 구조

```
APIRouter 생성
    ↓
엔드포인트 정의
    - list_todos (GET /)
    - get_todo (GET /{id})
    - create_todo (POST /)
    - update_todo (PUT /{id})
    - delete_todo (DELETE /{id})
```

### APIRouter 생성

```python
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)
```

**설명:**

| 파라미터 | 의미 | 효과 |
|---------|------|------|
| `prefix="/todos"` | 모든 경로 앞에 붙임 | `/` → `/todos/` |
| `tags=["todos"]` | Swagger 그룹 | "todos" 섹션으로 묶임 |

**main.py에서 등록:**

```python
app.include_router(router)
# 이제 /todos/로 시작하는 모든 경로 활성화
```

---

### list_todos (목록 조회)

```python
@router.get("/", response_model=List[TodoResponse])
def list_todos(db: Dict[int, dict] = Depends(get_todo_storage)):
    """모든 TODO 목록 조회"""
    return list(db.values())
```

**라인별 분석:**

```python
@router.get("/")
# - HTTP GET 메서드
# - 경로: /todos/ (prefix + /)
# - 실제 URL: http://localhost:8000/todos/

response_model=List[TodoResponse]
# - 응답 타입: TodoResponse 리스트
# - FastAPI가 자동으로:
#   1. 반환 데이터 검증
#   2. TodoResponse 형식으로 변환
#   3. API 문서 생성

db: Dict[int, dict] = Depends(get_todo_storage)
# - db 파라미터에 fake_db 주입
# - FastAPI가 자동으로 get_todo_storage() 호출

return list(db.values())
# - db의 모든 값을 리스트로 변환
# - 예: [{"id": 1, "title": "..."}, {"id": 2, "title": "..."}]
```

**실행 흐름:**

```
1. 클라이언트: GET /todos/
2. FastAPI: get_todo_storage() 호출 → fake_db 반환
3. FastAPI: list_todos(db=fake_db) 호출
4. 함수: list(fake_db.values()) 반환
5. FastAPI: 각 dict를 TodoResponse로 검증
6. 응답: JSON 리스트
```

---

### get_todo (단일 조회)

```python
@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """특정 TODO 조회"""
    return get_todo_by_id(todo_id, db)
```

**경로 파라미터:**

```python
"/{todo_id}"
# - 중괄호 안의 변수 = 경로 파라미터
# - 예: /todos/1 → todo_id=1
# - 예: /todos/42 → todo_id=42

todo_id: int
# - 타입 힌트: int
# - FastAPI가 자동으로:
#   1. 문자열을 int로 변환
#   2. 변환 실패 시 422 에러
```

**요청 예시:**

```bash
# 요청
GET /todos/1

# FastAPI 처리
1. todo_id="1" (문자열) → todo_id=1 (int)
2. db = get_todo_storage() → fake_db
3. get_todo(todo_id=1, db=fake_db)
4. get_todo_by_id(1, fake_db) 호출
5. fake_db에서 id=1 찾기
6. 있으면 반환, 없으면 404
```

---

### create_todo (생성)

```python
@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED
)
def create_todo(
    todo: TodoCreate,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """새 TODO 생성"""
    new_id = get_next_id()
    new_todo = {
        "id": new_id,
        **todo.model_dump()
    }
    db[new_id] = new_todo
    return new_todo
```

**라인별 분석:**

```python
@router.post("/")
# - HTTP POST 메서드
# - 경로: /todos/

status_code=status.HTTP_201_CREATED
# - 성공 시 상태 코드: 201 (생성됨)
# - 기본값은 200

todo: TodoCreate
# - 요청 바디를 TodoCreate로 파싱
# - FastAPI가 자동으로:
#   1. JSON 파싱
#   2. TodoCreate 검증
#   3. 에러 시 422 응답

new_id = get_next_id()
# - 새 ID 생성 (1, 2, 3, ...)

**todo.model_dump()
# - Pydantic 모델 → dict 변환
# - ** 연산자로 dict 펼치기
# - 예:
#   todo = TodoCreate(title="공부", completed=False)
#   todo.model_dump() → {"title": "공부", "completed": False, "description": None}
#   **todo.model_dump() → title="공부", completed=False, description=None

new_todo = {"id": new_id, **todo.model_dump()}
# - id 필드 추가 + 기존 필드 병합
# - 예: {"id": 1, "title": "공부", "description": None, "completed": False}

db[new_id] = new_todo
# - fake_db에 저장
# - fake_db = {1: {...}}

return new_todo
# - 생성된 TODO 반환
# - FastAPI가 TodoResponse로 검증
```

**요청/응답 예시:**

```bash
# 요청
POST /todos/
Content-Type: application/json

{
  "title": "운동하기",
  "completed": false
}

# FastAPI 처리
1. JSON 파싱
2. TodoCreate 검증 (title 필수, completed bool)
3. create_todo 실행
4. new_id = 1
5. new_todo = {"id": 1, "title": "운동하기", "completed": false, "description": null}
6. fake_db[1] = new_todo
7. 응답 반환

# 응답
HTTP 201 Created

{
  "id": 1,
  "title": "운동하기",
  "description": null,
  "completed": false
}
```

---

### update_todo (수정)

```python
@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """TODO 수정"""
    existing_todo = get_todo_by_id(todo_id, db)

    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        existing_todo[key] = value

    return existing_todo
```

**핵심: `exclude_unset=True`**

```python
# 요청
PUT /todos/1
{
  "completed": true
}
# title, description은 보내지 않음!

# 처리
todo_update = TodoUpdate(completed=True)
# 내부적으로: title=None, description=None, completed=True

todo_update.model_dump()
# 결과: {"title": None, "description": None, "completed": True}
# ❌ 문제: title, description이 None으로 덮어씌워짐!

todo_update.model_dump(exclude_unset=True)
# 결과: {"completed": True}
# ✅ 좋음: 실제로 설정한 값만 포함!
```

**전체 흐름:**

```python
# 기존 TODO
existing_todo = {"id": 1, "title": "공부", "description": "열심히", "completed": False}

# 요청
PUT /todos/1
{"completed": True}

# 처리
1. existing_todo = get_todo_by_id(1, db)
   # {"id": 1, "title": "공부", "description": "열심히", "completed": False}

2. update_data = todo_update.model_dump(exclude_unset=True)
   # {"completed": True}

3. for key, value in update_data.items():
       existing_todo[key] = value
   # existing_todo["completed"] = True

4. return existing_todo
   # {"id": 1, "title": "공부", "description": "열심히", "completed": True}
   # title, description 유지됨!
```

---

### delete_todo (삭제)

```python
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Dict[int, dict] = Depends(get_todo_storage)
):
    """TODO 삭제"""
    get_todo_by_id(todo_id, db)  # 존재 여부 확인
    del db[todo_id]
    return None
```

**라인별 분석:**

```python
status_code=status.HTTP_204_NO_CONTENT
# - 성공 시 상태 코드: 204
# - 204 = "성공했지만 응답 바디 없음"

get_todo_by_id(todo_id, db)
# - 존재하지 않으면 HTTPException 발생 (404)
# - 반환값은 사용하지 않음 (존재 확인용)

del db[todo_id]
# - fake_db에서 해당 ID 삭제

return None
# - 204 응답 시 바디는 무시됨
# - None 또는 아무것도 반환 안 해도 됨
```

**요청/응답:**

```bash
# 요청
DELETE /todos/1

# 처리
1. todo_id = 1
2. get_todo_by_id(1, db)
   - 존재 → 통과
   - 없으면 → 404 에러
3. del fake_db[1]
4. return None

# 응답
HTTP 204 No Content
(바디 없음)
```

---

## 4. main.py - 메인 애플리케이션

### 코드 분석

#### FastAPI 앱 생성

```python
app = FastAPI(
    title="TODO API",
    description="FastAPI로 만든 간단한 TODO 관리 API",
    version="1.0.0",
)
```

**효과:**

이 메타데이터는 자동 문서(`/docs`)에 표시됩니다.

```
Swagger UI 상단에:
┌─────────────────────────────┐
│ TODO API                    │
│ FastAPI로 만든 간단한...    │
│ Version: 1.0.0              │
└─────────────────────────────┘
```

---

#### 라우터 등록

```python
app.include_router(todos.router)
```

**역할:**

```python
# todos.router에 정의된 모든 엔드포인트를 app에 추가
# 결과:
# - GET  /todos/
# - GET  /todos/{todo_id}
# - POST /todos/
# - PUT  /todos/{todo_id}
# - DELETE /todos/{todo_id}
```

**여러 라우터 등록 예시:**

```python
app.include_router(todos.router)
app.include_router(users.router, prefix="/users")
app.include_router(auth.router, prefix="/auth")

# 결과:
# - /todos/...
# - /users/...
# - /auth/...
```

---

#### 루트 엔드포인트

```python
@app.get("/")
def root():
    """루트 엔드포인트"""
    return {
        "message": "TODO API에 오신 것을 환영합니다!",
        "docs": "/docs",
        "version": "1.0.0"
    }
```

**용도:**

1. API가 정상 작동하는지 확인
2. 문서 경로 안내
3. 버전 정보 제공

---

#### 헬스 체크

```python
@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}
```

**실제 사용:**

```python
# 로드 밸런서, 모니터링 도구가 주기적으로 호출
GET /health

# 응답이 200이면 서버 정상
# 응답이 없거나 500이면 서버 비정상
```

**확장 예시:**

```python
@app.get("/health")
def health_check(db = Depends(get_db)):
    try:
        # DB 연결 확인
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}
```

---

## 전체 요청 흐름 정리

### POST /todos/ 요청 시

```
1. 클라이언트
   POST /todos/
   {"title": "공부하기"}

2. uvicorn (ASGI 서버)
   - HTTP 요청 수신
   - FastAPI 앱으로 전달

3. FastAPI
   - 경로 매칭: /todos/ → create_todo 함수
   - JSON 파싱: {"title": "공부하기"}

4. Pydantic 검증
   - TodoCreate 모델로 검증
   - 타입 체크, 길이 체크
   - 성공 → TodoCreate 객체 생성
   - 실패 → 422 응답

5. Dependency Injection
   - Depends(get_todo_storage) 실행
   - fake_db 반환

6. create_todo 실행
   - new_id = get_next_id() → 1
   - new_todo = {"id": 1, "title": "공부하기", ...}
   - fake_db[1] = new_todo
   - return new_todo

7. Response 검증
   - TodoResponse 모델로 검증
   - dict → JSON 변환

8. uvicorn
   - HTTP 201 응답 생성
   - JSON 전송

9. 클라이언트
   - {"id": 1, "title": "공부하기", ...} 수신
```

---

## 다음 단계

이 코드를 완전히 이해했다면:

1. ✅ **실제 DB 연결**
   - SQLAlchemy로 PostgreSQL 연결
   - `fake_db` 대신 실제 DB 사용

2. ✅ **비동기 처리**
   - `async def`로 변경
   - `await`로 DB 호출

3. ✅ **인증/인가**
   - JWT 토큰 기반 인증
   - `Depends(get_current_user)`

4. ✅ **테스트 작성**
   - pytest로 단위 테스트
   - httpx로 통합 테스트

---

## 참고: 주요 개념 정리

### Pydantic 모델

```python
class TodoCreate(BaseModel):
    title: str = Field(...)
```
- 자동 타입 검증
- 자동 문서 생성
- IDE 자동완성

### Dependency Injection

```python
def endpoint(db = Depends(get_db)):
    pass
```
- 재사용 가능한 로직
- 테스트 용이
- 느슨한 결합

### FastAPI 데코레이터

```python
@app.get("/", response_model=Model)
```
- HTTP 메서드 지정
- 경로 지정
- 응답 모델 지정
- 자동 문서 생성

### 상태 코드

- `200`: 성공 (기본)
- `201`: 생성 성공
- `204`: 성공 (바디 없음)
- `400`: 잘못된 요청
- `404`: 찾을 수 없음
- `422`: 검증 실패
- `500`: 서버 에러
