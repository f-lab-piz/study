# 2주차: DB 연결해서 진짜 서비스처럼

## 핵심 목표

- Docker로 PostgreSQL 실행하기
- FastAPI와 DB 연결하기
- 메모리 CRUD → DB CRUD로 전환

---

## 1. 왜 데이터베이스가 필요한가?

### 1주차 방식의 문제점

```python
# week1의 메모리 저장 방식
fake_db: dict[int, dict] = {
    1: {"id": 1, "name": "김철수", "email": "kim@example.com"},
}
```

**문제점:**
1. ❌ **서버 재시작하면 데이터 사라짐** - 메모리에만 저장
2. ❌ **동시 접속 시 데이터 꼬임** - 멀티 프로세스 환경에서 문제
3. ❌ **대용량 데이터 처리 불가** - 메모리 한계
4. ❌ **복잡한 쿼리 불가능** - 검색, 필터링, 정렬 비효율적

### 데이터베이스를 사용하면

```
[FastAPI] ←─→ [PostgreSQL]
           SQL 쿼리

✅ 영구 저장 (서버 재시작해도 데이터 유지)
✅ 트랜잭션 (여러 작업을 하나로 묶어 안전하게)
✅ 인덱싱 (빠른 검색)
✅ 동시성 제어 (여러 클라이언트가 동시 접속해도 안전)
```

---

## 2. Docker란?

### Docker의 필요성

**문제 상황:**
```
개발자 A의 컴퓨터: PostgreSQL 14 설치
개발자 B의 컴퓨터: PostgreSQL 15 설치
운영 서버: PostgreSQL 13 설치

→ "내 컴퓨터에서는 되는데요?" 문제 발생
```

**Docker 사용:**
```
모두가 같은 컨테이너 사용
→ PostgreSQL 14 컨테이너
→ 어디서든 똑같이 동작
```

### Docker 핵심 개념

```
┌─────────────────────────────────────┐
│         내 컴퓨터 (Host)              │
│                                      │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ Container 1   │  │ Container 2   │ │
│  │              │  │              │ │
│  │ PostgreSQL   │  │ Redis        │ │
│  │ 14.0         │  │ 7.0          │ │
│  └──────────────┘  └──────────────┘ │
│                                      │
│        Docker Engine                 │
└─────────────────────────────────────┘
```

| 개념 | 설명 | 비유 |
|------|------|------|
| **Image** | 실행 가능한 패키지 (PostgreSQL 설치 파일) | 붕어빵 틀 |
| **Container** | Image를 실행한 인스턴스 | 붕어빵 (틀로 찍어낸 것) |
| **Docker Hub** | Image 저장소 | 앱스토어 |
| **Volume** | 데이터 영구 저장 공간 | 외장 하드 |

### Docker vs 가상머신

```
가상머신 (VM)                    Docker
┌─────────────────┐           ┌─────────────────┐
│   App           │           │   App           │
├─────────────────┤           ├─────────────────┤
│   Guest OS      │           │  (Host OS 공유)  │
├─────────────────┤           ├─────────────────┤
│   Hypervisor    │           │ Docker Engine   │
├─────────────────┤           ├─────────────────┤
│   Host OS       │           │   Host OS       │
└─────────────────┘           └─────────────────┘

⏱️ 부팅: 수십 초               ⏱️ 시작: 1초 이내
💾 용량: GB 단위               💾 용량: MB 단위
```

### Docker는 어떻게 OS에 상관없이 실행될까?

#### 1. Linux에서: 다른 커널 버전에서도 Docker가 실행되는 이유

**의문:**
```
Ubuntu 20.04 (커널 5.4)  →  Docker 실행 가능
Ubuntu 22.04 (커널 5.15) →  Docker 실행 가능
Ubuntu 24.04 (커널 6.8)  →  Docker 실행 가능

왜 커널 버전이 달라도 같은 Docker 이미지가 실행될까?
```

**핵심 원리: 컨테이너는 커널을 공유한다**

