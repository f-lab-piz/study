# AI API 통합 실전 가이드 - Python 백엔드로 프론트엔드에 제공하기

프론트엔드 개발자로서 AI 기능을 사용하는 가장 현실적인 방법은 **AI API를 Python 백엔드에서 호출하고, 그 결과를 프론트엔드에 제공**하는 것입니다.

## 1. OpenAI API 기본 사용법

### 설치 및 설정

```bash
# 필요한 패키지 설치
pip install openai python-dotenv fastapi uvicorn
```

```python
# .env 파일
OPENAI_API_KEY=sk-...your-api-key...
```

### 기본 채팅 API 호출

```python
# chat_basic.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_completion(user_message):
    """기본 채팅 완성"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 친절한 AI 어시스턴트입니다."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,  # 0~2, 높을수록 창의적
        max_tokens=500,   # 최대 응답 길이
    )

    return response.choices[0].message.content

# 사용 예시
if __name__ == "__main__":
    answer = chat_completion("Python과 JavaScript의 차이를 간단히 설명해줘")
    print(answer)
```

### 주요 파라미터 설명

```python
parameters = {
    "model": "gpt-3.5-turbo",  # 또는 "gpt-4", "gpt-4-turbo"

    "temperature": 0.7,
    # 0: 일관적이고 예측 가능 (FAQ, 번역)
    # 1: 균형잡힌 창의성 (일반 대화)
    # 2: 매우 창의적 (브레인스토밍, 창작)

    "max_tokens": 500,
    # 응답의 최대 길이 (1 토큰 ≈ 0.75 단어)
    # 프론트엔드에서 UI 제약 고려

    "top_p": 0.9,
    # 0~1, nucleus sampling (temperature 대신 사용 가능)

    "frequency_penalty": 0.0,
    # -2~2, 반복 줄이기

    "presence_penalty": 0.0,
    # -2~2, 새로운 주제 유도
}
```

## 2. 스트리밍 응답 (실시간 표시)

ChatGPT처럼 답변이 실시간으로 나타나게 하려면 스트리밍을 사용합니다.

### Python 백엔드

```python
# chat_streaming.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_streaming(user_message):
    """스트리밍 응답 생성기"""
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 친절한 AI 어시스턴트입니다."},
            {"role": "user", "content": user_message}
        ],
        stream=True,  # 스트리밍 활성화
    )

    # 청크 단위로 yield
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# 사용 예시
if __name__ == "__main__":
    print("AI: ", end="", flush=True)
    for chunk in chat_streaming("Python의 장점을 3가지 말해줘"):
        print(chunk, end="", flush=True)
    print()  # 줄바꿈
```

### FastAPI로 프론트엔드에 제공

```python
# main.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# CORS 설정 (프론트엔드에서 호출 가능하게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """일반 채팅 API"""
    # 대화 히스토리 구성
    messages = [
        {"role": "system", "content": "당신은 친절한 AI 어시스턴트입니다."}
    ]
    messages.extend(request.conversation_history)
    messages.append({"role": "user", "content": request.message})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )

    return {
        "response": response.choices[0].message.content,
        "tokens_used": response.usage.total_tokens
    }

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """스트리밍 채팅 API"""
    messages = [
        {"role": "system", "content": "당신은 친절한 AI 어시스턴트입니다."}
    ]
    messages.extend(request.conversation_history)
    messages.append({"role": "user", "content": request.message})

    def generate():
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                # SSE (Server-Sent Events) 형식
                yield f"data: {chunk.choices[0].delta.content}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

# 서버 실행: uvicorn main:app --reload
```

### 프론트엔드에서 호출 (React 예시)

```javascript
// 일반 채팅
async function sendMessage(message) {
    const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            conversation_history: conversationHistory
        })
    });

    const data = await response.json();
    return data.response;
}

// 스트리밍 채팅
async function sendStreamingMessage(message, onChunk) {
    const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: message,
            conversation_history: conversationHistory
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const content = line.slice(6);
                if (content === '[DONE]') return;
                onChunk(content);  // 각 청크를 UI에 표시
            }
        }
    }
}

// 사용 예시
const [response, setResponse] = useState('');

sendStreamingMessage('Python 설명해줘', (chunk) => {
    setResponse(prev => prev + chunk);  // 실시간으로 추가
});
```

