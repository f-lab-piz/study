## Adaptive TPS 데모 - ThreadPoolExecutor 기반

FastAPI 서버와 ThreadPoolExecutor 기반의 클라이언트로 구성된 데모입니다. 클라이언트는 API 요청(I/O-bound)과 CPU-bound 작업을 분리하여 처리하며, 토큰 버킷을 통한 Rate Limiting과 실시간 모니터링 기능을 제공합니다.

## 주요 특징

- **I/O와 CPU 작업 분리**: asyncio로 API 요청 처리, ThreadPoolExecutor로 CPU 작업 처리
- **Rate Limiting**: 토큰 버킷 알고리즘으로 초당 API 요청 제한
- **실시간 모니터링**: 초당 API 요청 수, 처리 완료 수, 큐 작업 수 출력
- **성능 튜닝 가능**: 워커 수, 작업 시간, API 호출 제한을 CLI로 조정

## 1. 환경 설정

```bash
cd example/case1

# uv를 사용한 환경 설정
uv init --no-readme --no-workspace
uv add fastapi httpx "uvicorn[standard]"
```

## 2. 서버 실행

`server.py`의 `ERROR_MODE` 값을 변경하여 오류 주입을 제어할 수 있습니다:
- `False`: 모든 요청에 200 응답
- `True`: 1% 확률로 503 오류 발생

```bash
# 서버 실행
uv run uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## 3. 클라이언트 실행

### 기본 실행

```bash
uv run python client.py
```

### 파라미터 커스터마이징

```bash
# 워커 수, 작업 시간, API 호출 제한 조정
uv run python client.py --workers 16 --work-time 0.1 --rate-limit 100
```

### CLI 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--workers` | ThreadPoolExecutor 워커 스레드 수 | 8 |
| `--consumers` | 동시 실행할 컨슈머 수 | 4 |
| `--work-time` | 워커에서 처리하는 작업 시간(초) | 0.2 |
| `--rate-limit` | 초당 API 호출 제한 횟수 (프로듀서) | 60 |
| `--queue-size` | 작업 큐의 최대 크기 | 200 |

### 예제 실행 명령어

```bash
# 기본 설정으로 실행
uv run python client.py

# 컨슈머 늘려서 API 요청 속도 향상
uv run python client.py --consumers 8 --workers 16 --rate-limit 100

# 작업 시간 길게, 워커 적게 (병목 테스트)
uv run python client.py --workers 4 --work-time 0.5 --rate-limit 30

# 큐 크기 작게 설정 (백프레셔 테스트)
uv run python client.py --queue-size 50 --rate-limit 100

# 도움말 보기
uv run python client.py --help
```

## 4. 모니터링 출력

실행 중 1초마다 다음 정보가 출력됩니다:

```
[Stats] API 요청/초:  36 | 처리완료/초:  36 | 큐 작업수: 111
```

- **API 요청/초**: 서버로 전송한 HTTP 요청 수
- **처리완료/초**: CPU-bound 작업까지 완료한 건수
- **큐 작업수**: 현재 큐에 대기 중인 작업 개수

## 5. 성능 튜닝 가이드

### 핵심 변수 이해

1. **컨슈머 수 (`--consumers`)**: **동시 처리 작업 수**를 결정
   - 각 컨슈머는 독립적인 asyncio 태스크로 작업을 순차 처리
   - 컨슈머 4개 = 동시에 4개 작업 처리 (API 요청 + CPU 작업)
   - **동시성 제어의 핵심**: 컨슈머 수로 시스템 부하 제어
   - 주의: 컨슈머가 너무 많으면 워커 대기로 비효율

2. **워커 수 (`--workers`)**: CPU-bound 작업의 병렬 처리 수
   - 이론적 최대 처리량 = workers / work_time
   - 예: 워커 8개, 작업 0.1초 → 최대 80/초

3. **Rate Limit (`--rate-limit`)**: 프로듀서가 큐에 넣는 속도
   - 컨슈머 처리 속도보다 높으면 큐가 계속 증가
   - 너무 낮으면 시스템 자원이 놀게 됨

4. **큐 크기 (`--queue-size`)**: 백프레셔 제어
   - 큐가 가득 차면 프로듀서가 대기
   - 메모리 사용량과 응답성의 트레이드오프

### 성능 최적화 시나리오

#### API 요청 속도를 높이려면
```bash
# 컨슈머를 늘려서 동시 API 요청 증가
uv run python client.py --consumers 8 --rate-limit 100
```

#### 처리 완료 속도를 높이려면
```bash
# 워커를 늘리고 작업 시간 단축
uv run python client.py --workers 16 --work-time 0.1
```

#### 메모리 사용량을 줄이려면
```bash
# 큐 크기를 줄여서 대기 작업 감소
uv run python client.py --queue-size 50
```

### 병목 구간 확인

**증상**: API 요청/초가 매우 낮음 (예: 9/초)
- **원인**: 컨슈머 수가 부족 (예: 1개)
- **해결**: `--consumers` 증가
- **예**: 컨슈머 1개 → 9/초, 컨슈머 8개 → 72/초

**증상**: 처리완료/초 < API 요청/초
- **원인**: 워커 수 부족 또는 작업 시간이 너무 김
- **해결**: `--workers` 증가 또는 `--work-time` 감소
- **예**: 워커 4개 (0.1초) → 40/초, 워커 16개 → 160/초

**증상**: 큐 작업수가 계속 증가
- **원인**: Rate limit이 처리 속도보다 높음
- **해결**: `--rate-limit` 감소 또는 컨슈머/워커 증가

### 최적 설정 가이드

**기본 공식**:
```
컨슈머 수 ≈ 목표 동시성 (보통 4~16)
워커 수 ≈ (목표 TPS) × (작업 시간)
```

**예시**: 초당 100개 처리 목표, 작업 시간 0.1초
```bash
uv run python client.py --consumers 8 --workers 16 --rate-limit 100
# 컨슈머 8개가 동시에 작업
# 워커 16개로 100/초 처리 (16 / 0.1 = 160/초 여유)
```
