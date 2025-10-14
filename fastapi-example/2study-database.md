# 데이터베이스 연동 학습 가이드 (PostgreSQL + SQLAlchemy)

## 목차
1. [데이터베이스가 필요한 이유](#데이터베이스가-필요한-이유)
2. [PostgreSQL이란?](#postgresql이란)
3. [ORM과 SQLAlchemy](#orm과-sqlalchemy)
4. [핵심 개념](#핵심-개념)
5. [프로젝트 구조](#프로젝트-구조)
6. [단계별 구현](#단계별-구현)
7. [실습: TODO API에 DB 연동](#실습-todo-api에-db-연동)
8. [트러블슈팅](#트러블슈팅)

---

## 데이터베이스가 필요한 이유

### 메모리 저장소의 한계

```python
# ❌ 메모리 저장소 (이전 방식)
fake_db = {}  # 딕셔너리에 저장

문제점:
1. 서버 재시작 시 데이터 손실 💥
2. 동시성 문제 (여러 요청 처리 시)
3. 대용량 데이터 처리 불가
4. 검색/정렬 성능 저하
5. 데이터 무결성 보장 어려움
```

### 데이터베이스 사용의 장점

```python
# ✅ 데이터베이스 (새로운 방식)
PostgreSQL + SQLAlchemy

장점:
1. 영속성: 서버 재시작해도 데이터 유지 ✨
2. 트랜잭션: 데이터 일관성 보장
3. 인덱싱: 빠른 검색 성능
4. 동시성: 여러 사용자 동시 접근
5. 백업/복구: 데이터 보호
```

---

## PostgreSQL이란?

### 개요

**PostgreSQL**은 오픈소스 관계형 데이터베이스 관리 시스템(RDBMS)입니다.

### 특징

- **오픈소스**: 무료, 커뮤니티 활발
- **표준 준수**: SQL 표준을 잘 따름
- **확장성**: 다양한 플러그인과 확장 기능
- **안정성**: 데이터 무결성과 안정성 보장
- **풍부한 기능**: JSON, 전문검색, GIS 등 지원

### 다른 데이터베이스와 비교

| 특성 | PostgreSQL | MySQL | SQLite |
|------|-----------|-------|--------|
| 타입 | 관계형 | 관계형 | 관계형 (파일) |
| 동시성 | 우수 | 좋음 | 제한적 |
| 기능 | 매우 풍부 | 풍부 | 기본적 |
| 복잡도 | 중간 | 중간 | 낮음 |
| 사용 사례 | 프로덕션 앱 | 웹 앱 | 소규모/테스트 |

---

## ORM과 SQLAlchemy

### ORM이란?

**ORM (Object-Relational Mapping)**은 객체와 데이터베이스 테이블을 매핑하는 기술입니다.

```python
# SQL 직접 작성 (ORM 없이)
cursor.execute("SELECT * FROM todos WHERE id = ?", (1,))

# ORM 사용 (SQLAlchemy)
db.query(TodoDB).filter(TodoDB.id == 1).first()
```

### ORM의 장점

1. **생산성 향상**: SQL 대신 Python 코드 작성
2. **데이터베이스 독립성**: PostgreSQL ↔ MySQL 쉽게 전환
3. **타입 안정성**: IDE 자동완성, 타입 체크
4. **유지보수성**: 코드 가독성 향상
5. **SQL 인젝션 방지**: 자동으로 쿼리 이스케이핑

### SQLAlchemy란?

Python에서 가장 인기 있는 ORM 라이브러리입니다.

**주요 기능:**
- ORM (객체-관계 매핑)
- Connection Pool (연결 풀 관리)
- Transaction Management (트랜잭션 관리)
- Query Builder (쿼리 빌더)

---

## 핵심 개념

### 1. 데이터베이스 엔진 (Engine)

데이터베이스와의 연결을 관리하는 객체

```python
from sqlalchemy import create_engine

# PostgreSQL 연결 문자열
# postgresql://사용자:비밀번호@호스트:포트/데이터베이스명
DATABASE_URL = "postgresql://postgres:postgres@db:5432/todoapp"

# 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)
```

### 2. 세션 (Session)

데이터베이스와의 대화 단위

```python
from sqlalchemy.orm import sessionmaker

# 세션 팩토리 생성
SessionLocal = sessionmaker(bind=engine)

# 세션 사용
session = SessionLocal()
try:
    # DB 작업
    session.add(todo)
    session.commit()
finally:
    session.close()
```

### 3. 모델 (Model)

데이터베이스 테이블을 Python 클래스로 표현

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TodoDB(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    completed = Column(Boolean, default=False)
```

### 4. Pydantic vs SQLAlchemy 모델

```
┌─────────────────────────────────────────────┐
│          HTTP Request (JSON)                │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Pydantic Model │  ← 데이터 검증
         │  (TodoCreate)  │
         └────────┬───────┘
                  │
                  ▼
      ┌──────────────────────┐
      │ SQLAlchemy Model     │  ← DB 테이블 매핑
      │    (TodoDB)          │
      └──────────┬───────────┘
                  │
                  ▼
         ┌────────────────┐
         │   PostgreSQL   │  ← 실제 저장
         └────────────────┘
```

**역할 분리:**
- **Pydantic**: API 입출력 검증 (HTTP 계층)
- **SQLAlchemy**: DB 테이블 매핑 (DB 계층)

---

## 프로젝트 구조

```
fastapi-example/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 + 생명주기 관리
│   ├── database.py          # ✨ DB 연결 설정
│   ├── init_db.py           # ✨ DB 초기화
│   ├── models.py            # ✨ Pydantic + SQLAlchemy 모델
│   ├── dependencies.py      # ✨ DB 세션 의존성
│   └── routers/
│       └── todos.py         # ✨ DB 사용하도록 수정
├── docker-compose.yml       # ✨ PostgreSQL 추가
├── pyproject.toml           # ✨ DB 의존성 추가
└── README.md
```

---

## 단계별 구현

### 1단계: 의존성 추가

**파일**: `pyproject.toml`

```toml
dependencies = [
    "fastapi>=0.115.6",
    "uvicorn[standard]>=0.34.0",
    "sqlalchemy>=2.0.0",      # ✨ ORM
    "psycopg2-binary>=2.9.9", # ✨ PostgreSQL 드라이버
]
```

### 2단계: 데이터베이스 연결 설정

**파일**: `app/database.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 환경 변수에서 DB URL 가져오기
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/todoapp"
)

# 엔진 생성
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스
Base = declarative_base()

# 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**핵심 포인트:**
- `echo=True`: SQL 쿼리 로깅 (개발 시 유용)
- `pool_pre_ping=True`: 연결 유효성 자동 확인
- `get_db()`: FastAPI의 Depends()와 함께 사용

### 3단계: SQLAlchemy 모델 정의

**파일**: `app/models.py`

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .database import Base

class TodoDB(Base):
    """SQLAlchemy ORM 모델"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(String(500))
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**칼럼 옵션:**
- `primary_key=True`: 기본 키
- `index=True`: 인덱스 생성 (검색 속도 향상)
- `nullable=False`: NOT NULL 제약조건
- `default`: 기본값
- `onupdate`: 업데이트 시 자동 실행

### 4단계: Pydantic 스키마 수정

**파일**: `app/models.py` (계속)

```python
from pydantic import BaseModel, ConfigDict

class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # Pydantic v2: ORM 모드 활성화
    model_config = ConfigDict(from_attributes=True)
```

**`from_attributes=True`의 역할:**
- SQLAlchemy 객체 → Pydantic 객체 자동 변환
- `TodoDB` → `TodoResponse` 변환 가능

### 5단계: 라우터를 DB 사용하도록 수정

**파일**: `app/routers/todos.py`

```python
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TodoDB

@router.post("/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    # Pydantic → SQLAlchemy 변환
    db_todo = TodoDB(**todo.model_dump())

    # DB에 추가
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)  # DB에서 생성된 값 가져오기

    return db_todo  # SQLAlchemy → Pydantic 자동 변환
```

**주요 메서드:**
- `db.add()`: 객체를 세션에 추가
- `db.commit()`: 변경사항 커밋
- `db.refresh()`: DB에서 최신 값 가져오기
- `db.query()`: 쿼리 시작
- `db.delete()`: 객체 삭제

### 6단계: Docker Compose에 PostgreSQL 추가

**파일**: `docker-compose.yml`

```yaml
services:
  # PostgreSQL 데이터베이스
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: todoapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s

  # FastAPI 앱
  fastapi-app:
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/todoapp
    depends_on:
      db:
        condition: service_healthy  # DB 준비될 때까지 대기

volumes:
  postgres_data:  # 데이터 영속성
```

### 7단계: DB 초기화

**파일**: `app/init_db.py`

```python
from .database import engine, Base
from .models import TodoDB

def init_db():
    """테이블 생성"""
    Base.metadata.create_all(bind=engine)
```

**파일**: `app/main.py`

```python
from contextlib import asynccontextmanager
from app.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: DB 초기화
    init_db()
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)
```

---

## 실습: TODO API에 DB 연동

### 1. 전체 스택 실행

```bash
# 1. 프로젝트 디렉토리로 이동
cd fastapi-example

# 2. Docker Compose로 실행 (PostgreSQL + FastAPI)
docker-compose up --build

# 로그 확인
# - PostgreSQL이 먼저 시작됨
# - FastAPI가 DB에 연결
# - 테이블 자동 생성 (init_db)
```

### 2. API 문서 확인

브라우저에서 http://localhost:8000/docs 접속

**변경사항 확인:**
- `TodoResponse`에 `created_at`, `updated_at` 필드 추가
- `GET /todos/`에 `skip`, `limit` 파라미터 추가 (페이지네이션)

### 3. TODO 생성 테스트

```bash
curl -X POST http://localhost:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "PostgreSQL 학습하기",
    "description": "SQLAlchemy로 DB 연동",
    "completed": false
  }'

# 응답 예시
{
  "id": 1,
  "title": "PostgreSQL 학습하기",
  "description": "SQLAlchemy로 DB 연동",
  "completed": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 4. 데이터 영속성 테스트

```bash
# 1. TODO 몇 개 생성
curl -X POST http://localhost:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "테스트 1"}'

curl -X POST http://localhost:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "테스트 2"}'

# 2. 컨테이너 재시작
docker-compose restart fastapi-app

# 3. 데이터 확인 (데이터가 남아있음!)
curl http://localhost:8000/todos/
```

### 5. PostgreSQL 직접 접속

```bash
# PostgreSQL 컨테이너에 접속
docker exec -it fastapi-postgres psql -U postgres -d todoapp

# SQL 쿼리 실행
todoapp=# SELECT * FROM todos;
todoapp=# \dt  -- 테이블 목록
todoapp=# \d todos  -- todos 테이블 구조
todoapp=# \q  -- 종료
```

### 6. CRUD 전체 테스트

```bash
# CREATE
curl -X POST http://localhost:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "장보기", "description": "우유, 계란"}'

# READ (전체)
curl http://localhost:8000/todos/

# READ (단일)
curl http://localhost:8000/todos/1

# UPDATE
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# DELETE
curl -X DELETE http://localhost:8000/todos/1
```

---

## SQLAlchemy 쿼리 가이드

### 기본 쿼리

```python
# 전체 조회
todos = db.query(TodoDB).all()

# 단일 조회
todo = db.query(TodoDB).filter(TodoDB.id == 1).first()

# 조건 필터링
completed_todos = db.query(TodoDB).filter(TodoDB.completed == True).all()

# 여러 조건 (AND)
from sqlalchemy import and_
todos = db.query(TodoDB).filter(
    and_(
        TodoDB.completed == False,
        TodoDB.title.like("%공부%")
    )
).all()

# 여러 조건 (OR)
from sqlalchemy import or_
todos = db.query(TodoDB).filter(
    or_(
        TodoDB.completed == True,
        TodoDB.title.like("%긴급%")
    )
).all()

# 정렬
todos = db.query(TodoDB).order_by(TodoDB.created_at.desc()).all()

# 페이지네이션
todos = db.query(TodoDB).offset(10).limit(10).all()

# 개수 세기
count = db.query(TodoDB).filter(TodoDB.completed == True).count()
```

### 생성, 수정, 삭제

```python
# 생성
new_todo = TodoDB(title="새 할일", completed=False)
db.add(new_todo)
db.commit()
db.refresh(new_todo)

# 수정
todo = db.query(TodoDB).filter(TodoDB.id == 1).first()
todo.completed = True
db.commit()
db.refresh(todo)

# 삭제
todo = db.query(TodoDB).filter(TodoDB.id == 1).first()
db.delete(todo)
db.commit()
```

---

## 코드 파일별 설명

### `app/database.py` - DB 연결 관리

```python
# 역할: 데이터베이스 연결 설정 및 세션 관리

DATABASE_URL = "postgresql://..."  # 연결 문자열
engine = create_engine(...)        # 엔진 생성
SessionLocal = sessionmaker(...)   # 세션 팩토리
Base = declarative_base()          # 모델 베이스 클래스

def get_db():                      # 세션 의존성
    """FastAPI Depends()와 함께 사용"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `app/models.py` - 데이터 모델

```python
# 역할: DB 테이블 + API 스키마 정의

# SQLAlchemy: DB 테이블 매핑
class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    ...

# Pydantic: API 입출력 검증
class TodoCreate(BaseModel):
    title: str
    ...

class TodoResponse(BaseModel):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### `app/routers/todos.py` - API 엔드포인트

```python
# 역할: HTTP 요청 처리 + DB 작업

@router.post("/")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    # 1. Pydantic 검증 (FastAPI 자동)
    # 2. SQLAlchemy 모델로 변환
    db_todo = TodoDB(**todo.model_dump())
    # 3. DB에 저장
    db.add(db_todo)
    db.commit()
    # 4. 응답 반환 (자동으로 Pydantic 변환)
    return db_todo
```

---

## 트러블슈팅

### 문제 1: DB 연결 실패

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**해결:**
```bash
# 1. PostgreSQL 컨테이너 상태 확인
docker-compose ps

# 2. PostgreSQL 로그 확인
docker-compose logs db

# 3. 네트워크 확인
docker-compose exec fastapi-app ping db

# 4. DB 준비 대기 확인
# docker-compose.yml에 depends_on.condition: service_healthy 확인
```

### 문제 2: 테이블이 생성되지 않음

```
sqlalchemy.exc.ProgrammingError: relation "todos" does not exist
```

**해결:**
```python
# app/init_db.py에서 모델 import 확인
from .models import TodoDB  # ✅ 반드시 import!

# app/main.py의 lifespan에서 init_db() 호출 확인
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # ✅ 호출 확인
    yield
```

### 문제 3: Pydantic 변환 에러

```
pydantic.error_wrappers.ValidationError
```

**해결:**
```python
# TodoResponse에 model_config 추가 확인
class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # ✅ 필수!
```

### 문제 4: 세션 관련 에러

```
sqlalchemy.exc.InvalidRequestError: Object is already attached to session
```

**해결:**
```python
# db.refresh() 사용
db.commit()
db.refresh(db_todo)  # ✅ 변경사항 반영
return db_todo
```

### 문제 5: 포트 충돌

```
Error: Bind for 0.0.0.0:5432 failed: port is already allocated
```

**해결:**
```bash
# 기존 PostgreSQL 중지
sudo service postgresql stop

# 또는 포트 변경 (docker-compose.yml)
ports:
  - "5433:5432"  # 호스트 포트 변경
```

---

## 다음 단계

이 가이드를 완료했다면:

1. ✅ **관계 (Relationships)**
   - 일대다, 다대다 관계 설정
   - `relationship()` 사용법

2. ✅ **트랜잭션**
   - 복잡한 비즈니스 로직
   - Rollback 처리

3. ✅ **성능 최적화**
   - 인덱싱
   - N+1 쿼리 문제 해결
   - 쿼리 최적화

4. ✅ **보안**
   - SQL 인젝션 방지
   - 환경 변수 관리
   - 비밀번호 암호화

---

## 참고 자료

### 공식 문서
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [FastAPI 데이터베이스 가이드](https://fastapi.tiangolo.com/tutorial/sql-databases/)

### 학습 리소스
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

---

## 요약

### 핵심 개념
- **PostgreSQL**: 강력한 오픈소스 관계형 데이터베이스
- **SQLAlchemy**: Python ORM (객체-관계 매핑)
- **세션**: DB와의 대화 단위
- **모델**: 테이블을 Python 클래스로 표현

### 주요 파일
```
app/
├── database.py      # DB 연결 설정
├── init_db.py       # 테이블 초기화
├── models.py        # ORM + Pydantic 모델
└── routers/todos.py # DB 사용하는 API
```

### 주요 명령어
```bash
# Docker Compose로 실행
docker-compose up --build

# PostgreSQL 접속
docker exec -it fastapi-postgres psql -U postgres -d todoapp

# 로그 확인
docker-compose logs -f
```

### 데이터 흐름
```
HTTP Request
    ↓
Pydantic (검증)
    ↓
SQLAlchemy (ORM)
    ↓
PostgreSQL (저장)
    ↓
SQLAlchemy (조회)
    ↓
Pydantic (응답)
    ↓
HTTP Response
```

---

**축하합니다!** 이제 FastAPI 애플리케이션에 PostgreSQL을 연동하는 방법을 배웠습니다. 다음은 인증/인가를 추가해보세요!
