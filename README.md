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
# .env 파일 생성
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-key
LANGFUSE_SECRET_KEY=sk-lf-your-key
LANGFUSE_HOST=http://localhost:3000
EOF

# 필요한 패키지 설치
pip install requests python-dotenv langchain langchain-openai langfuse
```

#### 2. Langfuse 셀프 호스팅 (선택)
```bash
cd ai-basics
# docker-compose.yml 생성 후
docker-compose up -d
# http://localhost:3000 접속
```

#### 3. 예시 실행
```bash
# 통합 예시 실행
python ai-basics/langchain_langfuse_example.py

# 또는 주피터 노트북으로 실습
jupyter notebook ai-basics/
```
