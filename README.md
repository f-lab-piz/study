# study

## AI 기초 학습 자료

### 목차
1. [AI/ML 기본 개념](ai-basics/01_ai_ml_concepts.md)
2. [API 통합](ai-basics/02_api_integration.md)
3. [AI UX 패턴](ai-basics/03_ai_ux_patterns.md)
4. [성능 최적화](ai-basics/04_performance_optimization.md)
5. [LLM API 기초](ai-basics/05_llm_api_practice.ipynb) - curl, Python requests로 API 호출
6. [LangChain 기초](ai-basics/06_langchain_practice.ipynb) - 프롬프트 템플릿, Chain, 메모리, 챗봇
7. [Langfuse 기초](ai-basics/07_langfuse_practice.ipynb) - Docker 셀프 호스팅, Trace logging

### 실습 파일
- `05_llm_api_practice.ipynb` - LLM API 직접 호출 실습
- `06_langchain_practice.ipynb` - LangChain 기초 실습
- `07_langfuse_practice.ipynb` - Langfuse 모니터링 실습
- `langchain_langfuse_example.py` - LangChain + Langfuse 통합 예시

### 시작하기

#### 1. 환경 설정
```bash
# 프로젝트 루트에 .env 파일 생성
cd /workspaces/study  # 또는 프로젝트 루트로 이동
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-key
LANGFUSE_SECRET_KEY=sk-lf-your-key
LANGFUSE_HOST=http://localhost:3000
EOF

# 필요한 패키지 설치
pip install requests python-dotenv langchain langchain-openai langfuse
```

**참고:** 노트북들은 `find_dotenv()`를 사용하여 현재 디렉토리부터 상위로 올라가며 `.env` 파일을 자동으로 찾습니다. 프로젝트 루트에 `.env` 파일을 두면 어디서 실행하든 동작합니다.

#### 2. Langfuse 셀프 호스팅 (선택)
```bash
# Langfuse 저장소 클론
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Docker Compose 실행
docker compose up -d

# http://localhost:3000 접속하여 회원가입 후 API 키 발급
```

#### 3. 예시 실행
```bash
# 통합 예시 실행
python ai-basics/langchain_langfuse_example.py

# 또는 주피터 노트북으로 실습
jupyter notebook ai-basics/
```
