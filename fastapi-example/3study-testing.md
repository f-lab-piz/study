# 테스팅 학습 가이드 (pytest, 유닛/통합 테스트)

## 🚀 빠른 시작 (Quick Start)

```bash
# 1. 프로젝트 디렉토리로 이동
cd fastapi-example

# 2. Docker Compose로 전체 스택 시작
docker-compose up --build -d

# 3. 테스트 실행
docker-compose exec fastapi-app uv run pytest -v

# 4. 커버리지 포함 테스트
docker-compose exec fastapi-app uv run pytest --cov=app --cov-report=term-missing
```

**기대 결과:**
- ✅ 40개 테스트 통과
- 📊 커버리지 약 96%
- ⏱️ 실행 시간 약 1-2초

---

## 📝 실습 과제

이 프로젝트에는 **예시 테스트**와 **TODO 테스트**가 혼합되어 있습니다.

### 과제 진행 방법

1. **예시 테스트 먼저 이해하기**
   - [tests/test_unit_todos.py](tests/test_unit_todos.py)에서 완성된 테스트 확인
   - [tests/test_integration_todos.py](tests/test_integration_todos.py)에서 완성된 테스트 확인
   - 각 테스트가 무엇을 검증하는지 이해하기

2. **TODO 주석 찾기**
   ```bash
   # TODO가 있는 테스트 찾기
   grep -n "TODO:" tests/*.py
   ```

3. **TODO 테스트 하나씩 완성하기**
   - 주석의 힌트를 참고하여 코드 작성
   - 테스트 실행하여 통과 확인
   - 다음 TODO로 진행

4. **커버리지 확인**
   ```bash
   # HTML 리포트 생성
   docker-compose exec fastapi-app uv run pytest --cov=app --cov-report=html

   # htmlcov/index.html 파일을 브라우저에서 열어서 확인
   ```

### 실습 체크리스트

#### 유닛 테스트 ([test_unit_todos.py](tests/test_unit_todos.py))
- [ ] `test_todo_create_default_completed` - completed 기본값 테스트
- [ ] `test_todo_update_partial` - 부분 업데이트 테스트
- [ ] `test_update_todo_in_db` - DB에서 TODO 수정
- [ ] `test_delete_todo_in_db` - DB에서 TODO 삭제
- [ ] `test_query_all_todos` - 전체 TODO 조회
- [ ] `test_get_todo_by_id_error_message` - 에러 메시지 검증
- [ ] `test_todo_description_validation` - description 파라미터화 테스트

#### 통합 테스트 ([test_integration_todos.py](tests/test_integration_todos.py))
- [ ] `test_update_todo_not_found` - 존재하지 않는 TODO 수정
- [ ] `test_delete_todo_not_found` - 존재하지 않는 TODO 삭제
- [ ] `test_pagination_default_values` - 페이지네이션 기본값
- [ ] `test_pagination_empty_page` - 빈 페이지 조회
- [ ] `test_bulk_todo_operations` - 대량 작업 워크플로우
- [ ] `test_concurrent_updates` - 동시 업데이트
- [ ] `test_create_todo_with_extra_fields` - 추가 필드 처리
- [ ] `test_create_todo_empty_title` - 빈 제목 검증

#### 픽스처 ([conftest.py](tests/conftest.py))
- [ ] `multiple_todos_in_db` - 여러 TODO 생성 픽스처
- [ ] `completed_todos_in_db` - 완료된 TODO 픽스처

---

