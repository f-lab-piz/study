# Docker 기초 학습 가이드

## 목차
1. [Docker란 무엇인가?](#docker란-무엇인가)
2. [왜 Docker를 사용하는가?](#왜-docker를-사용하는가)
3. [핵심 개념](#핵심-개념)
4. [Docker 설치](#docker-설치)
5. [기본 명령어](#기본-명령어)
6. [Dockerfile 작성](#dockerfile-작성)
7. [Docker Compose](#docker-compose)
8. [실습: FastAPI 프로젝트 Docker화](#실습-fastapi-프로젝트-docker화)

---

## Docker란 무엇인가?

Docker는 **컨테이너 기반의 가상화 플랫폼**입니다. 애플리케이션과 그 실행 환경을 하나의 패키지(컨테이너)로 만들어 어디서든 동일하게 실행할 수 있게 해줍니다.

### 가상 머신 vs Docker 컨테이너

```
가상 머신 (VM)                    Docker 컨테이너
┌─────────────────┐              ┌─────────────────┐
│   App A │ App B │              │ App A │ App B   │
├─────────┼───────┤              ├─────────┼───────┤
│  Guest OS       │              │   Docker Engine │
├─────────────────┤              ├─────────────────┤
│   Hypervisor    │              │    Host OS      │
├─────────────────┤              ├─────────────────┤
│    Host OS      │              │   Infrastructure│
├─────────────────┤              └─────────────────┘
│  Infrastructure │
└─────────────────┘
```

**차이점:**
- **VM**: 각각의 게스트 OS를 포함 → 무겁고 느림
- **Docker**: Host OS의 커널을 공유 → 가볍고 빠름

---

## 왜 Docker를 사용하는가?

### 1. "내 컴퓨터에서는 되는데..." 문제 해결
```bash
# 개발자 A의 환경
Python 3.12 + FastAPI 0.115.6 ✅

# 개발자 B의 환경
Python 3.9 + FastAPI 0.100.0 ❌ (버전 충돌!)

# Docker 사용 시
모든 개발자가 동일한 컨테이너 사용 ✅
```

### 2. 환경 설정 간소화
```bash
# 기존 방식
1. Python 설치
2. 가상환경 생성
3. 패키지 설치
4. 환경 변수 설정
5. 데이터베이스 설치
6. ...

# Docker 사용 시
docker-compose up  # 끝!
```

### 3. 격리된 환경
- 프로젝트마다 독립적인 환경
- 시스템에 영향을 주지 않음
- 여러 버전의 같은 프로그램 실행 가능

### 4. 배포 용이성
```bash
# 로컬에서 테스트
docker run myapp

# 서버에서 실행
docker run myapp  # 동일한 명령어!
```

---

## 핵심 개념

### 1. 이미지 (Image)
애플리케이션 실행에 필요한 모든 것을 포함한 **읽기 전용 템플릿**

```
이미지 = 애플리케이션 + 라이브러리 + 실행환경 + 설정파일
```

예시:
- `python:3.13-slim` - Python 3.13이 설치된 이미지
- `nginx:latest` - Nginx 웹서버 이미지

### 2. 컨테이너 (Container)
이미지를 실행한 **실행 가능한 인스턴스**

```
컨테이너 = 이미지 + 실행 프로세스
```

비유:
- **이미지** = 붕어빵 틀 (템플릿)
- **컨테이너** = 붕어빵 (실제 실행되는 것)

### 3. Dockerfile
이미지를 만들기 위한 **레시피(설명서)**

```dockerfile
FROM python:3.13-slim    # 베이스 이미지
WORKDIR /app             # 작업 디렉토리
COPY . .                 # 파일 복사
RUN pip install -r requirements.txt  # 명령 실행
CMD ["python", "app.py"] # 실행 명령
```

### 4. Docker Compose
**여러 컨테이너를 한 번에 관리**하기 위한 도구

```yaml
# docker-compose.yml
services:
  web:        # 웹 애플리케이션
    ...
  database:   # 데이터베이스
    ...
  redis:      # 캐시
    ...
```

---

## Docker 설치

### Windows / Mac
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치
2. 설치 후 Docker Desktop 실행

### Linux (Ubuntu)
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### 설치 확인
```bash
docker --version
# Docker version 24.0.0, build ...

docker-compose --version
# Docker Compose version v2.20.0
```

---

## 기본 명령어

### 이미지 관련

```bash
# 이미지 검색
docker search python

# 이미지 다운로드
docker pull python:3.13-slim

# 이미지 목록 확인
docker images

# 이미지 삭제
docker rmi python:3.13-slim

# 이미지 빌드
docker build -t myapp:latest .
```

### 컨테이너 관련

```bash
# 컨테이너 실행
docker run -d -p 8000:8000 --name myapp myapp:latest
# -d: 백그라운드 실행
# -p: 포트 매핑 (호스트:컨테이너)
# --name: 컨테이너 이름 지정

# 실행 중인 컨테이너 확인
docker ps

# 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a

# 컨테이너 로그 확인
docker logs myapp
docker logs -f myapp  # 실시간 로그

# 컨테이너 내부 접속
docker exec -it myapp /bin/bash

# 컨테이너 중지
docker stop myapp

# 컨테이너 시작
docker start myapp

# 컨테이너 재시작
docker restart myapp

# 컨테이너 삭제
docker rm myapp

# 실행 중인 컨테이너 강제 삭제
docker rm -f myapp
```

### 정리 명령어

```bash
# 중지된 모든 컨테이너 삭제
docker container prune

# 사용하지 않는 모든 이미지 삭제
docker image prune

# 사용하지 않는 모든 리소스 삭제 (컨테이너, 이미지, 네트워크, 볼륨)
docker system prune -a
```

---

## Dockerfile 작성

### 기본 구조

```dockerfile
# 1. 베이스 이미지 지정
FROM python:3.13-slim

# 2. 메타데이터 (선택사항)
LABEL maintainer="your@email.com"
LABEL description="FastAPI TODO Application"

# 3. 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 4. 작업 디렉토리 설정
WORKDIR /app

# 5. 파일 복사
COPY requirements.txt .
COPY app/ ./app/

# 6. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 7. 포트 노출 (문서화 목적)
EXPOSE 8000

# 8. 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# 9. 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 주요 명령어 설명

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `FROM` | 베이스 이미지 지정 | `FROM python:3.13-slim` |
| `WORKDIR` | 작업 디렉토리 설정 | `WORKDIR /app` |
| `COPY` | 파일/디렉토리 복사 | `COPY . .` |
| `RUN` | 이미지 빌드 시 명령 실행 | `RUN apt-get update` |
| `ENV` | 환경 변수 설정 | `ENV DEBUG=True` |
| `EXPOSE` | 포트 노출 (문서화) | `EXPOSE 8000` |
| `CMD` | 컨테이너 시작 시 실행 명령 | `CMD ["python", "app.py"]` |
| `ENTRYPOINT` | 컨테이너의 진입점 설정 | `ENTRYPOINT ["python"]` |

### 최적화 팁

#### 1. 레이어 캐싱 활용
```dockerfile
# ❌ 나쁜 예 - 코드 변경 시 매번 패키지 재설치
COPY . .
RUN pip install -r requirements.txt

# ✅ 좋은 예 - requirements.txt 변경 시만 재설치
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

#### 2. 멀티 스테이지 빌드
```dockerfile
# 빌드 스테이지
FROM python:3.13 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 실행 스테이지
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

#### 3. .dockerignore 사용
```
# .dockerignore
__pycache__
*.pyc
.git
.venv
*.md
.env
```

---

## Docker Compose

### 기본 구조

```yaml
version: '3.8'  # Docker Compose 파일 버전

services:
  # 서비스 1: 웹 애플리케이션
  web:
    build: .                    # Dockerfile로 빌드
    ports:
      - "8000:8000"            # 포트 매핑
    volumes:
      - ./app:/app/app         # 볼륨 마운트
    environment:
      - DEBUG=True             # 환경 변수
    depends_on:
      - db                     # 의존성 설정

  # 서비스 2: 데이터베이스
  db:
    image: postgres:15         # 이미지 사용
    environment:
      - POSTGRES_PASSWORD=secret
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:                     # 볼륨 정의
```

### 주요 명령어

```bash
# 서비스 시작 (백그라운드)
docker-compose up -d

# 서비스 시작 (포그라운드, 로그 확인)
docker-compose up

# 빌드 후 시작
docker-compose up --build

# 서비스 중지
docker-compose stop

# 서비스 중지 및 컨테이너 삭제
docker-compose down

# 서비스 중지 및 볼륨까지 삭제
docker-compose down -v

# 로그 확인
docker-compose logs
docker-compose logs -f web  # 특정 서비스 로그

# 실행 중인 서비스 확인
docker-compose ps

# 서비스 재시작
docker-compose restart

# 특정 서비스에서 명령 실행
docker-compose exec web /bin/bash
```

---

## 실습: FastAPI 프로젝트 Docker화

이제 `fastapi-example` 프로젝트를 Docker로 실행해봅시다!

### 1. 프로젝트 구조 확인

```
fastapi-example/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── dependencies.py
│   └── routers/
│       ├── __init__.py
│       └── todos.py
├── Dockerfile              # ← 새로 생성됨
├── docker-compose.yml      # ← 새로 생성됨
├── .dockerignore           # ← 새로 생성됨
├── pyproject.toml
└── README.md
```

### 2. Dockerfile 설명

```dockerfile
# Python 3.13 slim 이미지 사용
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock* ./

# 의존성 설치 (시스템 전역에 설치)
RUN uv sync --frozen --no-cache

# 애플리케이션 코드 복사
COPY app/ ./app/

# 포트 노출
EXPOSE 8000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 애플리케이션 실행
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**핵심 포인트:**
- `python:3.13-slim`: 경량화된 Python 이미지 사용
- `uv`: 빠른 Python 패키지 관리자 사용
- `HEALTHCHECK`: 컨테이너 상태 모니터링
- `--host 0.0.0.0`: 외부 접속 허용

### 3. docker-compose.yml 설명

```yaml
version: '3.8'

services:
  fastapi-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fastapi-todo-app
    ports:
      - "8000:8000"                # 호스트:컨테이너
    environment:
      - ENVIRONMENT=development
    volumes:
      # 개발 중 코드 변경사항을 실시간 반영 (개발 모드)
      - ./app:/app/app
    restart: unless-stopped        # 자동 재시작
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

**핵심 포인트:**
- `volumes`: 로컬 코드 변경 시 컨테이너에 즉시 반영
- `restart`: 컨테이너 종료 시 자동 재시작
- `healthcheck`: 애플리케이션 상태 확인

### 4. .dockerignore 설명

```
# Python
__pycache__
*.py[cod]
*.egg-info/

# Virtual environments
.venv
venv/

# Documentation
*.md
!README.md

# Docker
Dockerfile
docker-compose.yml
```

**목적:** 불필요한 파일이 이미지에 포함되지 않도록 제외

### 5. Docker로 실행하기

#### 방법 1: Docker Compose 사용 (권장)

```bash
# 프로젝트 디렉토리로 이동
cd fastapi-example

# 1. 빌드 및 실행
docker-compose up --build

# 또는 백그라운드 실행
docker-compose up -d

# 2. 로그 확인
docker-compose logs -f

# 3. 브라우저에서 확인
# http://localhost:8000/docs

# 4. 중지
docker-compose down
```

#### 방법 2: Docker 명령어 직접 사용

```bash
# 1. 이미지 빌드
docker build -t fastapi-todo:latest .

# 2. 컨테이너 실행
docker run -d \
  -p 8000:8000 \
  --name fastapi-todo \
  -v $(pwd)/app:/app/app \
  fastapi-todo:latest

# 3. 로그 확인
docker logs -f fastapi-todo

# 4. 중지 및 삭제
docker stop fastapi-todo
docker rm fastapi-todo
```

### 6. 동작 확인

```bash
# 1. 헬스체크
curl http://localhost:8000/health

# 2. API 문서 확인
# 브라우저: http://localhost:8000/docs

# 3. TODO 생성
curl -X POST http://localhost:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Docker 학습하기", "description": "컨테이너 기초 개념 이해"}'

# 4. TODO 목록 조회
curl http://localhost:8000/todos/
```

### 7. 개발 워크플로우

```bash
# 1. 컨테이너 시작
docker-compose up -d

# 2. 코드 수정
# app/ 디렉토리의 파일 수정

# 3. 변경사항 자동 반영
# uvicorn의 --reload 옵션으로 자동 재시작
# volumes 설정으로 실시간 반영

# 4. 로그 확인
docker-compose logs -f fastapi-app

# 5. 컨테이너 내부 접속 (디버깅)
docker-compose exec fastapi-app /bin/bash

# 6. 작업 완료 후 중지
docker-compose down
```

---

## 트러블슈팅

### 문제 1: 포트가 이미 사용 중
```bash
Error: Bind for 0.0.0.0:8000 failed: port is already allocated

# 해결 방법
# 1. 사용 중인 프로세스 확인 및 종료
lsof -i :8000
kill -9 <PID>

# 2. docker-compose.yml에서 포트 변경
ports:
  - "8001:8000"  # 호스트 포트를 8001로 변경
```

### 문제 2: 이미지 빌드 실패
```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 또는
docker build --no-cache -t fastapi-todo .
```

### 문제 3: 볼륨 권한 문제
```bash
# Linux에서 권한 문제 발생 시
sudo chown -R $USER:$USER ./app
```

### 문제 4: 컨테이너가 바로 종료됨
```bash
# 로그 확인
docker-compose logs

# 또는
docker logs <container-id>
```

---

## 다음 단계

이 가이드를 완료했다면:

1. ✅ Docker 네트워크 학습
   - 컨테이너 간 통신
   - 브릿지, 호스트, 오버레이 네트워크

2. ✅ Docker 볼륨 심화
   - 데이터 영속성
   - 볼륨 타입 (bind mount, volume, tmpfs)

3. ✅ 멀티 컨테이너 애플리케이션
   - FastAPI + PostgreSQL + Redis
   - 마이크로서비스 아키텍처

4. ✅ 프로덕션 배포
   - Docker Swarm 또는 Kubernetes
   - CI/CD 파이프라인

5. ✅ 보안
   - 이미지 스캔
   - 비밀 관리
   - 최소 권한 원칙

---

## 참고 자료

### 공식 문서
- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [Dockerfile 참조](https://docs.docker.com/engine/reference/builder/)

### 실습 자료
- [Play with Docker](https://labs.play-with-docker.com/) - 브라우저에서 Docker 실습
- [Docker Hub](https://hub.docker.com/) - 공식 이미지 저장소

### 학습 리소스
- [Docker for Beginners](https://docker-curriculum.com/)
- [Docker 한글 가이드](https://docs.docker.com/language/python/)

---

## 요약

### 핵심 개념
- **이미지**: 애플리케이션 실행 템플릿
- **컨테이너**: 이미지를 실행한 인스턴스
- **Dockerfile**: 이미지를 만드는 레시피
- **Docker Compose**: 멀티 컨테이너 관리 도구

### 주요 명령어
```bash
# 이미지
docker build -t name:tag .
docker pull image:tag
docker images

# 컨테이너
docker run -d -p 8000:8000 image
docker ps
docker logs container
docker exec -it container /bin/bash
docker stop container

# Compose
docker-compose up -d
docker-compose down
docker-compose logs -f
```

### 장점
- ✅ 환경 일관성
- ✅ 빠른 배포
- ✅ 격리된 환경
- ✅ 효율적인 리소스 사용

---

**다음 학습**: FastAPI 프로젝트를 PostgreSQL과 Redis를 추가하여 멀티 컨테이너 애플리케이션으로 확장해보세요!