## 3. 프롬프트 엔지니어링 기초

좋은 프롬프트를 작성하면 더 나은 결과를 얻을 수 있습니다.

### 기본 원칙

```python
# ❌ 나쁜 프롬프트
bad_prompt = "코드 리뷰해줘"

# ✅ 좋은 프롬프트
good_prompt = """
당신은 10년 경력의 시니어 Python 개발자입니다.
다음 코드를 리뷰하고, 개선점을 3가지 이내로 제시해주세요.
각 개선점은 이유와 함께 구체적인 코드 예시를 포함해주세요.

코드:
```python
def calculate(a, b):
    return a + b
```

리뷰:
"""
```

### Few-Shot 프롬프팅

예시를 제공하면 원하는 형식으로 답변을 받을 수 있습니다.

```python
def sentiment_analysis(text):
    """감정 분석 (Few-Shot)"""
    prompt = f"""
다음 텍스트의 감정을 분석하고 JSON 형식으로 답변하세요.

예시 1:
입력: "이 제품 정말 좋아요! 강추합니다"
출력: {{"sentiment": "positive", "score": 0.9, "keywords": ["좋아요", "강추"]}}

예시 2:
입력: "배송이 너무 늦어요. 실망했습니다"
출력: {{"sentiment": "negative", "score": 0.8, "keywords": ["늦어요", "실망"]}}

예시 3:
입력: "그냥 평범해요"
출력: {{"sentiment": "neutral", "score": 0.5, "keywords": ["평범"]}}

이제 다음 텍스트를 분석하세요:
입력: "{text}"
출력:
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # 일관성을 위해 낮게
    )

    return response.choices[0].message.content
```

### 시스템 프롬프트 활용

```python
system_prompts = {
    "customer_support": """
당신은 전자상거래 플랫폼의 고객 지원 AI입니다.
- 항상 예의 바르고 친절하게 응대합니다
- 정책: 배송은 3-5일, 반품은 7일 이내 가능
- 모르는 내용은 "상담원 연결을 도와드리겠습니다"라고 답변
- 절대 회사 정책 외의 내용을 약속하지 않습니다
""",

    "code_teacher": """
당신은 초보 개발자를 위한 프로그래밍 강사입니다.
- 복잡한 개념은 일상적인 비유로 설명합니다
- 코드 예시는 주석을 충분히 포함합니다
- 단계별로 쉽게 설명합니다
- 격려하는 톤을 유지합니다
""",

    "json_extractor": """
당신은 데이터 추출 전문가입니다.
- 사용자 입력에서 정보를 추출하여 JSON으로 반환합니다
- 추가 설명 없이 JSON만 출력합니다
- 정보가 없으면 null을 사용합니다
"""
}

def chat_with_persona(user_message, persona="customer_support"):
    """특정 페르소나로 대화"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompts[persona]},
            {"role": "user", "content": user_message}
        ],
    )
    return response.choices[0].message.content
```

## 4. Hugging Face API 사용

오픈소스 모델을 활용할 수 있습니다. 무료 티어도 제공됩니다.

### 설치 및 기본 사용

```bash
pip install huggingface_hub requests
```

```python
# huggingface_example.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def query_huggingface(api_url, payload):
    """Hugging Face API 호출"""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

# 1. 텍스트 생성
def generate_text(prompt):
    api_url = "https://api-inference.huggingface.co/models/gpt2"
    payload = {"inputs": prompt}
    return query_huggingface(api_url, payload)

# 2. 감정 분석 (한국어)
def sentiment_analysis_kr(text):
    api_url = "https://api-inference.huggingface.co/models/beomi/kcbert-base"
    payload = {"inputs": text}
    return query_huggingface(api_url, payload)

# 3. 이미지 분류
def classify_image(image_path):
    api_url = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"

    with open(image_path, "rb") as f:
        data = f.read()

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(api_url, headers=headers, data=data)
    return response.json()

# 4. 텍스트 임베딩
def get_embeddings(texts):
    api_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    payload = {"inputs": texts}
    return query_huggingface(api_url, payload)

# 사용 예시
if __name__ == "__main__":
    # 감정 분석
    result = sentiment_analysis_kr("이 제품 정말 좋아요!")
    print(result)

    # 임베딩 생성
    embeddings = get_embeddings(["안녕하세요", "반갑습니다"])
    print(f"임베딩 차원: {len(embeddings[0])}")
```

