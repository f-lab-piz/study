# 3주차: 테스트 - 코드를 믿을 수 있게 만들기

## 핵심 목표

- pytest로 유닛 테스트 / 통합 테스트 작성
- 테스트 격리 전략 이해 (SQLite 인메모리 DB)
- Locust로 부하 테스트 실행 및 결과 해석

---

## 1. 왜 테스트가 필요한가?

### 테스트 없는 개발의 문제점

```
개발자: "기능 추가 완료! 잘 되는 것 같은데?"
         ↓
1주일 후: "이전에 되던 기능이 안 돼요" (회귀 버그)
         ↓
3시간 디버깅...
```

**회귀 버그(Regression Bug):**
- 새 코드가 기존 기능을 망가뜨리는 버그
- 수동 테스트로는 발견하기 어려움
- **자동화된 테스트**가 있으면 즉시 감지 가능

### 테스트의 종류 - 테스트 피라미드

```
        /\
       /  \
      / E2E \         ← 느리고 비쌈 (브라우저 테스트)
     /--------\
    /  통합     \      ← HTTP API 레벨 테스트
   /--------------\
  /    유닛         \   ← 빠르고 많이 작성 (함수/클래스 단위)
 /--------------------\
```

| 종류 | 대상 | 속도 | 개수 |
|------|------|------|------|
| **유닛 테스트** | 함수, 클래스, 모델 | 빠름 (ms) | 많이 |
| **통합 테스트** | API 엔드포인트, DB 연동 | 보통 (ms~s) | 적당히 |
| **E2E 테스트** | 전체 시스템 (UI → API → DB) | 느림 (s~min) | 조금만 |

> **이번 주에 배울 것**: 유닛 테스트 + 통합 테스트 (pytest)

---

## 2. pytest 기초

### pytest란?

Python의 **테스트 프레임워크**. 표준 라이브러리의 `unittest`보다 간결하고 강력.

```python
# unittest (표준)
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)

# pytest (우리가 사용할 것)
def test_add():
    assert 1 + 1 == 2  # 훨씬 간결!
```

### AAA 패턴 (Arrange-Act-Assert)

테스트 작성의 기본 구조:

```python
def test_user_create():
    # Arrange (준비): 테스트에 필요한 데이터 준비
    data = {"name": "김철수", "email": "kim@example.com"}

    # Act (실행): 테스트할 코드 실행
    user = UserCreate(**data)

    # Assert (검증): 결과가 기대와 일치하는지 확인
    assert user.name == "김철수"
    assert user.email == "kim@example.com"
```

### assert 다양한 활용

```python
# 값 비교
assert result == expected
assert result != wrong_value

# 타입 확인
assert isinstance(user.id, int)

# 포함 확인
assert "에러" in error_message
assert user_id in user_ids_list

# None 확인
assert user is not None
assert deleted_user is None

# 길이 확인
assert len(users) == 3

# 예외 발생 확인 (가장 중요!)
with pytest.raises(ValidationError):
    UserCreate()  # 필수 필드 없이 생성 → 에러 발생해야 함
```

### 픽스처(Fixture) - 테스트의 재료 준비

**비유**: 요리 시작 전에 재료를 미리 준비하는 것

```python
import pytest

@pytest.fixture
def sample_user_data():
    """여러 테스트에서 재사용할 데이터"""
    return {"name": "김철수", "email": "kim@example.com"}

# 함수 인자로 받으면 자동 주입!
def test_create(sample_user_data):
    user = UserCreate(**sample_user_data)
    assert user.name == "김철수"

def test_email(sample_user_data):
    assert "@" in sample_user_data["email"]
```

**fixture scope (범위):**

| scope | 의미 | 실행 횟수 |
|-------|------|----------|
| `function` (기본) | 매 테스트 함수마다 | 가장 많이 (안전) |
| `class` | 테스트 클래스당 한 번 | |
| `module` | 파일(모듈)당 한 번 | |
| `session` | 전체 테스트 실행당 한 번 | 가장 적게 (빠름) |