```
┌───────────────────────────────────────────┐
│           Host 머신 (Ubuntu 22.04)         │
│                                            │
│  ┌────────────┐  ┌────────────┐           │
│  │ Container 1│  │ Container 2│           │
│  │ Alpine     │  │ Ubuntu     │           │
│  │ 3.18       │  │ 20.04      │           │
│  └────────────┘  └────────────┘           │
│         │              │                   │
│         └──────┬───────┘                   │
│                ↓                           │
│    Linux Kernel 5.15 (Host 커널 공유!)     │
│    ↑                                       │
│    Namespaces + Cgroups로 격리              │
└───────────────────────────────────────────┘
```

**중요한 사실:**
- ✅ **컨테이너는 별도의 커널을 가지지 않는다**
- ✅ **Host 머신의 커널을 공유**한다
- ✅ **Namespaces**로 프로세스/네트워크/파일시스템을 격리
- ✅ **Cgroups**로 CPU/메모리 자원을 제한

**예시:**
```bash
# Host 머신의 커널 확인
uname -r
# 출력: 5.15.0-86-generic

# 컨테이너 안에서 커널 확인
docker run alpine uname -r
# 출력: 5.15.0-86-generic (똑같음!)

# 컨테이너 안에서 OS 정보는 다름
docker run alpine cat /etc/os-release
# 출력: Alpine Linux
```

**왜 이게 가능한가?**

Docker는 **OS 수준 가상화**를 사용:
1. 컨테이너의 `/bin`, `/lib` 등 파일시스템만 격리
2. 실제 시스템 콜(syscall)은 Host 커널로 전달
3. 같은 리눅스 커널이면 어떤 버전이든 동작 (커널 API가 하위 호환)

**제약사항:**
- ❌ Linux 컨테이너는 Linux 커널이 필요
- ❌ Windows 컨테이너는 Windows 커널이 필요
- ❌ 커널 모듈이 필요한 작업은 Host 커널에 의존

---

#### 2. Windows/Mac에서 Linux Docker가 실행되는 원리

**의문:**
```
Mac (Darwin 커널)   →  Linux Docker 실행?
Windows (NT 커널)   →  Linux Docker 실행?

리눅스 커널이 없는데 어떻게 리눅스 컨테이너가 실행될까?
```

**답: 숨겨진 경량 가상머신이 있다!**

##### Windows/Mac의 Docker 아키텍처

```
┌─────────────────────────────────────────────┐
│          Mac / Windows (Host OS)             │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │    Docker Desktop (애플리케이션)         │ │
│  │                                          │ │
│  │  ┌────────────────────────────────────┐ │ │
│  │  │   경량 Linux VM (숨겨져 있음)        │ │ │
│  │  │   - HyperKit (Mac)                  │ │ │
│  │  │   - Hyper-V/WSL2 (Windows)          │ │ │
│  │  │                                      │ │ │
│  │  │  ┌─────────┐  ┌─────────┐           │ │ │
│  │  │  │Container│  │Container│  ← 리눅스  │ │ │
│  │  │  │  (앱)   │  │  (DB)   │     컨테이너│ │ │
│  │  │  └─────────┘  └─────────┘           │ │ │
│  │  │        ↑           ↑                 │ │ │
│  │  │        └───────────┘                 │ │ │
│  │  │     Linux Kernel (VM 내부)           │ │ │
│  │  └────────────────────────────────────┘ │ │
│  └────────────────────────────────────────┘ │
│                                              │
│         Mac Kernel / Windows Kernel          │
└─────────────────────────────────────────────┘
```

##### 각 OS별 상세 동작 방식

| OS | 가상화 기술 | 설명 |
|---|------------|------|
| **Linux** | 없음 (Native) | Docker가 Host 커널을 직접 사용 (가장 빠름) |
| **Mac** | HyperKit (macOS 13+) 또는 QEMU | 경량 Linux VM을 백그라운드에서 실행 |
| **Windows 10/11** | WSL2 (권장) 또는 Hyper-V | WSL2: 실제 Linux 커널 탑재, Hyper-V: 가상머신 |

##### Windows에서 Docker Desktop 실행 과정

```bash
# 1. Docker Desktop 실행
# → WSL2 또는 Hyper-V로 경량 Linux VM 시작

# 2. docker run alpine echo "hello"
# ↓
# Docker CLI (Windows)
#   → Docker Daemon (Linux VM 내부)
#     → Container 생성 (Linux VM 내부)

# 3. 결과는 Windows 터미널에 표시
# "hello"
```

