"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import todos
from app.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 관리
    시작 시: DB 테이블 생성
    종료 시: 정리 작업
    """
    # Startup: DB 초기화
    print("Initializing database...")
    init_db()
    yield
    # Shutdown: 정리 작업 (필요시)
    print("Shutting down...")


# FastAPI 앱 생성
app = FastAPI(
    title="TODO API",
    description="FastAPI + PostgreSQL로 만든 TODO 관리 API",
    version="2.0.0",
    lifespan=lifespan,
)

# 라우터 등록
app.include_router(todos.router)


@app.get("/")
def root():
    """
    루트 엔드포인트
    API 상태 확인용
    """
    return {
        "message": "TODO API에 오신 것을 환영합니다!",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    헬스 체크 엔드포인트
    서버 상태 모니터링용
    """
    return {"status": "healthy"}