> **우리는 `function` scope 사용** → 매 테스트마다 새 DB → 완벽한 격리

**conftest.py란?**

```
tests/
├── conftest.py          ← 이 파일의 fixture는 같은 디렉토리의
├── test_unit.py             모든 테스트 파일에서 사용 가능!
└── test_integration.py
```

- `conftest.py`에 정의한 fixture는 import 없이 자동으로 사용 가능
- 테스트 전체에서 공유할 설정이나 데이터를 여기에 정의

### 마커(Markers)

#### @pytest.mark.parametrize - 여러 입력으로 테스트

```python
@pytest.mark.parametrize(
    "name, email, expected",
    [
        ("김철수", "kim@test.com", True),
        ("이영희", "lee@test.com", True),
        ("", "empty@test.com", True),      # 빈 이름도 통과? (의도적 확인)
    ],
)
def test_user_create_parametrize(name, email, expected):
    user = UserCreate(name=name, email=email)
    assert (user is not None) == expected
```

→ 하나의 테스트 함수로 **3개의 테스트 케이스** 실행!

#### 기타 유용한 마커

```python
@pytest.mark.skip(reason="아직 미구현")
def test_not_ready():
    pass

@pytest.mark.xfail(reason="알려진 버그, 수정 예정")
def test_known_bug():
    assert 1 == 2  # 실패해도 OK

@pytest.mark.slow
def test_performance():
    # 느린 테스트에 마킹 → pytest -m "not slow" 로 제외 가능
    pass
```

### 코드 커버리지

**코드의 몇 %가 테스트로 실행되는지** 측정:

```bash
# 커버리지 리포트 생성
uv run pytest --cov=app --cov-report=term-missing

# 결과 예시:
# Name                 Stmts   Miss  Cover   Missing
# --------------------------------------------------
# app/database.py         15      2    87%   12, 15
# app/main.py             55      8    85%   88-95
# app/models.py           12      0   100%
# --------------------------------------------------
# TOTAL                   82     10    88%
```

| 항목 | 의미 |
|------|------|
| Stmts | 전체 코드 줄 수 |
| Miss | 테스트에서 실행되지 않은 줄 수 |
| Cover | 커버리지 비율 |
| Missing | 테스트되지 않은 줄 번호 |

> **목표**: 80% 이상이면 양호. 100%가 목표가 아님 (비용 대비 효과 고려)

---

## 3. 테스트 격리 전략

### 왜 PostgreSQL 대신 SQLite를 쓰는가?

```
실제 서비스:  FastAPI ←→ PostgreSQL (Docker)
테스트:      FastAPI ←→ SQLite (인메모리)  ← 이걸 사용!
```

| 비교 | PostgreSQL | SQLite 인메모리 |
|------|-----------|----------------|
| 설치 | Docker 필요 | 불필요 (Python 내장) |
| 속도 | 느림 (디스크 I/O) | 빠름 (메모리) |
| 격리 | 데이터 정리 필요 | 자동 (메모리 해제) |
| CI/CD | Docker 설정 필요 | 바로 실행 가능 |

**핵심**: 테스트에서는 "DB 동작이 올바른지"가 중요하지, "어떤 DB를 쓰는지"는 중요하지 않다.

### 의존성 오버라이드 패턴

```
실제 흐름:
  클라이언트 → FastAPI → get_db() → PostgreSQL 세션 → 응답

테스트 흐름:
  TestClient → FastAPI → override_get_db() → SQLite 세션 → 응답
                          ↑
                    dependency_overrides로 교체!
```

```python
# conftest.py에서의 핵심 코드

# 1. 테스트용 SQLite 엔진 생성
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)

# 2. 테스트용 세션 생성
TestingSession = sessionmaker(bind=engine)
test_db = TestingSession()

# 3. FastAPI의 get_db를 테스트 버전으로 교체!
def override_get_db():
    yield test_db

app.dependency_overrides[get_db] = override_get_db
```