**사용자는 눈치채지 못하지만:**
- Windows/Mac의 Docker CLI → **네트워크로 Linux VM의 Docker Daemon과 통신**
- 실제 컨테이너는 **숨겨진 Linux VM 안에서** 실행
- 파일 공유, 포트 포워딩 등은 Docker Desktop이 자동 처리

##### 성능 비교

| OS | 성능 | 이유 |
|---|------|------|
| **Linux** | ⭐⭐⭐⭐⭐ (가장 빠름) | 가상화 없이 커널 직접 사용 |
| **Mac** | ⭐⭐⭐ (적당) | HyperKit VM 오버헤드 존재 |
| **Windows (WSL2)** | ⭐⭐⭐⭐ (빠름) | WSL2는 경량화된 진짜 Linux |
| **Windows (Hyper-V)** | ⭐⭐ (느림) | 전통적인 VM 방식 |

##### WSL2란? (Windows 사용자 필독)

**WSL2 = Windows Subsystem for Linux 2**

```
기존 WSL1 (번역 방식)              WSL2 (진짜 리눅스)
┌──────────────────┐            ┌──────────────────┐
│  Linux 명령어     │            │  Linux 명령어     │
├──────────────────┤            ├──────────────────┤
│  번역 레이어       │            │ 진짜 Linux Kernel │ ← 여기!
│  (Syscall 변환)  │            │ (경량 VM)         │
├──────────────────┤            ├──────────────────┤
│  Windows Kernel  │            │  Windows Kernel  │
└──────────────────┘            └──────────────────┘

❌ 느리고 호환성 낮음            ✅ 빠르고 100% 호환
```

**WSL2의 장점:**
- ✅ **진짜 Linux 커널**을 Windows 안에서 실행
- ✅ Docker 성능이 거의 Native Linux 수준
- ✅ 파일 I/O 성능 대폭 향상
- ✅ 모든 Linux 시스템 콜 지원

**확인 방법:**
```powershell
# Windows에서
wsl --list --verbose

# WSL2로 실행 중인지 확인
# VERSION이 2이면 WSL2 사용 중
```

---

#### 정리: Docker의 크로스 플랫폼 전략

| 상황 | Docker 동작 방식 |
|-----|----------------|
| **Linux → Linux Container** | ✅ Host 커널 직접 사용 (Native, 가장 빠름) |
| **Mac → Linux Container** | ⚠️ HyperKit으로 Linux VM 실행 (약간 느림) |
| **Windows → Linux Container** | ⚠️ WSL2/Hyper-V로 Linux VM 실행 |
| **Windows → Windows Container** | ✅ Host 커널 직접 사용 (Native) |

**핵심:**
- Linux에서는 **커널 공유**로 초고속 실행
- Mac/Windows는 **보이지 않는 Linux VM**을 사용
- 사용자 경험은 동일하지만, 내부 동작은 완전히 다름

**실무 팁:**
- 운영 서버는 거의 Linux → Docker Native 사용
- 개발 환경(Mac/Windows)은 Docker Desktop 사용
- CI/CD도 대부분 Linux 기반

---

## 3. Docker Compose로 PostgreSQL 실행

### Docker Compose란?

**단일 컨테이너 (docker run):**
```bash
docker run -d \
  -e POSTGRES_PASSWORD=mysecret \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15

# 명령어가 너무 길고 복잡...
```

**Docker Compose (docker-compose.yml):**
```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mysecret
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

```bash
# 실행은 간단하게
docker compose up -d
```

→ 설정을 파일로 관리하고, 여러 컨테이너를 한 번에 실행

### docker-compose.yml 작성

**week2/docker-compose.yml**

```yaml
services:
  # PostgreSQL 데이터베이스
  db:
    image: postgres:15-alpine  # Alpine은 경량 Linux (용량 작음)
    container_name: week2-postgres
    environment:
      # 환경 변수로 DB 설정
      POSTGRES_USER: fastapi_user
      POSTGRES_PASSWORD: fastapi_pass
      POSTGRES_DB: fastapi_db
    ports:
      - "5432:5432"  # 호스트:컨테이너
    volumes:
      - postgres_data:/var/lib/postgresql/data  # 데이터 영구 저장
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fastapi_user"]
      interval: 5s
      timeout: 5s
      retries: 5

