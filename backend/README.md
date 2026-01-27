# 파이썬 백엔드 기본기 4주 과정

> 주 1회 40분 / FastAPI + Docker + PostgreSQL

## 목표

FastAPI로 CRUD 백엔드가 어떻게 만들어지고,
실제 서비스 형태(테스트·DB·도커)까지 한 번은 경험해본다.

## 커리큘럼

| 주차 | 주제 | 핵심 |
|------|------|------|
| [1주차](./week1/) | 백엔드 감 잡기 + FastAPI 첫 실행 | uv, FastAPI, /docs |
| [2주차](./week2/) | CRUD로 백엔드답게 만들기 | Pydantic, 메모리 CRUD |
| [3주차](./week3/) | DB 연결해서 진짜 서비스처럼 | Docker, PostgreSQL, ORM |
| [4주차](./week4/) | 테스트와 정리 | pytest, 전체 흐름 정리 |

## 학습 흐름

```
1주차: FastAPI만 (uv run)
    ↓
2주차: + CRUD (아직 메모리)
    ↓
3주차: + Docker + DB (영구 저장)
    ↓
4주차: + 테스트 (품질 보장)
```

## 사전 준비

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 설치
- Docker Desktop (3주차부터)

```bash
# uv 설치 (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 설치 확인
uv --version
```