### TestClient 사용법

```python
from fastapi.testclient import TestClient
from app.main import app

# 실제 서버를 띄우지 않고 HTTP 요청 테스트!
client = TestClient(app)

# GET 요청
response = client.get("/users")
assert response.status_code == 200

# POST 요청 (JSON body)
response = client.post("/users", json={"name": "김철수", "email": "kim@test.com"})
assert response.status_code == 201

# 응답 body 확인
data = response.json()
assert data["name"] == "김철수"
```

**TestClient vs 실제 HTTP:**

| 항목 | TestClient | 실제 HTTP (curl, httpx) |
|------|-----------|----------------------|
| 서버 필요 | 불필요 | 필요 (uvicorn 실행) |
| 속도 | 매우 빠름 | 느림 (네트워크) |
| 용도 | 자동화 테스트 | 수동 테스트, 부하 테스트 |

---

## 4. 유닛 테스트 작성

### 4.1 Pydantic 모델 테스트

DB 없이 **입력 유효성 검증**만 테스트:

```python
from pydantic import ValidationError
from app.main import UserCreate

class TestPydanticSchemas:

    def test_user_create_valid(self):
        """정상 데이터로 생성"""
        user = UserCreate(name="김철수", email="kim@example.com")
        assert user.name == "김철수"

    def test_user_create_name_required(self):
        """name 없으면 에러"""
        with pytest.raises(ValidationError):
            UserCreate(email="kim@example.com")
```

### 4.2 SQLAlchemy ORM 테스트

`test_db` 픽스처로 **DB 직접 조작** 테스트:

```python
from sqlalchemy.exc import IntegrityError
from app.models import User

class TestSQLAlchemyORM:

    def test_create_user_in_db(self, test_db):
        """유저 생성 후 ID 자동 할당"""
        user = User(name="김철수", email="kim@example.com")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.id > 0

    def test_email_uniqueness(self, test_db):
        """이메일 중복 시 IntegrityError"""
        user1 = User(name="김철수", email="same@example.com")
        test_db.add(user1)
        test_db.commit()

        user2 = User(name="이영희", email="same@example.com")
        test_db.add(user2)

        with pytest.raises(IntegrityError):
            test_db.commit()

        test_db.rollback()  # 에러 후 세션 정리
```

### 4.3 @pytest.mark.parametrize 실전

한 함수로 여러 케이스를 한 번에 테스트:

```python
@pytest.mark.parametrize(
    "name, email, should_succeed",
    [
        ("김철수", "kim@example.com", True),
        ("a" * 100, "max@example.com", True),      # 이름 100자
        ("A", "short@example.com", True),           # 이름 1자
        ("홍길동 Jr.", "hong.jr@example.com", True), # 특수문자
    ],
)
def test_user_create_various(name, email, should_succeed):
    if should_succeed:
        user = UserCreate(name=name, email=email)
        assert user.name == name
```

---

## 5. 통합 테스트 작성

### 5.1 HTTP API 테스트 구조

```python
class TestCreateUser:
    """POST /users 테스트"""

    def test_create_success(self, client, sample_user_data):
        response = client.post("/users", json=sample_user_data)

        assert response.status_code == 201      # HTTP 상태 코드
        data = response.json()                    # 응답 body
        assert data["name"] == "김철수"           # 필드 값 검증
        assert "id" in data                       # ID 존재 여부
```

### 5.2 CRUD 시나리오별 테스트

**Create (POST):**
```python
def test_create_duplicate_email(self, client, sample_user_data):
    """이메일 중복 → 400"""
    client.post("/users", json=sample_user_data)  # 첫 번째: 성공
    response = client.post("/users", json=sample_user_data)  # 두 번째: 실패

    assert response.status_code == 400
    assert "이미 존재하는 이메일" in response.json()["detail"]
```