# 볼륨 정의 (컨테이너 삭제해도 데이터 유지)
volumes:
  postgres_data:
```

**주요 옵션 설명:**

| 옵션 | 의미 | 예시 |
|------|------|------|
| `image` | 사용할 이미지 | `postgres:15-alpine` |
| `container_name` | 컨테이너 이름 | `week2-postgres` |
| `environment` | 환경 변수 | DB 사용자/비밀번호 설정 |
| `ports` | 포트 매핑 | `5432:5432` (외부:내부) |
| `volumes` | 데이터 저장 위치 | 컨테이너 삭제해도 데이터 유지 |
| `healthcheck` | 컨테이너 상태 확인 | DB가 준비됐는지 체크 |

### 포트 매핑 이해하기

```
내 컴퓨터 (Host)                   Container
    :5432        ←───────────→      :5432
     ↑                               ↑
   외부 접속                      PostgreSQL이
   (FastAPI,                     실제 실행되는
   DBeaver 등)                    포트
```

```yaml
ports:
  - "5432:5432"
    ↑      ↑
    │      └─ 컨테이너 내부 포트 (PostgreSQL 기본)
    └─ 호스트 포트 (내 컴퓨터에서 접속할 포트)
```

- `5432:5432` → 외부 5432로 접속하면 컨테이너 5432로 연결
- `5433:5432` → 외부 5433으로 접속하면 컨테이너 5432로 연결 (포트 충돌 시)

### Docker Compose 명령어

```bash
# 컨테이너 시작 (백그라운드)
docker compose up -d

# 로그 확인
docker compose logs
docker compose logs -f  # 실시간 로그

# 상태 확인
docker compose ps

# 컨테이너 중지
docker compose stop

# 컨테이너 삭제 (볼륨은 유지)
docker compose down

# 컨테이너 + 볼륨 모두 삭제 (데이터도 삭제!)
docker compose down -v

# 컨테이너 재시작
docker compose restart
```

---

## 4. PostgreSQL 기초

### PostgreSQL이란?

**관계형 데이터베이스(RDBMS)** 중 하나로, 오픈소스이며 강력한 기능을 제공한다.

| 데이터베이스 | 특징 | 주 사용처 |
|------------|------|----------|
| **PostgreSQL** | 오픈소스, 표준 준수, 확장성 | 웹 서비스, 데이터 분석 |
| MySQL | 빠름, 가벼움 | 웹 애플리케이션 |
| SQLite | 파일 기반, 설치 불필요 | 모바일, 소규모 앱 |
| MongoDB | NoSQL, 유연한 스키마 | 빅데이터, 실시간 분석 |

### SQL 기본 개념

**테이블 구조:**

```
users 테이블
┌────┬──────────┬────────────────────┐
│ id │ name     │ email              │ ← 컬럼(Column)
├────┼──────────┼────────────────────┤
│ 1  │ 김철수    │ kim@example.com    │ ← 로우(Row)
│ 2  │ 이영희    │ lee@example.com    │
└────┴──────────┴────────────────────┘
```

**기본 SQL 명령어:**

```sql
-- 테이블 생성
CREATE TABLE users (
    id SERIAL PRIMARY KEY,      -- 자동 증가 ID
    name VARCHAR(100) NOT NULL, -- 문자열 (최대 100자)
    email VARCHAR(255) UNIQUE,  -- 중복 불가
    created_at TIMESTAMP DEFAULT NOW()  -- 생성 시각
);

-- 데이터 삽입 (Create)
INSERT INTO users (name, email)
VALUES ('김철수', 'kim@example.com');

-- 데이터 조회 (Read)
SELECT * FROM users;
SELECT * FROM users WHERE id = 1;

-- 데이터 수정 (Update)
UPDATE users SET name = '김영희' WHERE id = 1;

-- 데이터 삭제 (Delete)
DELETE FROM users WHERE id = 1;
```

**주요 데이터 타입:**

| SQL 타입 | Python 타입 | 설명 |
|----------|------------|------|
| `INTEGER` / `SERIAL` | `int` | 정수 (SERIAL은 자동 증가) |
| `VARCHAR(n)` | `str` | 문자열 (최대 n자) |
| `TEXT` | `str` | 긴 문자열 (길이 제한 없음) |
| `BOOLEAN` | `bool` | 참/거짓 |
| `TIMESTAMP` | `datetime` | 날짜+시간 |
| `JSON` / `JSONB` | `dict` | JSON 데이터 |

---

## 5. FastAPI와 DB 연결

### 필요한 패키지

```bash
cd week2

