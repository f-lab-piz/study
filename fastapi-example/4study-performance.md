# 성능 테스트 학습 가이드 (Locust)

## 🚀 빠른 시작 (Quick Start)

```bash
# 1. 프로젝트 디렉토리로 이동
cd fastapi-example

# 2. Docker Compose로 전체 스택 시작
docker-compose up --build -d

# 3. Locust 실행 (TodoUser 클래스만 사용)
docker-compose exec -T fastapi-app bash -c "uv run locust -f locustfile.py --headless --users 20 --spawn-rate 5 --run-time 15s --host http://localhost:8000 TodoUser"
```

**기대 결과:**
- 👥 사용자: 20명
- 📊 총 요청: 약 130개
- ✅ 실패율: 0%
- ⚡ 평균 응답 시간: 약 8-15ms

### Locust 웹 UI 실행 (선택)

```bash
# 웹 UI 모드로 실행
docker-compose exec fastapi-app uv run locust -f locustfile.py

# 브라우저에서 http://localhost:8089 접속
# 설정:
# - Number of users: 20
# - Spawn rate: 5
# - Host: http://localhost:8000
```

---

## 📝 실습 과제

[locustfile.py](locustfile.py)에는 **완성된 시나리오**와 **TODO 시나리오**가 있습니다.

### 과제 진행 방법

1. **완성된 시나리오 먼저 이해하기**
   ```python
   # TodoUser 클래스의 완성된 메서드들:
   - create_todo()     # TODO 생성 (가중치 3)
   - list_todos()      # 리스트 조회 (가중치 2)
   - get_single_todo() # 개별 조회 (가중치 1)
   ```

2. **TODO 메서드 찾기**
   ```bash
   grep -n "TODO:" locustfile.py
   ```

3. **TODO 메서드 하나씩 완성하기**
   - `update_todo()` - TODO 수정 시나리오
   - `delete_todo()` - TODO 삭제 시나리오
   - `MixedWorkloadUser.complete_workflow()` - 복잡한 워크플로우
   - `StressTestUser` - 스트레스 테스트 시나리오

4. **완성한 시나리오 테스트**
   ```bash
   # 모든 User 클래스 실행 (완성 후)
   docker-compose exec fastapi-app uv run locust -f locustfile.py --headless --users 30 --spawn-rate 10 --run-time 20s --host http://localhost:8000
   ```

### 실습 체크리스트

#### TodoUser 클래스 ([locustfile.py](locustfile.py))
- [x] `create_todo()` - ✅ 완성됨 (예시)
- [x] `list_todos()` - ✅ 완성됨 (예시)
- [x] `get_single_todo()` - ✅ 완성됨 (예시)
- [ ] `update_todo()` - TODO 수정 시나리오 완성하기
- [ ] `delete_todo()` - TODO 삭제 시나리오 완성하기

#### 추가 시나리오
- [ ] `MixedWorkloadUser` - 복잡한 워크플로우 시나리오
  - 여러 TODO 생성 → 리스트 조회 → 일부 완료 처리 → 삭제
- [ ] `StressTestUser` - 스트레스 테스트 시나리오
  - wait_time 최소화, 대량 데이터 생성

### 실습 예시: update_todo() 완성하기

```python
@task(1)
def update_todo(self):
    """TODO 수정 시나리오"""
    if not self.created_todo_ids:
        return

    todo_id = random.choice(self.created_todo_ids)

    # 업데이트 데이터 작성
    update_data = {
        "title": f"수정된 제목 {random.randint(1, 1000)}",
        "completed": random.choice([True, False])
    }

    # PUT 요청 작성
    with self.client.put(
        f"/todos/{todo_id}",
        json=update_data,
        name="/todos/{id} [PUT - Update]",
        catch_response=True
    ) as response:
        if response.status_code == 200:
            response.success()
        elif response.status_code == 404:
            response.success()  # 이미 삭제된 TODO
        else:
            response.failure(f"수정 실패: {response.status_code}")
```

---