**Read (GET):**
```python
def test_get_user_not_found(self, client):
    """없는 ID → 404"""
    response = client.get("/users/99999")
    assert response.status_code == 404
```

**Update (PUT):**
```python
def test_update_name_only(self, client, sample_user_in_db):
    """이름만 수정 → 이메일 유지"""
    response = client.put(
        f"/users/{sample_user_in_db.id}",
        json={"name": "새이름"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "새이름"
    assert response.json()["email"] == sample_user_in_db.email
```

**Delete (DELETE):**
```python
def test_delete_then_verify(self, client, sample_user_in_db):
    """삭제 후 조회 → 404"""
    client.delete(f"/users/{sample_user_in_db.id}")

    response = client.get(f"/users/{sample_user_in_db.id}")
    assert response.status_code == 404
```

### 5.3 전체 워크플로우 테스트

```python
def test_complete_lifecycle(self, client):
    """생성 → 조회 → 수정 → 삭제 → 확인"""

    # 1. 생성
    res = client.post("/users", json={"name": "김철수", "email": "kim@test.com"})
    user_id = res.json()["id"]

    # 2. 조회
    res = client.get(f"/users/{user_id}")
    assert res.json()["name"] == "김철수"

    # 3. 수정
    res = client.put(f"/users/{user_id}", json={"name": "김영희"})
    assert res.json()["name"] == "김영희"

    # 4. 삭제
    res = client.delete(f"/users/{user_id}")
    assert res.status_code == 200

    # 5. 확인
    res = client.get(f"/users/{user_id}")
    assert res.status_code == 404
```

---

## 6. 실습: 직접 테스트 작성해보기

### 6.1 환경 설정

```bash
cd backend/week3

# 의존성 설치
uv sync

# 테스트 실행
uv run pytest

# 상세 출력
uv run pytest -v

# 특정 파일만 실행
uv run pytest tests/test_unit_users.py

# 특정 테스트만 실행
uv run pytest tests/test_unit_users.py::TestPydanticSchemas::test_user_create_valid

# 커버리지 포함
uv run pytest --cov=app --cov-report=term-missing
```

### 6.2 실습 과제 목록

코드에 `TODO`로 표시된 스텁을 완성하세요:

#### 유닛 테스트 (`tests/test_unit_users.py`)

| 난이도 | 테스트 | 힌트 |
|--------|--------|------|
| ⭐ | `test_user_update_all_optional` | `UserUpdate()` 빈 인자 생성 |
| ⭐ | `test_user_update_partial_name` | `UserUpdate(name="x")` |
| ⭐⭐ | `test_update_user_name` | ORM 객체 속성 변경 + commit |
| ⭐⭐ | `test_delete_user_from_db` | `test_db.delete()` + commit |
| ⭐⭐ | `test_query_all_users` | `add_all()` + `.all()` 길이 확인 |
| ⭐⭐ | `test_create_multiple_users_in_db` | parametrize + DB 생성 |

#### 통합 테스트 (`tests/test_integration_users.py`)

| 난이도 | 테스트 | 힌트 |
|--------|--------|------|
| ⭐ | `test_create_user_extra_fields_ignored` | 추가 필드 포함 POST |
| ⭐ | `test_delete_user_not_found` | DELETE /users/99999 |
| ⭐⭐ | `test_update_user_own_email` | 자기 이메일로 PUT |
| ⭐⭐⭐ | `test_pagination_skip_limit` | 10명 생성 + skip/limit |
| ⭐⭐⭐ | `test_bulk_user_operations` | 5명 생성 + 2명 삭제 + 통계 확인 |

#### conftest.py 픽스처

| 난이도 | 픽스처 | 힌트 |
|--------|--------|------|
| ⭐⭐ | `multiple_users_in_db` | 5~10명 유저 리스트 생성 |

---

## 7. Locust 부하 테스트

### 7.1 기능 테스트 vs 성능 테스트

