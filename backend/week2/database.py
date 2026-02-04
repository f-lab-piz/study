"""
데이터베이스 연결 설정
- SQLAlchemy 엔진 생성
- 세션 관리
- Base 클래스 정의
"""

from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 URL
# postgresql://사용자:비밀번호@호스트:포트/DB명
DATABASE_URL = getenv("DATABASE_URL", "postgresql://fastapi_user:fastapi_pass@localhost:5432/fastapi_db")

# 엔진 생성 (DB와의 연결 풀 관리)
# echo=True: SQL 쿼리를 콘솔에 출력 (개발 시 디버깅용)
engine = create_engine(DATABASE_URL, echo=True)

# 세션 팩토리 (DB 작업 단위)
# autocommit=False: 명시적으로 commit() 호출 필요
# autoflush=False: 자동 flush 비활성화
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 베이스 클래스 (모든 모델이 상속받음)
Base = declarative_base()


def get_db():
    """
    FastAPI 의존성 주입용 함수
    요청마다 DB 세션을 생성하고, 요청 종료 시 자동으로 닫음

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db  # 요청 처리 중에 세션 제공
    finally:
        db.close()  # 요청 종료 시 세션 닫기