## 목차
1. [성능 테스트가 필요한 이유](#성능-테스트가-필요한-이유)
2. [성능 테스트의 종류](#성능-테스트의-종류)
3. [Locust 소개](#locust-소개)
4. [핵심 개념](#핵심-개념)
5. [Locust 시나리오 작성](#locust-시나리오-작성)
6. [실행 및 결과 분석](#실행-및-결과-분석)
7. [실습](#실습)
8. [성능 최적화 팁](#성능-최적화-팁)

---

## 성능 테스트가 필요한 이유

### 성능 문제는 언제 발견될까?

```
개발 환경    ✅ 빠름 (사용자 1명)
  ↓
테스트 환경  ✅ 괜찮음 (사용자 10명)
  ↓
프로덕션     💥 느림! (사용자 1000명)
```

### 성능 테스트 없이 배포할 때의 문제

```python
# ❌ 성능 테스트 없이 배포
- 서버 다운 (트래픽 폭주 시)
- 느린 응답 (사용자 이탈)
- 비용 폭증 (서버 스케일링)
- 신뢰도 하락

# ✅ 성능 테스트 후 배포
- 예상 트래픽 처리 가능 확인
- 병목 지점 사전 파악
- 최적화 후 배포
- 안정적인 서비스
```

### 성능 테스트의 목적

1. **시스템 한계 파악**: 얼마나 많은 사용자를 처리할 수 있나?
2. **병목 지점 발견**: 어디가 느린가? (DB? API? 네트워크?)
3. **안정성 검증**: 장시간 운영 시 문제는 없나?
4. **용량 계획**: 필요한 서버 스펙은?
5. **SLA 달성**: 응답 시간 목표를 만족하나?

---

## 성능 테스트의 종류

### 1. 부하 테스트 (Load Test)

**정상적인 부하에서의 성능 측정**

```
사용자 수
  │
  │     ┌─────────────┐
  │    ╱               ╲
  │   ╱                 ╲
  │  ╱                   ╲
  │ ╱                     ╲
  └─────────────────────────→ 시간
    증가    유지    감소

목적: 예상 트래픽에서 잘 동작하는가?
예시: 평소 사용자 100명 → 테스트 100명
```

### 2. 스트레스 테스트 (Stress Test)

**시스템의 한계점 찾기**

```
사용자 수
  │
  │                 ╱
  │               ╱
  │             ╱
  │           ╱
  │         ╱
  │       ╱
  │     ╱
  │   ╱
  └─────────────────→ 시간
    계속 증가 (한계까지)

목적: 시스템이 언제 무너지는가?
예시: 100 → 200 → 500 → 1000 → 💥
```

### 3. 스파이크 테스트 (Spike Test)

**급격한 트래픽 변화 대응**

```
사용자 수
  │
  │       ┌─┐
  │       │ │
  │       │ │
  │ ──────┘ └────────
  │
  └─────────────────→ 시간
    급증   급감

목적: 갑작스런 트래픽 증가에 대응 가능한가?
예시: 이벤트, 뉴스 등으로 트래픽 폭증
```

### 4. 내구성 테스트 (Endurance/Soak Test)

**장시간 운영 안정성**

```
사용자 수
  │
  │ ────────────────────
  │
  │
  └─────────────────────→ 시간
    일정 부하 유지 (수시간~일)

목적: 메모리 누수, 성능 저하는 없는가?
예시: 100명 부하를 24시간 유지
```

---

## Locust 소개

### Locust란?

**Python 기반의 오픈소스 부하 테스트 도구**

```python
from locust import HttpUser, task

class MyUser(HttpUser):
    @task
    def hello(self):
        self.client.get("/")
```

### 다른 도구와 비교

| 특성 | Locust | JMeter | k6 | Apache Bench |
|------|--------|--------|-----|--------------|
| 언어 | Python | Java | JavaScript | C |
| 코드 기반 | ✅ | ❌ (GUI) | ✅ | ❌ (CLI) |
| 확장성 | 우수 | 좋음 | 우수 | 제한적 |
| 학습 곡선 | 낮음 | 중간 | 낮음 | 매우 낮음 |
| 웹 UI | ✅ | ✅ | ❌ | ❌ |

### Locust의 장점

1. **Python 코드**: 프로그래밍 언어로 시나리오 작성
2. **간단한 문법**: 몇 줄로 복잡한 시나리오 작성
3. **웹 UI**: 실시간 모니터링 및 차트
4. **분산 테스트**: 여러 서버에서 동시 실행 가능
5. **확장성**: Python 생태계 활용 가능

---

## 핵심 개념

### 1. HttpUser

**가상 사용자 클래스**

```python
from locust import HttpUser

class TodoUser(HttpUser):
    """
    하나의 가상 사용자를 나타냄
    - 각 사용자는 독립적으로 동작
    - self.client로 HTTP 요청
    """
    pass
```

### 2. Task

**사용자가 수행하는 작업**

```python
from locust import task

class TodoUser(HttpUser):
    @task
    def get_todos(self):
        """
        @task: 이 메서드를 반복 실행
        """
        self.client.get("/todos/")

    @task(3)  # 가중치 3
    def create_todo(self):
        """
        가중치 3: get_todos보다 3배 자주 실행
        """
        self.client.post("/todos/", json={"title": "테스트"})
```

### 3. Wait Time

**태스크 사이 대기 시간**

```python
from locust import between, constant

class TodoUser(HttpUser):
    # 1~3초 사이 랜덤 대기 (실제 사용자처럼)
    wait_time = between(1, 3)

    # 또는 고정 대기 시간
    # wait_time = constant(2)  # 항상 2초
```

### 4. On Start/Stop

**사용자 생명주기 훅**

```python
class TodoUser(HttpUser):
    def on_start(self):
        """
        각 사용자 시작 시 한 번 실행
        예: 로그인, 초기 설정
        """
        self.client.post("/login", json={"username": "user"})

    def on_stop(self):
        """
        각 사용자 종료 시 실행
        예: 로그아웃, 정리 작업
        """
        self.client.post("/logout")
```

### 5. Catch Response

**응답 성공/실패 커스터마이징**

```python
@task
def create_todo(self):
    with self.client.post(
        "/todos/",
        json={"title": "테스트"},
        catch_response=True
    ) as response:
        if response.status_code == 201:
            # 성공
            response.success()
        else:
            # 실패로 기록
            response.failure(f"생성 실패: {response.status_code}")
```

---

## Locust 시나리오 작성

### 기본 시나리오

[locustfile.py](locustfile.py) 파일 참조

```python
from locust import HttpUser, task, between

class TodoUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def create_todo(self):
        """TODO 생성 (가중치 3)"""
        self.client.post("/todos/", json={
            "title": "성능 테스트",
            "completed": False
        })

    @task(1)
    def list_todos(self):
        """TODO 리스트 조회 (가중치 1)"""
        self.client.get("/todos/")
```

### 복잡한 워크플로우

```python
class UserJourneyUser(HttpUser):
    wait_time = between(2, 5)

    @task
    def complete_user_journey(self):
        """
        실제 사용자의 전체 여정 시뮬레이션
        """
        # 1. 리스트 조회
        response = self.client.get("/todos/")

        # 2. TODO 생성
        create_response = self.client.post("/todos/", json={
            "title": "새 할일",
            "completed": False
        })

        if create_response.status_code == 201:
            todo_id = create_response.json()["id"]

            # 3. 생성한 TODO 조회
            self.client.get(f"/todos/{todo_id}")

            # 4. TODO 완료 처리
            self.client.put(f"/todos/{todo_id}", json={
                "completed": True
            })

            # 5. 삭제
            self.client.delete(f"/todos/{todo_id}")
```

---

## 실행 및 결과 분석

### Docker 컨테이너에서 실행

```bash
# 1. Docker Compose로 스택 시작
docker-compose up --build -d

# 2. Locust 실행 (웹 UI 모드)
docker-compose exec fastapi-app locust -f locustfile.py

# 3. 브라우저에서 접속
# http://localhost:8089
```

### Locust 웹 UI 설정

1. **Number of users**: 시뮬레이션할 총 사용자 수
   - 부하 테스트: 50~100
   - 스트레스 테스트: 500~1000

2. **Spawn rate**: 초당 증가할 사용자 수
   - 부드러운 증가: 10 users/sec
   - 급격한 증가: 50~100 users/sec

3. **Host**: 테스트 대상 URL
   - `http://fastapi-app:8000` (Docker 네트워크 내부)
   - 또는 `http://localhost:8000`

### 주요 메트릭 이해

#### 1. Request Statistics

| 메트릭 | 의미 | 목표 |
|--------|------|------|
| **Total Requests** | 총 요청 수 | - |
| **RPS** (Requests/sec) | 초당 요청 수 | 높을수록 좋음 |
| **Failures** | 실패한 요청 수 | 0에 가까울수록 좋음 |
| **Median (ms)** | 응답 시간 중앙값 | < 200ms |
| **95%ile (ms)** | 95% 사용자 응답 시간 | < 500ms |
| **99%ile (ms)** | 99% 사용자 응답 시간 | < 1000ms |

#### 2. Response Time Chart

```
응답 시간 (ms)
  │
  │     ┌───┐
  │   ╱ │   │ ╲
  │  ╱  │   │  ╲
  │ ╱   │   │   ╲
  └─────────────────→ 시간

초록색: 정상 (< 500ms)
노란색: 주의 (500-1000ms)
빨간색: 느림 (> 1000ms)
```

#### 3. Failures

```
에러 타입별 분류:
- 500 Internal Server Error: 서버 오류
- 404 Not Found: 리소스 없음
- Connection Error: 서버 연결 실패
- Timeout: 응답 시간 초과
```

### CLI 모드 (헤드리스)

```bash
# UI 없이 자동으로 테스트 실행
docker-compose exec fastapi-app locust \
  -f locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 1m \
  --host http://fastapi-app:8000

# HTML 리포트 생성
docker-compose exec fastapi-app locust \
  -f locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 1m \
  --host http://fastapi-app:8000 \
  --html report.html
```

---

## 실습

### 실습 1: 기본 시나리오 실행

1. **Locust 시작**
   ```bash
   docker-compose exec fastapi-app locust -f locustfile.py
   ```

2. **웹 UI 접속**
   - http://localhost:8089

3. **테스트 설정**
   - Number of users: 50
   - Spawn rate: 10
   - Host: http://fastapi-app:8000

4. **결과 관찰**
   - RPS는 얼마나 나오나?
   - 응답 시간은 어떤가?
   - 에러는 없는가?

### 실습 2: locustfile.py 완성하기

[locustfile.py](locustfile.py)의 TODO 부분을 완성하세요.

**1. `update_todo` 메서드 완성**

```python
@task(1)
def update_todo(self):
    """TODO 수정 시나리오"""
    if not self.created_todo_ids:
        return

    todo_id = random.choice(self.created_todo_ids)

    update_data = {
        "title": f"수정된 제목 {random.randint(1, 1000)}",
        "completed": random.choice([True, False])
    }

    with self.client.put(
        f"/todos/{todo_id}",
        json=update_data,
        name="/todos/{id} [PUT - Update]",
        catch_response=True
    ) as response:
        if response.status_code == 200:
            response.success()
        elif response.status_code == 404:
            response.success()  # 이미 삭제된 TODO
        else:
            response.failure(f"수정 실패: {response.status_code}")
```

**2. `delete_todo` 메서드 완성**

```python
@task(1)
def delete_todo(self):
    """TODO 삭제 시나리오"""
    if not self.created_todo_ids:
        return

    todo_id = random.choice(self.created_todo_ids)

    with self.client.delete(
        f"/todos/{todo_id}",
        name="/todos/{id} [DELETE]",
        catch_response=True
    ) as response:
        if response.status_code == 204:
            # 삭제 성공: 리스트에서 제거
            if todo_id in self.created_todo_ids:
                self.created_todo_ids.remove(todo_id)
            response.success()
        elif response.status_code == 404:
            response.success()  # 이미 삭제됨
        else:
            response.failure(f"삭제 실패: {response.status_code}")
```

**3. 새로운 시나리오 작성**

`MixedWorkloadUser` 클래스 완성:

```python
class MixedWorkloadUser(HttpUser):
    wait_time = between(2, 5)

    @task
    def complete_workflow(self):
        """전체 워크플로우"""
        # 1. TODO 3개 생성
        todo_ids = []
        for i in range(3):
            response = self.client.post("/todos/", json={
                "title": f"워크플로우 TODO {i}",
                "completed": False
            })
            if response.status_code == 201:
                todo_ids.append(response.json()["id"])

        # 2. 리스트 조회
        self.client.get("/todos/")

        # 3. 첫 번째 TODO 완료 처리
        if todo_ids:
            self.client.put(f"/todos/{todo_ids[0]}", json={
                "completed": True
            })

        # 4. 완료된 TODO 삭제
        if todo_ids:
            self.client.delete(f"/todos/{todo_ids[0]}")
```

### 실습 3: 스트레스 테스트

1. **점진적 부하 증가**
   - 시작: 10 users
   - 증가: 5분마다 +10 users
   - 최대: 500 users

2. **관찰 포인트**
   - 어느 시점에서 응답 시간이 급증하나?
   - 에러가 발생하기 시작하는 사용자 수는?
   - CPU/메모리 사용률은? (docker stats)

3. **병목 지점 찾기**
   ```bash
   # 컨테이너 리소스 모니터링
   docker stats
   ```

### 실습 4: 다양한 시나리오 비교

| 시나리오 | Users | Spawn Rate | Duration | 목적 |
|----------|-------|------------|----------|------|
| 부하 테스트 | 50 | 10 | 5분 | 정상 성능 |
| 스트레스 테스트 | 500 | 50 | 10분 | 한계 파악 |
| 스파이크 테스트 | 0→200→0 | 100 | 3분 | 급증 대응 |

---

## 성능 최적화 팁

### 병목 지점별 해결 방법

#### 1. DB 병목

**증상:**
- 사용자 증가 시 응답 시간 선형 증가
- DB CPU 사용률 높음

**해결:**
```python
# ❌ N+1 쿼리 문제
for todo in todos:
    user = db.query(User).filter(User.id == todo.user_id).first()

# ✅ 조인으로 해결
todos = db.query(TodoDB).join(User).all()

# ✅ 인덱스 추가
class TodoDB(Base):
    title = Column(String, index=True)  # 인덱스 추가
    user_id = Column(Integer, index=True)
```

#### 2. API 병목

**증상:**
- 특정 엔드포인트만 느림
- CPU 사용률 높음

**해결:**
```python
# ✅ 캐싱 (Redis 등)
from functools import lru_cache

@lru_cache(maxsize=128)
def get_expensive_data():
    # 비용이 큰 연산 캐싱
    pass

# ✅ 비동기 처리
async def get_todos():
    # async/await로 I/O 병목 해결
    pass
```

#### 3. 네트워크 병목

**증상:**
- 응답 크기가 큼
- 네트워크 대역폭 포화

**해결:**
```python
# ✅ 페이지네이션
@router.get("/todos/")
def list_todos(skip: int = 0, limit: int = 100):
    # 대량 데이터를 나눠서 전송
    pass

# ✅ 압축 (gzip)
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 성능 개선 체크리스트

- [ ] DB 쿼리 최적화 (인덱스, N+1 해결)
- [ ] 캐싱 적용 (Redis, 메모리 캐시)
- [ ] 비동기 처리 (async/await)
- [ ] 커넥션 풀 설정
- [ ] 페이지네이션 구현
- [ ] 응답 압축 (gzip)
- [ ] 정적 파일 CDN 사용
- [ ] 불필요한 데이터 제거 (응답 최소화)

---

## 실전 시나리오

### 시나리오 1: 출시 전 성능 검증

**목표**: 예상 트래픽 처리 가능 여부 확인

```bash
# 예상: 동시 사용자 100명
docker-compose exec fastapi-app locust \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --host http://fastapi-app:8000

# 검증 기준:
# - 95%ile 응답 시간 < 500ms
# - 에러율 < 0.1%
# - RPS > 50
```

### 시나리오 2: 서버 용량 계획

**목표**: 서버 스펙 결정

```bash
# 단계적으로 사용자 증가시키며 테스트
# 50, 100, 200, 500, 1000 users

# 결과 분석:
# - 500 users까지 안정적
# → 서버 2대로 1000 users 처리 가능 (예상)
```

### 시나리오 3: 릴리스 후 성능 회귀 테스트

**목표**: 새 버전이 성능 저하 없는지 확인

```bash
# 1. 기존 버전 테스트 (결과 저장)
locust ... --html baseline.html

# 2. 새 버전 테스트
locust ... --html new-version.html

# 3. 비교
# - 응답 시간 차이
# - RPS 변화
# - 에러율 비교
```

---

## 트러블슈팅

### 문제 1: Locust UI에 접속 안 됨

```
Connection refused on http://localhost:8089
```

**해결:**
```bash
# docker-compose.yml에 포트 추가
services:
  fastapi-app:
    ports:
      - "8000:8000"
      - "8089:8089"  # Locust UI 포트

# Locust 실행 시 --web-port 지정
docker-compose exec fastapi-app locust -f locustfile.py --web-port 8089
```

### 문제 2: 모든 요청이 실패

```
Connection Error: Connection refused
```

**해결:**
```python
# Host 설정 확인
# ❌ 외부 URL
class TodoUser(HttpUser):
    host = "http://localhost:8000"  # 컨테이너 내부에서 안 됨

# ✅ Docker 네트워크 URL
class TodoUser(HttpUser):
    host = "http://fastapi-app:8000"  # 또는 UI에서 입력
```

### 문제 3: 테스트 중 서버 다운

```
서버가 응답하지 않음
```

**원인 파악:**
```bash
# 1. 로그 확인
docker-compose logs fastapi-app

# 2. 리소스 확인
docker stats

# 3. DB 연결 확인
docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

**해결:**
- 커넥션 풀 크기 조정
- 리소스 제한 증가 (docker-compose.yml)
- 코드 최적화

---

## 다음 단계

이 가이드를 완료했다면:

1. ✅ **프로파일링**
   - Python cProfile
   - Django Debug Toolbar
   - 코드 레벨 병목 찾기

2. ✅ **모니터링**
   - Prometheus + Grafana
   - 실시간 성능 모니터링
   - 알림 설정

3. ✅ **분산 테스트**
   - Locust Master/Worker 모드
   - 여러 서버에서 동시 테스트

4. ✅ **실제 데이터**
   - 프로덕션 로그 기반 시나리오
   - 실제 사용 패턴 반영

---

## 참고 자료

### 공식 문서
- [Locust 공식 문서](https://docs.locust.io/)
- [성능 테스트 베스트 프랙티스](https://learn.microsoft.com/en-us/azure/architecture/best-practices/performance-testing)

### 학습 리소스
- [Web Performance Testing with Locust](https://www.youtube.com/results?search_query=locust+performance+testing)
- [Performance Testing Fundamentals](https://www.guru99.com/performance-testing.html)

---

## 요약

### 핵심 개념
- **부하 테스트**: 정상 트래픽 성능 측정
- **스트레스 테스트**: 시스템 한계 파악
- **Locust**: Python 기반 부하 테스트 도구
- **메트릭**: RPS, 응답 시간, 에러율

### 주요 명령어
```bash
# Locust 웹 UI 실행
docker-compose exec fastapi-app locust -f locustfile.py

# 헤드리스 모드
docker-compose exec fastapi-app locust \
  -f locustfile.py \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --host http://fastapi-app:8000

# HTML 리포트 생성
... --html report.html
```

### 성능 목표 (예시)
- 95%ile 응답 시간: < 500ms
- 에러율: < 0.1%
- RPS: > 100 (사용자 100명 기준)
- 동시 사용자: > 1000명

---

**축하합니다!** 이제 FastAPI 애플리케이션의 성능을 측정하고 최적화하는 방법을 배웠습니다!