```
기능 테스트 (pytest):
  "이 API가 올바르게 동작하는가?"
  → 1명의 사용자, 1번의 요청

성능 테스트 (Locust):
  "이 API가 100명이 동시에 쓰면 어떻게 되는가?"
  → N명의 사용자, 지속적인 요청
```

### 7.2 부하 테스트 종류

| 종류 | 목적 | 비유 |
|------|------|------|
| **부하 테스트** | 정상 트래픽에서 성능 측정 | 평일 출퇴근 교통량 |
| **스트레스 테스트** | 시스템 한계 파악 | 명절 고속도로 정체 |
| **스파이크 테스트** | 갑작스런 트래픽 대응 | 한정 판매 시작 순간 |
| **내구성 테스트** | 장시간 운영 시 안정성 | 24시간 운영 모니터링 |

### 7.3 Locust 핵심 개념

```python
from locust import HttpUser, task, between

class MyUser(HttpUser):
    # 1. 요청 사이 대기 시간
    wait_time = between(1, 3)  # 1~3초 랜덤 대기

    # 2. 시작 시 실행 (로그인, 초기화 등)
    def on_start(self):
        self.client.get("/health")

    # 3. 반복 실행할 태스크
    @task(3)  # 가중치 3 (다른 태스크 대비 3배 자주 실행)
    def list_users(self):
        self.client.get("/users")

    @task(1)  # 가중치 1
    def create_user(self):
        self.client.post("/users", json={...})
```

**@task 가중치:**

```
@task(3) list_users   → 3/(3+1) = 75% 확률로 실행
@task(1) create_user  → 1/(3+1) = 25% 확률로 실행
```

**catch_response 패턴:**

```python
with self.client.get("/users", catch_response=True) as response:
    if response.status_code == 200:
        response.success()       # Locust에 "성공"으로 기록
    else:
        response.failure("실패!")  # Locust에 "실패"로 기록
```

### 7.4 Locust 실행 방법

**사전 준비 (터미널 2개 필요):**

```bash
# 터미널 1: week2 서버 실행
cd backend/week2
docker compose up -d       # PostgreSQL 시작
uv run uvicorn main:app --reload --host 0.0.0.0

# 터미널 2: Locust 실행
cd backend/week3
uv run locust
```

**브라우저에서 접속:**

```
http://localhost:8089

┌──────────────────────────────────────┐
│  Locust - New Test                    │
│                                       │
│  Host: http://localhost:8000          │ ← week2 서버 주소
│  Number of users: 10                  │ ← 동시 사용자 수
│  Spawn rate: 2                        │ ← 초당 생성할 사용자 수
│                                       │
│  [Start swarming]                     │
└──────────────────────────────────────┘
```

### 7.5 결과 해석

```
┌─────────────────────────────────────────────────────────┐
│ Type   Name                    # Reqs  Avg   P95   P99  │
├─────────────────────────────────────────────────────────┤
│ GET    /users [GET - List]      150    12ms  25ms  45ms │
│ POST   /users [POST - Create]   52    18ms  35ms  60ms │
│ GET    /users/{id} [Detail]    105    10ms  20ms  40ms │
│ GET    /stats [GET]              48     8ms  15ms  30ms │
├─────────────────────────────────────────────────────────┤
│        Total                    355    12ms  25ms  50ms │
│        RPS: 23.5                                        │
│        Failures: 0 (0.00%)                              │
└─────────────────────────────────────────────────────────┘
```

**주요 메트릭:**

| 메트릭 | 의미 | 좋은 기준 |
|--------|------|----------|
| **Avg** | 평균 응답 시간 | < 100ms |
| **P95** | 95%의 요청이 이 시간 내 완료 | < 200ms |
| **P99** | 99%의 요청이 이 시간 내 완료 | < 500ms |
| **RPS** | 초당 처리 요청 수 | 높을수록 좋음 |
| **Failures** | 에러 비율 | < 1% |

