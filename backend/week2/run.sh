#!/bin/bash
# Week2 FastAPI 서버 실행 스크립트
# 외부 PC에서도 접속 가능하도록 0.0.0.0으로 바인딩

echo "🚀 Week2 FastAPI 서버 시작..."
echo "📍 외부 접속 가능 (0.0.0.0:8000)"
echo ""

# 현재 디렉토리 확인
if [ ! -f "main.py" ]; then
    echo "❌ main.py를 찾을 수 없습니다. week2 디렉토리에서 실행하세요."
    exit 1
fi

# Docker Compose 상태 확인
if ! docker compose ps | grep -q "Up.*healthy"; then
    echo "⚠️  PostgreSQL이 실행되지 않았습니다."
    echo "🔄 PostgreSQL 시작 중..."
    docker compose up -d
    echo "⏳ DB 준비 대기 중 (5초)..."
    sleep 5
fi

# FastAPI 서버 실행
echo "✅ PostgreSQL 준비 완료"
echo ""
echo "📡 서버 접속 방법:"
echo "   - 로컬: http://localhost:8000"
echo "   - 외부: http://$(hostname -I | awk '{print $1}'):8000"
echo "   - Swagger: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "🛑 종료: Ctrl + C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