## 목차
1. [테스트가 필요한 이유](#테스트가-필요한-이유)
2. [테스트의 종류](#테스트의-종류)
3. [pytest 소개](#pytest-소개)
4. [핵심 개념](#핵심-개념)
5. [프로젝트 테스트 구조](#프로젝트-테스트-구조)
6. [테스트 작성 실습](#테스트-작성-실습)
7. [실행 및 커버리지](#실행-및-커버리지)
8. [모범 사례](#모범-사례)

---

## 테스트가 필요한 이유

### 테스트 없이 개발할 때의 문제점

```python
# ❌ 테스트 없는 개발
def create_user(name, email):
    # 코드 작성
    ...

# 문제점:
1. 버그 발견이 늦음 (프로덕션에서 발견) 💥
2. 리팩토링이 두려움 (뭐가 깨질지 모름)
3. 새 기능 추가 시 기존 기능 깨짐
4. 수동 테스트로 시간 낭비
5. 협업 시 신뢰도 하락
```

### 테스트의 장점

```python
# ✅ 테스트가 있는 개발
def test_create_user():
    user = create_user("홍길동", "hong@example.com")
    assert user.name == "홍길동"
    assert user.email == "hong@example.com"

장점:
1. 버그를 빨리 발견 ⚡
2. 자신감 있게 리팩토링 가능 ✨
3. 문서 역할 (코드 사용법 설명)
4. 회귀(Regression) 방지 (기존 기능 보호)
5. 개발 속도 향상 (장기적으로)
```

---

## 테스트의 종류

### 테스트 피라미드

```
        /\
       /  \
      / E2E\      ← 적음 (느림, 비용 높음)
     /______\
    /        \
   / 통합 테스트 \   ← 중간 (여러 컴포넌트 함께)
  /____________\
 /              \
/   유닛 테스트    \  ← 많음 (빠름, 비용 낮음)
/__________________\
```

### 1. 유닛 테스트 (Unit Test)

**개별 함수나 클래스를 독립적으로 테스트**

```python
# 예시: Pydantic 모델 검증
def test_todo_create_valid():
    todo = TodoCreate(title="공부하기", completed=False)
    assert todo.title == "공부하기"

특징:
✅ 빠름 (밀리초 단위)
✅ 독립적 (DB, 네트워크 불필요)
✅ 디버깅 쉬움 (범위가 좁음)
```

### 2. 통합 테스트 (Integration Test)

**여러 컴포넌트가 함께 동작하는 것을 테스트**

```python
# 예시: API 엔드포인트 전체 플로우
def test_create_todo(client):
    response = client.post("/todos/", json={"title": "테스트"})
    assert response.status_code == 201

특징:
✅ 실제 사용자 시나리오 테스트
✅ 컴포넌트 간 상호작용 검증
⚠️  유닛 테스트보다 느림
⚠️  실패 원인 찾기 어려움
```

### 3. E2E 테스트 (End-to-End Test)

**사용자 관점에서 전체 시스템 테스트**

```python
# 예시: 브라우저 자동화 (Selenium, Playwright 등)
# 이 가이드에서는 다루지 않음

특징:
✅ 실제 사용자 경험 검증
⚠️  매우 느림 (초 단위)
⚠️  유지보수 비용 높음
⚠️  불안정 (Flaky)
```

---

## pytest 소개

### pytest란?

**Python에서 가장 인기 있는 테스트 프레임워크**

```python
# unittest (표준 라이브러리) vs pytest

# ❌ unittest (복잡함)
import unittest

class TestTodo(unittest.TestCase):
    def test_create(self):
        self.assertEqual(todo.title, "테스트")

# ✅ pytest (간단함)
def test_create():
    assert todo.title == "테스트"
```

### pytest의 장점

1. **간단한 문법**: `assert` 문만으로 테스트
2. **강력한 픽스처**: 재사용 가능한 테스트 설정
3. **풍부한 플러그인**: pytest-asyncio, pytest-cov 등
4. **상세한 에러 메시지**: 실패 원인을 명확히 표시
5. **파라미터화**: 하나의 테스트로 여러 케이스 검증

---

## 핵심 개념

### 1. Arrange-Act-Assert (AAA) 패턴

모든 테스트는 3단계로 구성:

```python
def test_create_todo():
    # Arrange (준비): 테스트 데이터 준비
    data = {"title": "공부", "completed": False}

    # Act (실행): 테스트 대상 실행
    todo = TodoCreate(**data)

    # Assert (검증): 결과 검증
    assert todo.title == "공부"
    assert todo.completed is False
```

### 2. 픽스처 (Fixture)

**테스트에서 반복적으로 사용하는 설정을 재사용**

```python
# conftest.py
@pytest.fixture
def sample_data():
    """샘플 데이터 픽스처"""
    return {"title": "테스트", "completed": False}

# test_*.py
def test_with_fixture(sample_data):
    """픽스처를 파라미터로 받아 사용"""
    todo = TodoCreate(**sample_data)
    assert todo.title == "테스트"
```

**픽스처 스코프:**
```python
@pytest.fixture(scope="function")  # 각 테스트마다 실행 (기본값)
@pytest.fixture(scope="class")     # 클래스마다 한 번
@pytest.fixture(scope="module")    # 파일마다 한 번
@pytest.fixture(scope="session")   # 전체 테스트에서 한 번
```

### 3. TestClient (FastAPI 테스트)

**실제 서버 없이 API 테스트**

```python
from fastapi.testclient import TestClient

def test_api(client):  # client는 픽스처
    # HTTP 요청 시뮬레이션
    response = client.get("/todos/")

    # 응답 검증
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### 4. 테스트 DB 분리

**프로덕션 DB와 테스트 DB를 분리**

```python
# ❌ 프로덕션 DB 사용 (위험!)
# 테스트 실행 시 실제 데이터 손상 위험

# ✅ 테스트용 DB 사용 (안전)
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def test_db():
    # 테스트 전: 테이블 생성
    Base.metadata.create_all(bind=engine)
    yield db
    # 테스트 후: 테이블 삭제 (정리)
    Base.metadata.drop_all(bind=engine)
```

### 5. 파라미터화 (Parametrize)

**하나의 테스트로 여러 케이스 검증**

```python
@pytest.mark.parametrize("title,expected_valid", [
    ("정상 제목", True),
    ("a" * 100, True),   # 최대 길이
    ("", False),         # 빈 문자열
    ("a" * 101, False),  # 길이 초과
])
def test_title_validation(title, expected_valid):
    if expected_valid:
        todo = TodoCreate(title=title, completed=False)
        assert todo.title == title
    else:
        with pytest.raises(ValidationError):
            TodoCreate(title=title, completed=False)
```

---

## 프로젝트 테스트 구조

```
fastapi-example/
├── app/
│   ├── main.py
│   ├── models.py
│   └── routers/
│       └── todos.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # 픽스처 정의
│   ├── test_unit_todos.py       # 유닛 테스트
│   └── test_integration_todos.py # 통합 테스트
└── pyproject.toml               # pytest 설정
```

### 파일별 역할

| 파일 | 역할 |
|------|------|
| [conftest.py](tests/conftest.py) | 모든 테스트에서 사용하는 픽스처 정의 |
| [test_unit_todos.py](tests/test_unit_todos.py) | 개별 함수/모델 테스트 |
| [test_integration_todos.py](tests/test_integration_todos.py) | API 엔드포인트 E2E 테스트 |

---

## 테스트 작성 실습

### 실습 1: 유닛 테스트 완성하기

[test_unit_todos.py](tests/test_unit_todos.py) 파일을 열고 `TODO` 주석이 있는 테스트를 완성하세요.

**예시: `test_todo_create_default_completed` 완성**

```python
def test_todo_create_default_completed(self):
    """completed 기본값이 False인지 테스트"""
    # Arrange
    data = {"title": "기본값 테스트"}

    # Act
    todo = TodoCreate(**data)

    # Assert
    assert todo.completed is False  # 기본값 확인
```

**실습 목록:**
1. ✅ `test_todo_create_default_completed` - 기본값 테스트
2. ✅ `test_todo_update_partial` - 부분 업데이트 테스트
3. ✅ `test_update_todo_in_db` - DB 수정 테스트
4. ✅ `test_delete_todo_in_db` - DB 삭제 테스트
5. ✅ `test_query_all_todos` - 전체 조회 테스트
6. ✅ `test_get_todo_by_id_error_message` - 에러 메시지 검증

### 실습 2: 통합 테스트 완성하기

[test_integration_todos.py](tests/test_integration_todos.py) 파일의 TODO 테스트를 완성하세요.

**예시: `test_update_todo_not_found` 완성**

```python
def test_update_todo_not_found(self, client):
    """존재하지 않는 TODO 수정 시도"""
    # Arrange
    non_existent_id = 99999
    update_data = {"title": "수정"}

    # Act
    response = client.put(f"/todos/{non_existent_id}", json=update_data)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
```

**실습 목록:**
1. ✅ `test_update_todo_not_found` - 존재하지 않는 TODO 수정
2. ✅ `test_delete_todo_not_found` - 존재하지 않는 TODO 삭제
3. ✅ `test_pagination_default_values` - 페이지네이션 기본값
4. ✅ `test_pagination_empty_page` - 빈 페이지 조회
5. ✅ `test_bulk_todo_operations` - 대량 작업 워크플로우
6. ✅ `test_concurrent_updates` - 동시 업데이트
7. ✅ `test_create_todo_with_extra_fields` - 추가 필드 처리
8. ✅ `test_create_todo_empty_title` - 빈 제목 검증

### 실습 3: 새로운 픽스처 작성하기

[conftest.py](tests/conftest.py)의 TODO 픽스처를 완성하세요.

**예시: `multiple_todos_in_db` 완성**

```python
@pytest.fixture
def multiple_todos_in_db(test_db):
    """여러 개의 TODO를 DB에 미리 생성"""
    todos = []
    for i in range(5):
        todo = TodoDB(
            title=f"할일 {i}",
            description=f"설명 {i}",
            completed=False
        )
        test_db.add(todo)
        todos.append(todo)

    test_db.commit()

    # 모든 TODO의 최신 상태 가져오기
    for todo in todos:
        test_db.refresh(todo)

    return todos
```

---

## 실행 및 커버리지

### Docker 컨테이너에서 테스트 실행

```bash
# 1. Docker Compose로 전체 스택 시작
docker-compose up --build -d

# 2. 컨테이너 안에서 pytest 실행
docker-compose exec fastapi-app pytest

# 3. 상세 출력 모드
docker-compose exec fastapi-app pytest -v

# 4. 특정 파일만 실행
docker-compose exec fastapi-app pytest tests/test_unit_todos.py

# 5. 특정 테스트만 실행
docker-compose exec fastapi-app pytest tests/test_unit_todos.py::TestPydanticModels::test_todo_create_valid

# 6. 실패한 테스트만 재실행
docker-compose exec fastapi-app pytest --lf
```

### 출력 예시

```
================================ test session starts =================================
platform linux -- Python 3.13.0, pytest-8.3.4, pluggy-1.5.0
collected 15 items

tests/test_unit_todos.py .......                                            [ 46%]
tests/test_integration_todos.py ........                                    [100%]

================================= 15 passed in 2.31s =================================
```

### 커버리지 측정

**코드 커버리지**: 테스트가 코드의 몇 %를 실행했는지 측정

```bash
# 1. 커버리지 포함 테스트 실행
docker-compose exec fastapi-app pytest --cov=app --cov-report=term

# 2. HTML 리포트 생성
docker-compose exec fastapi-app pytest --cov=app --cov-report=html

# 3. HTML 리포트 확인
# htmlcov/index.html 파일을 브라우저에서 열기
```

**커버리지 출력 예시:**
```
Name                      Stmts   Miss  Cover
---------------------------------------------
app/__init__.py              0      0   100%
app/database.py             15      0   100%
app/dependencies.py          8      0   100%
app/main.py                 12      2    83%
app/models.py               25      0   100%
app/routers/todos.py        35      3    91%
---------------------------------------------
TOTAL                       95      5    95%
```

**목표:**
- 전체 커버리지: 80% 이상
- 핵심 비즈니스 로직: 90% 이상

---

## 모범 사례

### 1. 테스트 이름은 명확하게

```python
# ❌ 나쁜 예
def test_1():
    pass

# ✅ 좋은 예
def test_create_todo_with_valid_data_returns_201():
    """유효한 데이터로 TODO 생성 시 201 응답"""
    pass
```

### 2. 하나의 테스트는 하나만 검증

```python
# ❌ 나쁜 예 (여러 개 검증)
def test_todo():
    # 생성 테스트
    response = client.post("/todos/", json=data)
    assert response.status_code == 201

    # 조회 테스트
    response = client.get("/todos/1")
    assert response.status_code == 200

# ✅ 좋은 예 (분리)
def test_create_todo():
    response = client.post("/todos/", json=data)
    assert response.status_code == 201

def test_get_todo():
    response = client.get("/todos/1")
    assert response.status_code == 200
```

### 3. 테스트는 독립적으로

```python
# ❌ 나쁜 예 (테스트 간 의존성)
def test_a():
    global user_id
    user_id = create_user()

def test_b():
    # test_a에 의존
    get_user(user_id)

# ✅ 좋은 예 (픽스처 사용)
@pytest.fixture
def user_id(test_db):
    return create_user()

def test_a(user_id):
    assert user_id is not None

def test_b(user_id):
    assert get_user(user_id) is not None
```

### 4. 테스트 데이터는 명확하게

```python
# ❌ 나쁜 예 (매직 넘버/문자열)
def test_create():
    todo = TodoCreate(title="abc", completed=True)

# ✅ 좋은 예 (의도가 명확)
def test_create():
    todo = TodoCreate(
        title="FastAPI 학습하기",  # 실제 사용 예시
        completed=False
    )
```

### 5. 테스트도 리팩토링

```python
# ❌ 나쁜 예 (중복 코드)
def test_a():
    data = {"title": "테스트", "completed": False}
    response = client.post("/todos/", json=data)
    assert response.status_code == 201

def test_b():
    data = {"title": "테스트", "completed": False}
    response = client.post("/todos/", json=data)
    assert response.status_code == 201

# ✅ 좋은 예 (픽스처 사용)
@pytest.fixture
def create_todo_response(client, sample_todo_data):
    return client.post("/todos/", json=sample_todo_data)

def test_a(create_todo_response):
    assert create_todo_response.status_code == 201

def test_b(create_todo_response):
    assert create_todo_response.status_code == 201
```

---

## 고급 주제

### 1. 비동기 테스트

FastAPI는 async/await를 지원하므로 비동기 테스트도 가능:

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    # 비동기 함수 테스트
    result = await some_async_function()
    assert result is not None
```

### 2. 모킹 (Mocking)

외부 의존성(API, DB 등)을 가짜로 대체:

```python
from unittest.mock import patch

def test_with_mock():
    with patch('app.some_module.external_api_call') as mock_api:
        mock_api.return_value = {"result": "mocked"}
        # 실제로 외부 API를 호출하지 않고 테스트
        result = function_that_calls_api()
        assert result["result"] == "mocked"
```

### 3. 테스트 마커 (Markers)

테스트를 그룹화하고 선택적으로 실행:

```python
@pytest.mark.slow
def test_slow_operation():
    """느린 테스트"""
    pass

@pytest.mark.integration
def test_api_integration():
    """통합 테스트"""
    pass

# 실행: pytest -m slow  (slow 마커만)
# 실행: pytest -m "not slow"  (slow 제외)
```

---

## 트러블슈팅

### 문제 1: 테스트 DB가 정리되지 않음

```
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed
```

**해결:**
```python
# conftest.py의 test_db 픽스처 확인
@pytest.fixture(scope="function")  # ✅ function scope 사용
def test_db():
    # ...
    yield db
    Base.metadata.drop_all(bind=engine)  # ✅ 테이블 삭제 확인
```

### 문제 2: 픽스처를 찾을 수 없음

```
fixture 'test_db' not found
```

**해결:**
- `conftest.py`가 `tests/` 디렉토리에 있는지 확인
- `tests/__init__.py` 파일이 있는지 확인

### 문제 3: import 에러

```
ModuleNotFoundError: No module named 'app'
```

**해결:**
```bash
# 컨테이너 안에서 실행하는지 확인
docker-compose exec fastapi-app pytest

# 또는 PYTHONPATH 설정
export PYTHONPATH=/app:$PYTHONPATH
```

### 문제 4: 테스트가 느림

**해결:**
1. 유닛 테스트와 통합 테스트 분리
2. 테스트 DB로 SQLite 사용 (PostgreSQL보다 빠름)
3. 픽스처 scope 조정 (function → class → module)
4. 병렬 실행: `pytest -n auto` (pytest-xdist 필요)

---

## 다음 단계

이 가이드를 완료했다면:

1. ✅ **더 많은 테스트 작성**
   - 엣지 케이스 (경계값, null 등)
   - 에러 처리 경로
   - 성능 테스트 (다음 가이드)

2. ✅ **CI/CD 통합**
   - GitHub Actions, GitLab CI 등
   - 커밋/PR마다 자동 테스트 실행

3. ✅ **TDD (Test-Driven Development)**
   - 테스트 먼저 작성
   - 최소한의 코드로 통과
   - 리팩토링

4. ✅ **성능 테스트**
   - 다음 가이드: [4study-performance.md](4study-performance.md)
   - Locust를 사용한 부하 테스트

---

## 참고 자료

### 공식 문서
- [pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI 테스팅 가이드](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

### 학습 리소스
- [Real Python - Testing with pytest](https://realpython.com/pytest-python-testing/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

---

## 요약

### 핵심 개념
- **유닛 테스트**: 개별 함수/클래스 독립 테스트
- **통합 테스트**: 여러 컴포넌트 함께 테스트
- **픽스처**: 재사용 가능한 테스트 설정
- **AAA 패턴**: Arrange-Act-Assert
- **커버리지**: 테스트가 코드를 얼마나 실행했는지

### 주요 명령어
```bash
# 전체 테스트 실행
docker-compose exec fastapi-app pytest

# 상세 출력
docker-compose exec fastapi-app pytest -v

# 커버리지 측정
docker-compose exec fastapi-app pytest --cov=app --cov-report=html

# 특정 파일 실행
docker-compose exec fastapi-app pytest tests/test_unit_todos.py

# 실패한 테스트만 재실행
docker-compose exec fastapi-app pytest --lf
```

### 테스트 작성 체크리스트
- [ ] AAA 패턴 사용
- [ ] 테스트 이름이 명확함
- [ ] 하나의 테스트는 하나만 검증
- [ ] 테스트는 독립적임
- [ ] 픽스처로 중복 제거
- [ ] 엣지 케이스 포함
- [ ] 에러 케이스 포함

---

**축하합니다!** 이제 FastAPI 애플리케이션을 체계적으로 테스트하는 방법을 배웠습니다. 다음은 성능 테스트를 배워보세요!