### FastAPI 엔드포인트 추가

```python
# main.py에 추가
@app.post("/api/sentiment")
async def analyze_sentiment(text: str):
    """감정 분석 API"""
    api_url = "https://api-inference.huggingface.co/models/beomi/kcbert-base"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

    response = requests.post(
        api_url,
        headers=headers,
        json={"inputs": text}
    )

    return response.json()

@app.post("/api/image/classify")
async def classify_image(image_url: str):
    """이미지 분류 API"""
    # 이미지 다운로드
    img_response = requests.get(image_url)

    # Hugging Face API 호출
    api_url = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

    hf_response = requests.post(
        api_url,
        headers=headers,
        data=img_response.content
    )

    return hf_response.json()
```

## 5. 실전 예제: FAQ 챗봇

사용자 질문에 맞는 FAQ를 찾아서 답변하는 챗봇입니다.

```python
# faq_chatbot.py
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# FAQ 데이터
FAQ_DATA = [
    {
        "question": "배송은 얼마나 걸리나요?",
        "answer": "일반 배송은 주문 후 3-5 영업일이 소요됩니다. 제주도 및 도서산간 지역은 1-2일 추가될 수 있습니다."
    },
    {
        "question": "반품은 어떻게 하나요?",
        "answer": "상품 수령 후 7일 이내에 마이페이지에서 반품 신청 가능합니다. 단, 포장이 훼손되지 않은 상품에 한합니다."
    },
    {
        "question": "결제 방법은 무엇이 있나요?",
        "answer": "신용카드, 체크카드, 계좌이체, 카카오페이, 네이버페이를 지원합니다."
    },
]

def get_embedding(text):
    """텍스트 임베딩 생성"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def find_best_faq(user_question):
    """가장 유사한 FAQ 찾기"""
    # 사용자 질문 임베딩
    user_embedding = get_embedding(user_question)

    # 각 FAQ와 유사도 계산
    best_match = None
    best_score = -1

    for faq in FAQ_DATA:
        faq_embedding = get_embedding(faq["question"])

        # 코사인 유사도 계산
        similarity = cosine_similarity(
            [user_embedding],
            [faq_embedding]
        )[0][0]

        if similarity > best_score:
            best_score = similarity
            best_match = faq

    # 유사도가 0.7 이상이면 FAQ 답변, 아니면 GPT에게 물어봄
    if best_score > 0.7:
        return {
            "source": "faq",
            "answer": best_match["answer"],
            "confidence": best_score
        }
    else:
        # 일반 대화로 처리
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "고객 지원 AI입니다. 모르면 '상담원 연결을 도와드리겠습니다'라고 하세요."},
                {"role": "user", "content": user_question}
            ],
        )
        return {
            "source": "gpt",
            "answer": response.choices[0].message.content,
            "confidence": None
        }

# FastAPI 엔드포인트
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/faq")
async def faq_chatbot(question: str):
    result = find_best_faq(question)
    return result

# 사용 예시
if __name__ == "__main__":
    questions = [
        "배송 기간이 궁금해요",  # FAQ 매칭
        "오늘 날씨 어때요?",      # GPT 처리
    ]

    for q in questions:
        result = find_best_faq(q)
        print(f"\n질문: {q}")
        print(f"출처: {result['source']}")
        print(f"답변: {result['answer']}")
        if result['confidence']:
            print(f"신뢰도: {result['confidence']:.2f}")
```

## 6. 에러 처리 및 재시도 전략

API 호출은 실패할 수 있으므로 적절한 에러 처리가 필요합니다.

