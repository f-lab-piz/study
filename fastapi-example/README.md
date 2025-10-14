# FastAPI TODO API 예제

FastAPI 학습을 위한 간단한 TODO 관리 API입니다.

## 특징

- ✅ Pydantic을 사용한 데이터 검증
- ✅ Dependency Injection 패턴 적용
- ✅ 자동 API 문서 생성
- ✅ RESTful API 설계
- ✅ 메모리 기반 저장소 (DB 불필요)

## 프로젝트 구조

```
fastapi-example/
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

## 설치 및 실행

### Docker 사용 (권장)

Docker를 사용하면 환경 설정 없이 바로 실행할 수 있습니다.

**사전 요구사항:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치

**실행 방법:**

```bash
# 1. Docker Compose로 실행
docker-compose up -d

# 2. 로그 확인
docker-compose logs -f

# 3. 브라우저에서 확인
# http://localhost:8000/docs

# 4. 중지
docker-compose down
```

**개발 모드로 실행:**
```bash
# 코드 변경 시 자동으로 재시작됩니다
docker-compose up

# 컨테이너 내부 접속 (디버깅)
docker-compose exec fastapi-app /bin/bash
```

### uv 설치

uv가 설치되어 있지 않다면 먼저 설치해주세요.

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

### uv 사용 (권장)

```bash
# 1. 의존성 설치
uv sync

# 2. 개발 서버 실행
uv run uvicorn app.main:app --reload

# 3. 브라우저에서 확인
# http://127.0.0.1:8000/docs
```

### pip 사용

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 의존성 설치
pip install fastapi "uvicorn[standard]"

# 3. 개발 서버 실행
uvicorn app.main:app --reload
```

## API 엔드포인트

### 기본

- `GET /` - 루트 엔드포인트
- `GET /health` - 헬스 체크
- `GET /docs` - Swagger UI (자동 문서)
- `GET /redoc` - ReDoc (대체 문서)

### TODO

- `GET /todos/` - 모든 TODO 목록 조회
- `GET /todos/{todo_id}` - 특정 TODO 조회
- `POST /todos/` - 새 TODO 생성
- `PUT /todos/{todo_id}` - TODO 수정
- `DELETE /todos/{todo_id}` - TODO 삭제

## 사용 예시

### curl

```bash
# TODO 생성
curl -X POST http://127.0.0.1:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FastAPI 공부하기",
    "description": "Pydantic과 DI 개념 학습",
    "completed": false
  }'

# TODO 목록 조회
curl http://127.0.0.1:8000/todos/

# TODO 수정
curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# TODO 삭제
curl -X DELETE http://127.0.0.1:8000/todos/1
```

### Python requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# TODO 생성
response = requests.post(
    f"{BASE_URL}/todos/",
    json={
        "title": "장보기",
        "description": "우유, 계란, 빵"
    }
)
print(response.json())

# TODO 목록 조회
response = requests.get(f"{BASE_URL}/todos/")
print(response.json())
```

## 학습 포인트

### 1. Pydantic 모델 (`models.py`)

- 타입 힌트를 사용한 데이터 검증
- `Field()`를 통한 세부 검증 규칙
- 자동 문서 생성

### 2. Dependency Injection (`dependencies.py`)

- `Depends()`를 사용한 의존성 주입
- 재사용 가능한 로직 분리
- 테스트 용이성

### 3. APIRouter (`routers/todos.py`)

- 라우트 그룹화
- 경로 파라미터 처리
- 상태 코드 지정
- 에러 처리

### 4. FastAPI 앱 (`main.py`)

- 애플리케이션 설정
- 라우터 등록
- 메타데이터 정의

## Docker 학습

Docker에 대해 더 자세히 알고 싶다면:
- [Docker 기초 학습 가이드](1study-docker.md)

Docker 파일 구조:
- [`Dockerfile`](Dockerfile) - 이미지 빌드 레시피
- [`docker-compose.yml`](docker-compose.yml) - 멀티 컨테이너 설정
- [`.dockerignore`](.dockerignore) - 이미지에서 제외할 파일 목록

## 다음 단계

이 예제를 완료했다면:

1. ✅ Docker 컨테이너화 (완료)
2. ✅ DB 연결 (SQLAlchemy + PostgreSQL + Docker)
3. ✅ 인증/인가 (JWT)
4. ✅ 테스트 작성 (pytest)
5. ✅ 프로덕션 배포 (Kubernetes, AWS ECS)

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [Docker 공식 문서](https://docs.docker.com/)
- [FastAPI 학습 가이드](fastapi-beginner-guide.md)
- [Docker 학습 가이드](1study-docker.md)