# SQLAlchemy: ORM 라이브러리
# psycopg2-binary: PostgreSQL 드라이버
uv add sqlalchemy psycopg2-binary
```

### ORM이란?

**ORM (Object-Relational Mapping):**
객체(Python 클래스)와 관계형 DB 테이블을 자동으로 매핑해주는 기술

**ORM 없이 (순수 SQL):**
```python
import psycopg2

conn = psycopg2.connect("postgresql://user:pass@localhost/db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = %s", (1,))
result = cursor.fetchone()
user = {"id": result[0], "name": result[1], "email": result[2]}  # 수동 매핑
```

**ORM 사용 (SQLAlchemy):**
```python
from sqlalchemy.orm import Session

user = session.query(User).filter(User.id == 1).first()
print(user.name)  # 자동으로 객체로 변환
```

**ORM의 장점:**
- ✅ SQL 문법 몰라도 Python으로 쿼리 작성
- ✅ 데이터베이스 변경 시 코드 수정 최소화
- ✅ SQL 인젝션 공격 자동 방어
- ✅ 타입 안전성 (IDE 자동완성, 타입 체크)

**ORM의 단점:**
- ❌ 복잡한 쿼리는 SQL이 더 직관적일 수 있음
- ❌ 성능 최적화가 어려울 수 있음 (N+1 문제 등)

### 프로젝트 구조

```
week2/
├── docker-compose.yml      # Docker 설정
├── .env                    # 환경 변수 (DB 접속 정보)
├── pyproject.toml          # 의존성 관리
├── main.py                 # FastAPI 앱
├── database.py             # DB 연결 설정
└── models.py               # DB 모델 (테이블 정의)
```

### database.py - DB 연결 설정

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 데이터베이스 URL
# postgresql://사용자:비밀번호@호스트:포트/DB명
DATABASE_URL = "postgresql://fastapi_user:fastapi_pass@localhost:5432/fastapi_db"

# 엔진 생성 (DB와의 연결 풀)
engine = create_engine(DATABASE_URL)

# 세션 팩토리 (DB 작업 단위)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 베이스 클래스
Base = declarative_base()

# 의존성 주입용 함수
def get_db():
    """요청마다 DB 세션을 생성하고 종료"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**핵심 개념:**

| 구성요소 | 역할 |
|---------|------|
| `engine` | DB와의 실제 연결을 관리하는 엔진 |
| `SessionLocal` | DB 작업을 위한 세션 생성 팩토리 |
| `Base` | 모델 클래스가 상속받을 기본 클래스 |
| `get_db()` | FastAPI 의존성 주입으로 세션 제공 |

### models.py - DB 모델 정의

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    """users 테이블"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**컬럼 옵션:**

| 옵션 | 의미 |
|------|------|
| `primary_key=True` | 기본 키 (ID) |
| `index=True` | 인덱스 생성 (검색 속도 향상) |
| `unique=True` | 중복 불가 |
| `nullable=False` | NULL 허용 안 함 (필수) |
| `server_default` | DB 기본값 |

### main.py - CRUD API 구현

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, get_db, Base
from models import User

# 앱 시작 시 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="2주차 - DB 연동")

# Pydantic 스키마
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True  # ORM 모델 → Pydantic 변환 허용
```

---

#### Pydantic Config 클래스 이해하기

**Config 클래스란?**

Pydantic 모델의 **동작 방식을 설정**하는 내부 클래스입니다.
ORM 연동, API 문서 예제, 검증 방식 등을 제어합니다.

##### 1️⃣ `json_schema_extra` - Swagger 문서용 예제

```python
class UserCreate(BaseModel):
    name: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "김철수",
                "email": "kim@example.com",
            }
        }
```

**역할:**
- FastAPI의 Swagger UI (`/docs`)에서
- Request Body 예제를 자동으로 보여주기 위한 설정

**효과:**

Swagger에서 이렇게 표시됨:

```json
{
  "name": "김철수",
  "email": "kim@example.com"
}
```

→ **API 문서 가독성** + **프론트/테스터 편의성** 증가

---

##### 2️⃣ `from_attributes = True` - ORM 객체 → Pydantic 변환 ⭐

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True  # 중요!
```

**역할 (매우 중요!):**

SQLAlchemy ORM 객체를 그대로 반환해도
Pydantic이 알아서 필드를 매핑해서 JSON으로 변환하게 해줌

**없으면 생기는 문제:**

```python
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user  # SQLAlchemy ORM 객체
    # ❌ 에러 발생: value is not a valid dict
```

**이 설정이 있으면:**

```python
class Config:
    from_attributes = True  # ← 이게 있으면

# Pydantic이 내부적으로 이렇게 처리:
{
    "id": db_user.id,        # 객체의 속성(attribute)에서 값 추출
    "name": db_user.name,
    "email": db_user.email
}
```

→ ORM 객체의 **속성(attribute)**에서 값을 꺼내서 자동 매핑

**참고:** Pydantic v1에서는 `orm_mode = True`라고 불렸음

---

##### 3️⃣ 실무에서 자주 쓰는 Config 옵션

```python
from pydantic import BaseModel

class StrictUser(BaseModel):
    name: str
    email: str

    class Config:
        # ORM 객체 지원 (SQLAlchemy)
        from_attributes = True

        # Swagger 예제 표시
        json_schema_extra = {
            "example": {"name": "김철수", "email": "kim@example.com"}
        }

        # 정의되지 않은 필드 입력 금지
        extra = "forbid"  # {"name": "...", "extra_field": "..."} → 에러

        # 필드 재할당 시에도 검증
        validate_assignment = True

        # 필드 별칭 허용
        populate_by_name = True  # alias와 실제 필드명 둘 다 허용
```

**주요 옵션 정리:**

| 옵션 | 설명 | 언제 사용? |
|------|------|-----------|
| `from_attributes = True` | ORM 객체 → Pydantic 자동 변환 | **SQLAlchemy 사용 시 필수** |
| `json_schema_extra` | Swagger 예제 표시 | API 문서 개선 |
| `extra = "forbid"` | 정의되지 않은 필드 금지 | 엄격한 입력 검증 필요 시 |
| `extra = "allow"` | 추가 필드 허용 | 유연한 입력 허용 |
| `validate_assignment = True` | 재할당 시 검증 | 값 변경 시 타입 체크 필요 시 |
| `populate_by_name = True` | 별칭과 원래 이름 둘 다 허용 | 레거시 호환 |

---

##### 4️⃣ 실전 예제 - Config 조합

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    """유저 생성 요청"""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    class Config:
        # Swagger 예제
        json_schema_extra = {
            "example": {
                "name": "김철수",
                "email": "kim@example.com"
            }
        }
        # 추가 필드 금지 (보안)
        extra = "forbid"


class UserResponse(BaseModel):
    """유저 응답"""
    id: int
    name: str
    email: str

    class Config:
        # ORM 객체 변환 필수!
        from_attributes = True


# API에서 사용
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user  # ← from_attributes=True 덕분에 ORM 객체 그대로 반환 가능
```

---

##### 5️⃣ 핵심 요약

| Config 설정 | 의미 | 왜 필요한가? |
|------------|------|-------------|
| `json_schema_extra` | Swagger 예제 표시 | API 문서 개선 |
| `from_attributes = True` | ORM → Pydantic 자동 변환 | `return db_user` 가능하게 함 |
| `extra = "forbid"` | 정의 안 된 필드 금지 | 보안 강화 |
| `validate_assignment` | 재할당 시 검증 | 타입 안정성 |

**한 줄 요약:**

> **Config는 Pydantic 모델의 "동작 규칙과 옵션"을 정의하는 설정 클래스다.**
> ORM 연동 + Swagger 문서 + 검증 방식 등을 제어한다.

---

```python
# 이어서 CRUD API 구현

# Create
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 체크
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다")

    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # DB에서 생성된 ID 등을 다시 로드
    return db_user

# Read (전체)
@app.get("/users", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Read (단일)
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    return user

# Update
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    db.delete(db_user)
    db.commit()
    return {"message": "삭제 완료", "deleted_id": user_id}
```

