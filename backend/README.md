# 파이썬 백엔드 멘토링 자료

> FastAPI + PostgreSQL + 테스트 + AI 연동 + 프로젝트 시작 설계

## 목표

FastAPI로 CRUD 백엔드가 어떻게 만들어지고,
DB/테스트/AI 연동까지 어떻게 확장되는지 본 뒤,
실제 프로젝트를 어떤 순서로 시작해야 하는지까지 연결한다.

## 커리큘럼

| 주차 | 주제 | 핵심 |
|------|------|------|
| [1주차](./week1/) | 백엔드 감 잡기 + CRUD 구현 | uv, FastAPI, Pydantic, 메모리 CRUD |
| [2주차](./week2/) | DB 연결해서 진짜 서비스처럼 | Docker, PostgreSQL, ORM |
| [3주차](./week3/) | 테스트와 정리 | pytest, 테스트 격리, Locust |
| [4주차](./week4/) | AI 기능 붙여보기 | OpenAI API, Tool Calling, LangChain, LangGraph |
| [5주차](./week5/) | 상태 관리와 프로젝트 시작 | 상태 관리, 멱등성, MVP 설계 |

## 보강 주제

정규 주차와 별도로 아래 개념을 보강해서 연결할 수 있다.

- 낙관적 락
- 비관적 락
- 분산 락
- EC2
- RDS
- S3

## 학습 흐름

```
1주차: FastAPI + CRUD (메모리)
    ↓
2주차: + Docker + DB (영구 저장)
    ↓
3주차: + 테스트 (품질 보장)
    ↓
4주차: + AI API / Agent 기초
    ↓
5주차: + 상태 관리 + 멱등성 + MVP 설계
```

## Week5의 역할

Week5는 이미 배운 기술 위에 실무 감각을 얹는 주차다.

핵심은 아래 세 가지다.

- 상태를 왜 관리해야 하는지 이해한다
- 같은 요청이 여러 번 와도 왜 안전해야 하는지 이해한다
- 그래서 지금 무엇부터 만들지 결정한다

즉, 이번 주에는 아래 흐름을 연결해서 본다.

```text
상태 관리 -> 멱등성 -> MVP 설계
```

## 사전 준비

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) 설치
- Docker Desktop (2주차부터)
- OpenAI API Key (4주차부터)

```bash
# uv 설치 (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 설치 확인
uv --version
```
