# Week2 빠른 시작 가이드

## 🚀 가장 빠른 시작 (권장)

```bash
cd /workspaces/study/backend/week2

# 실행 스크립트 사용 (DB + API 서버 자동 시작)
./run.sh
```

**자동으로 처리되는 것:**
- ✅ PostgreSQL 컨테이너 시작 확인 및 자동 실행
- ✅ DB 준비 대기
- ✅ FastAPI 서버 실행 (외부 접속 가능)
- ✅ 접속 URL 자동 표시

---

## 📡 외부 PC에서 접속하기

### 현재 서버 IP 확인
```bash
# Linux/Mac
hostname -I | awk '{print $1}'

# 또는
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### 접속 URL
```
로컬 접속:     http://localhost:8000
외부 접속:     http://<서버IP>:8000
Swagger UI:   http://<서버IP>:8000/docs
```

**예시:**
- 서버 IP가 `192.168.1.100`이면
- 외부에서 `http://192.168.1.100:8000/docs` 접속

**주의사항:**
- 방화벽에서 8000 포트 허용 필요
- 같은 네트워크에 있어야 함 (또는 포트포워딩 설정)

---

## 1. PostgreSQL 실행 (Docker)

```bash
cd /workspaces/study/backend/week2

# Docker Compose로 PostgreSQL 시작
docker compose up -d

# 상태 확인
docker compose ps
docker compose logs
```

**예상 출력:**
```
NAME              IMAGE                COMMAND                  SERVICE   CREATED         STATUS                   PORTS
week2-postgres    postgres:15-alpine   "docker-entrypoint.s…"   db        5 seconds ago   Up 4 seconds (healthy)   0.0.0.0:5432->5432/tcp
```

## 2. FastAPI 서버 실행

### 방법 1: 스크립트 사용 (권장)
```bash
cd /workspaces/study/backend/week2
./run.sh  # DB 자동 시작 + 서버 실행
```

### 방법 2: 직접 실행
```bash
# week2 디렉토리에서
cd /workspaces/study/backend/week2

# 외부 접속 가능하도록 0.0.0.0으로 실행
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**⚠️ 중요:**
- `--host 0.0.0.0`: 외부 PC에서 접속 가능
- `--host 127.0.0.1`: 로컬에서만 접속 가능 (기본값)

**서버 시작 확인:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 3. API 테스트

### Swagger UI로 테스트
브라우저에서 http://localhost:8000/docs 접속

### curl로 테스트

```bash
# 1. 헬스체크 (DB 연결 확인)
curl http://localhost:8000/health

# 2. 유저 생성
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "김철수", "email": "kim@example.com"}'

# 3. 모든 유저 조회
curl http://localhost:8000/users

# 4. 특정 유저 조회
curl http://localhost:8000/users/1

# 5. 유저 수정
curl -X PUT http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "김영희"}'

# 6. 유저 삭제
curl -X DELETE http://localhost:8000/users/1

# 7. 통계 조회
curl http://localhost:8000/stats
```

## 4. DB 직접 접속 (선택사항)

```bash
# PostgreSQL 컨테이너 접속
docker compose exec db psql -U fastapi_user -d fastapi_db

# SQL 명령어
\dt              # 테이블 목록
\d users         # users 테이블 구조
SELECT * FROM users;  # 모든 유저 조회
\q               # 종료
```

## 5. 종료하기

```bash
# FastAPI 서버 종료
Ctrl + C

# PostgreSQL 컨테이너 종료
docker compose stop

# 컨테이너 완전 삭제 (데이터는 유지)
docker compose down

# 컨테이너 + 볼륨 모두 삭제 (데이터도 삭제!)
docker compose down -v
```

## 프로젝트 구조

```
week2/
├── docker-compose.yml   # PostgreSQL 컨테이너 설정
├── .env                 # 환경 변수 (DB 접속 정보)
├── .gitignore           # Git 제외 파일
├── pyproject.toml       # 의존성 관리
├── database.py          # SQLAlchemy 연결 설정
├── models.py            # User 모델 (테이블 정의)
├── main.py              # FastAPI CRUD API
└── README.md            # 학습 가이드
```

## Week1 vs Week2 비교

| 항목 | Week1 | Week2 |
|------|-------|-------|
| 저장소 | `dict` (메모리) | PostgreSQL (디스크) |
| 영속성 | ❌ 재시작 시 삭제 | ✅ 영구 저장 |
| 인프라 | 없음 | Docker Compose |
| ORM | 없음 | SQLAlchemy |
| 코드 | `fake_db[id]` | `db.query(User).filter(...)` |

## 트러블슈팅

### 1. "Port 5432 is already in use"
```bash
# 기존 PostgreSQL 중지 또는 포트 변경
# docker-compose.yml에서 포트를 5433:5432로 변경
# .env의 DATABASE_URL도 5433으로 변경
```

### 2. "could not connect to server"
```bash
# PostgreSQL이 준비될 때까지 대기 (5초 정도)
docker compose logs db

# healthcheck 확인
docker compose ps
```

### 3. DB 초기화가 필요할 때
```bash
# 모든 데이터 삭제 후 재시작
docker compose down -v
docker compose up -d
```

## 다음 단계

- [ ] Alembic으로 DB 마이그레이션
- [ ] 관계(Relationship) 추가 (1:N, N:M)
- [ ] 인증/인가 (JWT)
- [ ] 테스트 작성 (Week3에서 다룸)
