"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from app.routers import todos

# FastAPI 앱 생성
app = FastAPI(
    title="TODO API",
    description="FastAPI로 만든 간단한 TODO 관리 API",
    version="1.0.0",
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