**의존성 주입 (Dependency Injection):**

```python
def create_user(user: UserCreate, db: Session = Depends(get_db)):
                                    ↑
                          FastAPI가 자동으로 get_db() 실행해서
                          DB 세션을 주입해줌
```

---

## 6. 환경 변수 관리

### .env 파일 사용

DB 접속 정보를 코드에 하드코딩하면 보안 문제가 발생한다.

**잘못된 방법:**
```python
# main.py
DATABASE_URL = "postgresql://fastapi_user:fastapi_pass@localhost:5432/fastapi_db"
# ❌ 비밀번호가 코드에 노출
# ❌ Git에 커밋되면 위험
```

**올바른 방법:**
```bash
# .env (Git에 커밋 안 함)
DATABASE_URL=postgresql://fastapi_user:fastapi_pass@localhost:5432/fastapi_db
```

```python
# database.py
from os import getenv
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드
DATABASE_URL = getenv("DATABASE_URL")
```

**.gitignore에 추가:**
```
.env
__pycache__/
.venv/
```

---

## 7. 실습 순서

### 1단계: Docker로 PostgreSQL 실행

```bash
cd week2

# docker-compose.yml 작성 후
docker compose up -d

# 상태 확인
docker compose ps
docker compose logs

# PostgreSQL 접속 테스트
docker compose exec db psql -U fastapi_user -d fastapi_db
# \dt  ← 테이블 목록
# \q   ← 종료
```

### 2단계: 패키지 설치 및 코드 작성

```bash
# 의존성 설치
uv add fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv

# 파일 작성
# - database.py
# - models.py
# - main.py
```

### 3단계: 서버 실행 및 테스트

```bash
uv run uvicorn main:app --reload --host 0.0.0.0

# http://localhost:8000/docs 에서 테스트
```

### 4단계: 데이터 영속성 확인

```bash
# 1. 유저 생성
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "김철수", "email": "kim@example.com"}'

# 2. 서버 재시작
# Ctrl+C 후 다시 실행

# 3. 데이터 확인 (여전히 존재!)
curl http://localhost:8000/users
```

---

## 8. 주요 차이점 정리

### Week1 (메모리) vs Week2 (DB)

| 구분 | Week1 (메모리) | Week2 (DB) |
|------|---------------|-----------|
| **데이터 저장** | `dict` (메모리) | PostgreSQL (디스크) |
| **영속성** | ❌ 서버 재시작 시 삭제 | ✅ 영구 저장 |
| **동시성** | ❌ 멀티 프로세스 불가 | ✅ 트랜잭션 지원 |
| **검색** | 반복문으로 직접 검색 | ✅ SQL 쿼리, 인덱싱 |
| **코드 복잡도** | 간단 | 중간 (ORM 사용) |

**코드 비교:**

```python
# Week1: 메모리
fake_db = {1: {"id": 1, "name": "김철수"}}
user = fake_db[1]

# Week2: DB
user = db.query(User).filter(User.id == 1).first()
```

---

## 9. 다음 단계 (심화)

시간이 남으면 추가로 학습:

1. **Alembic**: DB 스키마 마이그레이션 도구
2. **환경별 설정**: 개발/운영 환경 분리
3. **Connection Pool**: DB 연결 최적화
4. **Soft Delete**: 실제 삭제 대신 플래그로 표시
5. **관계(Relationship)**: 1:N, N:M 관계 설정

---

## 정리

오늘 배운 것:

- [x] Docker는 격리된 환경에서 애플리케이션을 실행하는 컨테이너 기술
- [x] Docker Compose로 여러 서비스를 정의하고 실행
- [x] PostgreSQL은 강력한 오픈소스 관계형 데이터베이스
- [x] ORM(SQLAlchemy)으로 Python 객체를 DB 테이블과 매핑
- [x] 의존성 주입(`Depends`)으로 DB 세션을 자동으로 관리
- [x] 환경 변수로 민감 정보를 코드와 분리
- [x] 메모리 기반 CRUD를 DB 기반 CRUD로 전환

**핵심 변화:**
```
Week1: dict (메모리)  →  Week2: PostgreSQL (디스크)
→ 진짜 서비스처럼 데이터가 영구 저장됨!
```

다음 주: 테스트 작성하기!