```python
# error_handling.py
import time
from openai import OpenAI, OpenAIError, RateLimitError, APIError
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_retry(user_message, max_retries=3):
    """재시도 로직이 포함된 채팅"""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
                timeout=30,  # 30초 타임아웃
            )
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "tokens": response.usage.total_tokens
            }

        except RateLimitError as e:
            # Rate limit에 걸림 - 대기 후 재시도
            wait_time = 2 ** attempt  # 지수 백오프: 1초, 2초, 4초
            print(f"Rate limit 도달. {wait_time}초 후 재시도...")
            time.sleep(wait_time)

        except APIError as e:
            # API 에러 - 서버 문제일 수 있음
            if attempt == max_retries - 1:
                return {
                    "success": False,
                    "error": "API 서버 오류",
                    "detail": str(e)
                }
            time.sleep(1)

        except OpenAIError as e:
            # 기타 OpenAI 에러
            return {
                "success": False,
                "error": "OpenAI 에러",
                "detail": str(e)
            }

        except Exception as e:
            # 예상치 못한 에러
            return {
                "success": False,
                "error": "알 수 없는 에러",
                "detail": str(e)
            }

    # 모든 재시도 실패
    return {
        "success": False,
        "error": "최대 재시도 횟수 초과"
    }

# FastAPI 엔드포인트에서 사용
@app.post("/api/chat/safe")
async def safe_chat(message: str):
    result = chat_with_retry(message)

    if not result["success"]:
        # 프론트엔드에 적절한 HTTP 상태 코드 반환
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=result["error"])

    return result
```

## 7. 비용 모니터링

OpenAI API는 토큰 수에 따라 과금되므로 모니터링이 중요합니다.

```python
# cost_monitoring.py
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 모델별 가격 (2025년 1월 기준, 1000 토큰당 USD)
PRICING = {
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "text-embedding-3-small": {"input": 0.00002, "output": 0},
}

def calculate_cost(model, input_tokens, output_tokens):
    """비용 계산"""
    pricing = PRICING.get(model, {"input": 0, "output": 0})

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]

    return input_cost + output_cost

def chat_with_cost_tracking(user_message, model="gpt-3.5-turbo"):
    """비용 추적이 포함된 채팅"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": user_message}],
    )

    usage = response.usage
    cost = calculate_cost(model, usage.prompt_tokens, usage.completion_tokens)

    # 로그 기록 (실제로는 DB에 저장)
    log = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "cost_usd": cost,
        "cost_krw": cost * 1300,  # 환율 적용
    }

    print(f"사용 토큰: {usage.total_tokens} | 비용: ${cost:.4f} (약 {cost*1300:.0f}원)")

    return {
        "response": response.choices[0].message.content,
        "usage": log
    }

# 일일 사용량 제한
DAILY_LIMIT_USD = 10.0  # 하루 10달러 제한
daily_usage = 0.0

def chat_with_limit(user_message):
    """일일 사용량 제한"""
    global daily_usage

    if daily_usage >= DAILY_LIMIT_USD:
        return {
            "success": False,
            "error": "일일 사용량 한도 초과",
            "limit": DAILY_LIMIT_USD,
            "used": daily_usage
        }

    result = chat_with_cost_tracking(user_message)
    daily_usage += result["usage"]["cost_usd"]

    return result
```

## 요약

### 핵심 포인트
1. **OpenAI API**: 강력하지만 유료, 토큰 기반 과금
2. **Hugging Face**: 오픈소스 모델, 무료 티어 제공
3. **스트리밍**: UX 개선을 위해 필수
4. **프롬프트 엔지니어링**: 좋은 프롬프트 = 좋은 결과
5. **에러 처리**: 재시도, 타임아웃, 폴백 전략 필수
6. **비용 관리**: 모니터링과 제한 설정

### FastAPI 서버 실행

```bash
# 개발 서버
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 (gunicorn + uvicorn)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 프론트엔드 연동 체크리스트
- [ ] CORS 설정 확인
- [ ] 로딩 상태 UI
- [ ] 에러 메시지 표시
- [ ] 스트리밍 응답 처리
- [ ] 토큰 제한 안내
- [ ] 재시도 로직
- [ ] 비용 모니터링 대시보드

다음 문서에서는 AI 기능의 UX 패턴을 다룹니다!