> **P95 vs 평균**: 평균이 좋아도 P95가 나쁘면 일부 사용자가 느린 것.
> 실무에서는 **P95, P99**를 더 중요하게 봄.

### 7.6 테스트 시나리오 설명

**UserCRUDUser (메인 시나리오):**

| 태스크 | 가중치 | 비율 | 설명 |
|--------|--------|------|------|
| `list_users` | 3 | ~33% | 유저 리스트 조회 (가장 빈번) |
| `get_single_user` | 2 | ~22% | 단건 조회 |
| `create_user` | 1 | ~11% | 유저 생성 |
| `update_user` | 1 | ~11% | 유저 수정 (TODO) |
| `delete_user` | 1 | ~11% | 유저 삭제 (TODO) |
| `get_stats` | 1 | ~11% | 통계 조회 |

→ 읽기(조회) 비중이 높은 **실제 서비스 패턴**을 반영

### 7.7 Locust 실습 과제

`locustfile.py`의 TODO를 완성하세요:

| 난이도 | 과제 | 힌트 |
|--------|------|------|
| ⭐⭐ | `update_user` 메서드 | PUT 요청 + catch_response |
| ⭐⭐ | `delete_user` 메서드 | DELETE 요청 + ID 리스트 관리 |
| ⭐⭐⭐ | `MixedWorkloadUser.complete_workflow` | 생성→조회→수정→삭제 순차 실행 |
| ⭐⭐⭐ | `StressTestUser` 클래스 | wait_time 최소화 + 대량 생성 |

---

## 8. 테스트 모범 사례

### 명명 규칙

```python
# 좋은 예: 무엇을 테스트하는지 명확
def test_create_user_with_duplicate_email_returns_400():
    ...

# 나쁜 예: 의미 불명확
def test_user_1():
    ...
```

### 한 테스트 = 한 가지 검증

```python
# 좋은 예: 하나만 검증
def test_create_user_returns_201(self, client):
    response = client.post("/users", json=data)
    assert response.status_code == 201

def test_create_user_returns_correct_name(self, client):
    response = client.post("/users", json=data)
    assert response.json()["name"] == "김철수"

# 나쁜 예: 여러 가지를 한 번에 (실패 시 원인 파악 어려움)
# → 하지만 실무에서는 적절히 묶는 것도 OK
```

### 테스트 독립성

```python
# 좋은 예: 각 테스트가 독립적 (fixture로 데이터 준비)
def test_get_user(self, client, sample_user_in_db):
    response = client.get(f"/users/{sample_user_in_db.id}")
    assert response.status_code == 200

# 나쁜 예: 다른 테스트에서 만든 데이터에 의존
# → test_create가 먼저 실행되어야 test_get이 성공 (순서 의존)
```

---

## 9. 정리

오늘 배운 것:

- [x] pytest로 유닛 테스트 작성 (Pydantic, SQLAlchemy)
- [x] TestClient로 통합 테스트 작성 (HTTP API)
- [x] SQLite 인메모리 DB로 테스트 격리
- [x] dependency_overrides로 의존성 교체
- [x] @pytest.mark.parametrize로 다양한 케이스 테스트
- [x] Locust로 부하 테스트 실행 및 결과 해석

**핵심 변화:**
```
Week1: dict (메모리)    → Week2: PostgreSQL (디스크) → Week3: 테스트 (품질 보장)
→ 코드가 올바르게 동작한다는 것을 자동으로 검증!
```

---

## 참고 명령어 모음

```bash
# pytest 실행
uv run pytest                              # 전체 테스트
uv run pytest -v                           # 상세 출력
uv run pytest -x                           # 첫 실패에서 중단
uv run pytest tests/test_unit_users.py     # 특정 파일
uv run pytest -k "test_create"             # 이름 필터
uv run pytest --cov=app                    # 커버리지

# Locust 실행
uv run locust                              # 웹 UI 모드
uv run locust --headless -u 10 -r 2 -t 60s  # 헤드리스 모드 (60초)
```
