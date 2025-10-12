# AI 성능 및 비용 최적화 - 프론트엔드 개발자 필수 가이드

AI API는 일반 API보다 느리고 비용이 높습니다. 프론트엔드 개발자로서 이를 이해하고 최적화 전략을 제안할 수 있어야 합니다.

## 1. 클라이언트 vs 서버 추론

### 비교

| 구분 | 클라이언트 추론 | 서버 추론 |
|------|----------------|----------|
| **속도** | 빠름 (네트워크 없음) | 느림 (네트워크 지연) |
| **비용** | 무료 (사용자 기기) | 유료 (API 호출) |
| **모델 크기** | 작음 (< 100MB) | 제한 없음 (수십 GB) |
| **정확도** | 낮음 | 높음 |
| **프라이버시** | 우수 (로컬 처리) | 데이터 전송 필요 |
| **업데이트** | 어려움 | 쉬움 (서버만) |

### 클라이언트 추론: TensorFlow.js

간단한 작업은 브라우저에서 직접 처리할 수 있습니다.

```javascript
// 이미지 분류 (브라우저)
import * as mobilenet from '@tensorflow-models/mobilenet';

async function classifyImage(imageElement) {
    // 모델 로드 (첫 실행시만, 이후 캐싱)
    const model = await mobilenet.load();

    // 추론 (즉시 실행, 서버 불필요)
    const predictions = await model.classify(imageElement);

    console.log(predictions);
    // [
    //   { className: 'dog', probability: 0.92 },
    //   { className: 'cat', probability: 0.05 },
    //   ...
    // ]
}

// 장점: 빠름, 무료, 오프라인 가능
// 단점: 정확도 낮음, 모델 크기 제한
```

### 서버 추론: API 호출

복잡한 작업은 서버에서 처리합니다.

```python
# 서버에서 강력한 모델 사용
from transformers import pipeline

# GPU로 실행 (빠르고 정확)
classifier = pipeline("sentiment-analysis", model="bert-base-multilingual", device=0)

@app.post("/api/sentiment")
async def analyze_sentiment(text: str):
    result = classifier(text)
    return result
```

### 하이브리드 접근

```javascript
// 간단한 작업: 클라이언트
if (isSimpleTask) {
    result = await localModel.predict(input);
}
// 복잡한 작업: 서버
else {
    result = await fetch('/api/ai/complex', { body: input });
}
```

**예시**:
- **클라이언트**: 이미지 리사이징, 얼굴 감지, 간단한 텍스트 분류
- **서버**: 복잡한 텍스트 생성, 고품질 이미지 생성, 정밀 분석

## 2. 캐싱 전략

AI API는 느리고 비싸므로, 같은 요청은 캐싱해야 합니다.

### Redis로 응답 캐싱

```python
# caching.py
import redis
import json
import hashlib
from openai import OpenAI

# Redis 연결
redis_client = redis.Redis(host='localhost', port=6379, db=0)
openai_client = OpenAI()

def get_cache_key(prompt, model="gpt-3.5-turbo"):
    """캐시 키 생성"""
    key_string = f"{model}:{prompt}"
    return hashlib.md5(key_string.encode()).hexdigest()

def chat_with_cache(prompt, ttl=3600):
    """캐싱이 포함된 채팅"""

    # 1. 캐시 확인
    cache_key = get_cache_key(prompt)
    cached = redis_client.get(cache_key)

    if cached:
        print("✓ 캐시 히트!")
        return json.loads(cached)

    # 2. 캐시 미스 - API 호출
    print("✗ 캐시 미스 - API 호출")
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )

    result = {
        "response": response.choices[0].message.content,
        "tokens": response.usage.total_tokens,
        "cached": False
    }

    # 3. 캐시 저장 (1시간)
    redis_client.setex(
        cache_key,
        ttl,
        json.dumps(result, ensure_ascii=False)
    )

    return result

# 사용 예시
if __name__ == "__main__":
    # 첫 번째 호출: API 호출 (느림)
    result1 = chat_with_cache("Python의 장점을 3가지 말해줘")
    print(result1["response"])

    # 두 번째 호출: 캐시 사용 (빠름)
    result2 = chat_with_cache("Python의 장점을 3가지 말해줘")
    print(result2["response"])
```

### 의미 기반 캐싱 (Semantic Caching)

비슷한 질문도 캐싱합니다.

```python
# semantic_caching.py
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import redis
import json

client = OpenAI()
redis_client = redis.Redis(decode_responses=True)

def get_embedding(text):
    """텍스트 임베딩 생성"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def semantic_cache_lookup(query, similarity_threshold=0.9):
    """의미가 비슷한 캐시 검색"""

    # 쿼리 임베딩
    query_embedding = get_embedding(query)

    # 모든 캐시된 쿼리 검색
    cached_keys = redis_client.keys("semantic:*")

    best_match = None
    best_similarity = 0

    for key in cached_keys:
        cached_data = json.loads(redis_client.get(key))
        cached_embedding = cached_data["embedding"]

        # 코사인 유사도 계산
        similarity = cosine_similarity(
            [query_embedding],
            [cached_embedding]
        )[0][0]

        if similarity > best_similarity and similarity >= similarity_threshold:
            best_similarity = similarity
            best_match = cached_data

    if best_match:
        print(f"✓ 의미 기반 캐시 히트! (유사도: {best_similarity:.2f})")
        return best_match["response"]

    return None

def chat_with_semantic_cache(query):
    """의미 기반 캐싱"""

    # 1. 의미 기반 캐시 확인
    cached_response = semantic_cache_lookup(query)
    if cached_response:
        return {"response": cached_response, "cached": True}

    # 2. API 호출
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
    )

    answer = response.choices[0].message.content

    # 3. 캐시 저장
    cache_key = f"semantic:{hash(query)}"
    cache_data = {
        "query": query,
        "embedding": get_embedding(query),
        "response": answer,
    }
    redis_client.setex(cache_key, 3600, json.dumps(cache_data))

    return {"response": answer, "cached": False}

# 사용 예시
if __name__ == "__main__":
    # 다양한 표현의 같은 질문
    queries = [
        "Python의 장점을 알려줘",
        "Python이 좋은 이유는 뭐야?",
        "파이썬의 강점은?",
    ]

    for q in queries:
        result = chat_with_semantic_cache(q)
        print(f"\n질문: {q}")
        print(f"답변: {result['response'][:100]}...")
        print(f"캐시됨: {result['cached']}")
```

### FastAPI에서 캐싱 사용

```python
# main.py
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

app = FastAPI()

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.post("/api/chat")
@cache(expire=3600)  # 1시간 캐싱
async def chat(message: str):
    # 같은 message는 1시간 동안 캐싱됨
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
    )
    return {"response": response.choices[0].message.content}
```

### 프론트엔드 캐싱

```javascript
// 브라우저 캐싱 (React Query)
import { useQuery } from '@tanstack/react-query';

function useChatQuery(message) {
    return useQuery({
        queryKey: ['chat', message],
        queryFn: async () => {
            const response = await fetch('/api/chat', {
                method: 'POST',
                body: JSON.stringify({ message }),
            });
            return response.json();
        },
        staleTime: 1000 * 60 * 60, // 1시간 동안 신선
        cacheTime: 1000 * 60 * 60 * 24, // 24시간 캐싱
    });
}

// 사용
function ChatComponent() {
    const { data, isLoading } = useChatQuery("Python 장점은?");

    // 같은 질문을 다시 하면 즉시 응답 (캐시 사용)
}
```

## 3. Rate Limiting 및 배치 처리

### Rate Limiting (요청 제한)

API 제공자의 제한을 지키고, 비용을 관리합니다.

```python
# rate_limiting.py
import time
from collections import deque
from threading import Lock

class RateLimiter:
    """분당 요청 수 제한"""

    def __init__(self, max_requests, time_window=60):
        self.max_requests = max_requests  # 최대 요청 수
        self.time_window = time_window    # 시간 창 (초)
        self.requests = deque()
        self.lock = Lock()

    def acquire(self):
        """요청 허가 (필요시 대기)"""
        with self.lock:
            now = time.time()

            # 오래된 요청 제거
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()

            # 제한 초과시 대기
            if len(self.requests) >= self.max_requests:
                wait_time = self.requests[0] + self.time_window - now
                print(f"Rate limit 도달. {wait_time:.1f}초 대기...")
                time.sleep(wait_time)
                return self.acquire()  # 재시도

            # 요청 기록
            self.requests.append(now)

# OpenAI 무료 티어: 분당 3회
rate_limiter = RateLimiter(max_requests=3, time_window=60)

def chat_with_rate_limit(message):
    """Rate limiting이 적용된 채팅"""
    rate_limiter.acquire()  # 허가 대기

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
    )

    return response.choices[0].message.content

# 사용 예시
if __name__ == "__main__":
    # 4개 요청 (4번째는 대기)
    for i in range(4):
        print(f"\n{i+1}번째 요청")
        answer = chat_with_rate_limit(f"숫자 {i}를 영어로?")
        print(answer)
```

### 배치 처리

여러 요청을 모아서 한 번에 처리하면 효율적입니다.

```python
# batch_processing.py
import asyncio
from typing import List

class BatchProcessor:
    """요청을 모아서 배치 처리"""

    def __init__(self, batch_size=10, max_wait=2.0):
        self.batch_size = batch_size  # 배치 크기
        self.max_wait = max_wait      # 최대 대기 시간 (초)
        self.queue = []
        self.results = {}

    async def add_request(self, request_id, message):
        """요청 추가"""
        future = asyncio.Future()
        self.queue.append((request_id, message, future))

        # 배치가 차거나 시간 초과시 처리
        if len(self.queue) >= self.batch_size:
            await self.process_batch()

        # 또는 최대 대기 시간 후 처리
        asyncio.create_task(self.auto_process(request_id))

        return await future

    async def auto_process(self, request_id):
        """일정 시간 후 자동 처리"""
        await asyncio.sleep(self.max_wait)
        if any(req[0] == request_id for req in self.queue):
            await self.process_batch()

    async def process_batch(self):
        """배치 처리"""
        if not self.queue:
            return

        batch = self.queue[:self.batch_size]
        self.queue = self.queue[self.batch_size:]

        print(f"배치 처리: {len(batch)}개 요청")

        # 병렬 처리
        tasks = []
        for request_id, message, future in batch:
            tasks.append(self.process_single(request_id, message, future))

        await asyncio.gather(*tasks)

    async def process_single(self, request_id, message, future):
        """단일 요청 처리"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
            )
            result = response.choices[0].message.content
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)

# FastAPI에서 사용
batch_processor = BatchProcessor(batch_size=10, max_wait=2.0)

@app.post("/api/chat/batch")
async def chat_batch(request_id: str, message: str):
    """배치 처리 엔드포인트"""
    result = await batch_processor.add_request(request_id, message)
    return {"response": result}

# 장점: 10개 요청이 2초 안에 들어오면 한 번에 처리
# 비용 절감 및 처리량 증가
```

### 프론트엔드에서 디바운싱

```javascript
// 사용자가 타이핑 중일 때는 요청 안 보내기
import { useState, useEffect } from 'react';

function useDebouncedValue(value, delay = 500) {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        return () => clearTimeout(handler);
    }, [value, delay]);

    return debouncedValue;
}

// 사용
function SearchWithAI() {
    const [query, setQuery] = useState('');
    const debouncedQuery = useDebouncedValue(query, 1000);

    useEffect(() => {
        if (debouncedQuery) {
            // 1초 동안 입력 없으면 검색
            fetchAISearch(debouncedQuery);
        }
    }, [debouncedQuery]);

    return (
        <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="AI 검색..."
        />
    );
}
```

## 4. 모델 경량화 이해

ML 팀과 협업할 때 알아두면 좋습니다.

### 모델 크기 vs 성능

```
GPT-4 (1.7T 파라미터)
- 크기: ~수 TB
- 성능: 최고
- 속도: 느림 (10-30초)
- 비용: 매우 비쌈

GPT-3.5 (175B 파라미터)
- 크기: ~350GB
- 성능: 우수
- 속도: 빠름 (1-3초)
- 비용: 저렴

DistilBERT (66M 파라미터)
- 크기: ~250MB
- 성능: 보통
- 속도: 매우 빠름 (< 100ms)
- 비용: 거의 무료
```

### 프론트엔드 개발자가 제안할 수 있는 것

```python
# ML 팀과의 대화 예시

프론트엔드: "현재 응답 시간이 5초인데, 3초 이내로 줄일 수 있을까요?"

ML 엔지니어: "더 작은 모델을 사용하거나, 모델 양자화를 적용할 수 있어요."

프론트엔드: "정확도가 얼마나 떨어질까요?"

ML 엔지니어: "현재 92%인데, 89%로 약간 떨어질 것 같아요."

프론트엔드: "UX 테스트 결과 3% 차이는 사용자들이 못 느꼈어요.
           속도가 더 중요하니 적용해보면 좋을 것 같아요."
```

### 양자화 (Quantization) 예시

```python
# 모델 양자화로 크기와 속도 개선
from transformers import AutoModelForCausalLM
import torch

# 원본 모델 (FP32)
model = AutoModelForCausalLM.from_pretrained("gpt2")
# 크기: ~500MB, 속도: 100ms

# 양자화 (INT8)
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)
# 크기: ~125MB (4배 감소), 속도: 50ms (2배 빠름)
# 정확도: 거의 동일 (~1% 차이)
```

## 5. 비용 최적화

### 모델 선택 전략

```python
# 작업별 모델 선택
def choose_model(task_complexity, budget="low"):
    """작업 복잡도와 예산에 따라 모델 선택"""

    if budget == "low":
        if task_complexity == "simple":
            return "gpt-3.5-turbo"  # $0.0015/1K tokens
        elif task_complexity == "medium":
            return "gpt-3.5-turbo"
        else:
            return "gpt-4-turbo"    # $0.03/1K tokens (필요시만)

    elif budget == "high":
        if task_complexity == "simple":
            return "gpt-3.5-turbo"
        else:
            return "gpt-4"          # $0.06/1K tokens

    return "gpt-3.5-turbo"  # 기본값

# 사용 예시
@app.post("/api/chat/smart")
async def smart_chat(message: str, task_type: str):
    """작업에 맞는 모델 선택"""

    # 간단한 FAQ → 저렴한 모델
    if task_type == "faq":
        model = "gpt-3.5-turbo"

    # 복잡한 코드 생성 → 강력한 모델
    elif task_type == "code_generation":
        model = "gpt-4-turbo"

    # 일반 대화 → 중간 모델
    else:
        model = "gpt-3.5-turbo"

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
    )

    return {
        "response": response.choices[0].message.content,
        "model_used": model,
        "cost": calculate_cost(model, response.usage.total_tokens)
    }
```

### 프롬프트 최적화로 토큰 절약

```python
# ❌ 나쁜 예: 불필요하게 긴 프롬프트
bad_prompt = """
안녕하세요. 저는 지금 Python 프로그래밍 언어를 공부하고 있는 학생입니다.
Python에 대해서 배우고 있는데요, 리스트와 튜플의 차이점에 대해서 잘 모르겠어서
이렇게 질문을 드립니다. 리스트와 튜플은 어떻게 다른가요?
자세하게 설명해주시면 감사하겠습니다.
"""
# 토큰: ~60

# ✅ 좋은 예: 간결한 프롬프트
good_prompt = "Python 리스트와 튜플의 차이를 3가지로 요약해줘"
# 토큰: ~15

# 75% 토큰 절약!
```

### 스트리밍으로 체감 속도 개선

```python
# 스트리밍: 첫 토큰 0.5초, 전체 5초
# 일반: 첫 응답 5초

# 사용자는 스트리밍이 훨씬 빠르게 느낌!
# 비용은 동일하지만 UX 개선
```

### 비용 알림 시스템

```python
# cost_monitoring.py
from datetime import datetime, timedelta

class CostMonitor:
    """비용 모니터링 및 알림"""

    def __init__(self, daily_limit=100.0):
        self.daily_limit = daily_limit  # 일일 한도 (USD)
        self.today_cost = 0.0
        self.today = datetime.now().date()

    def add_cost(self, cost):
        """비용 추가"""
        # 날짜 변경시 리셋
        if datetime.now().date() != self.today:
            self.today_cost = 0.0
            self.today = datetime.now().date()

        self.today_cost += cost

        # 경고 수준
        usage_percent = (self.today_cost / self.daily_limit) * 100

        if usage_percent >= 90:
            self.alert("🚨 일일 비용 90% 초과!")
        elif usage_percent >= 75:
            self.alert("⚠️ 일일 비용 75% 초과")

        # 한도 초과시 차단
        if self.today_cost >= self.daily_limit:
            raise Exception("일일 비용 한도 초과")

    def alert(self, message):
        """알림 전송"""
        print(f"[{datetime.now()}] {message}")
        print(f"오늘 사용량: ${self.today_cost:.2f} / ${self.daily_limit}")
        # 실제로는 Slack, 이메일 등으로 전송

cost_monitor = CostMonitor(daily_limit=100.0)

@app.post("/api/chat/monitored")
async def monitored_chat(message: str):
    """비용 모니터링이 적용된 채팅"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
    )

    # 비용 계산 및 기록
    cost = calculate_cost("gpt-3.5-turbo", response.usage.total_tokens)
    cost_monitor.add_cost(cost)

    return {
        "response": response.choices[0].message.content,
        "cost": cost,
        "daily_usage": cost_monitor.today_cost,
        "daily_limit": cost_monitor.daily_limit,
    }
```

## 6. 데이터베이스 최적화

### 벡터 데이터베이스 사용

임베딩 검색은 전용 DB를 사용하는 것이 빠릅니다.

```python
# vector_db.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Qdrant (벡터 DB) 연결
qdrant = QdrantClient("localhost", port=6333)

# 컬렉션 생성
qdrant.create_collection(
    collection_name="faq",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

def add_faq_to_db(question, answer):
    """FAQ를 벡터 DB에 추가"""
    # 임베딩 생성
    embedding = get_embedding(question)

    # 저장
    qdrant.upsert(
        collection_name="faq",
        points=[
            PointStruct(
                id=hash(question) % (10 ** 8),
                vector=embedding,
                payload={"question": question, "answer": answer}
            )
        ]
    )

def search_similar_faq(query, top_k=3):
    """유사한 FAQ 검색"""
    query_embedding = get_embedding(query)

    results = qdrant.search(
        collection_name="faq",
        query_vector=query_embedding,
        limit=top_k,
    )

    return [
        {
            "question": hit.payload["question"],
            "answer": hit.payload["answer"],
            "score": hit.score,
        }
        for hit in results
    ]

# 사용 예시
if __name__ == "__main__":
    # FAQ 추가
    add_faq_to_db(
        "배송은 얼마나 걸리나요?",
        "일반 배송은 3-5일 소요됩니다."
    )

    # 검색 (매우 빠름: < 10ms)
    results = search_similar_faq("배송 기간이 궁금해요")
    print(results)
    # [
    #   {
    #     "question": "배송은 얼마나 걸리나요?",
    #     "answer": "일반 배송은 3-5일 소요됩니다.",
    #     "score": 0.95
    #   }
    # ]
```

**장점**:
- 일반 DB (PostgreSQL): 1000개 검색 ~500ms
- 벡터 DB (Qdrant): 100만개 검색 ~10ms

### 인덱싱 전략

```python
# MongoDB에 임베딩 저장 및 인덱싱
from pymongo import MongoClient

mongo = MongoClient()
db = mongo["ai_app"]

# 인덱스 생성 (응답 속도 향상)
db.conversations.create_index([("user_id", 1), ("timestamp", -1)])
db.feedbacks.create_index([("message_id", 1)])

# 자주 사용하는 쿼리 최적화
def get_user_conversations(user_id, limit=10):
    """사용자 대화 기록 (인덱스 활용)"""
    return db.conversations.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit)
```

## 7. 실전 최적화 체크리스트

### 프론트엔드

```javascript
// 1. 디바운싱으로 불필요한 요청 방지
const debouncedSearch = useDebouncedValue(searchQuery, 1000);

// 2. 요청 취소 (사용자가 새 검색 시작하면 이전 요청 취소)
const abortController = new AbortController();
fetch('/api/search', {
    signal: abortController.signal
});

// 3. 낙관적 업데이트
setMessages([...messages, { text: userInput, from: 'user' }]);
// API 호출 전에 UI 먼저 업데이트

// 4. 스켈레톤 UI로 체감 속도 개선
{isLoading && <SkeletonLoader />}

// 5. 에러 바운더리
<ErrorBoundary fallback={<ErrorUI />}>
    <AIFeature />
</ErrorBoundary>
```

### 백엔드

```python
# 1. 캐싱
@cache(expire=3600)
async def chat(message: str): ...

# 2. Rate limiting
@limiter.limit("10/minute")
async def chat(message: str): ...

# 3. 배치 처리
await batch_processor.add_request(id, message)

# 4. 비동기 처리
async def chat(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(...)

# 5. 모니터링
from prometheus_client import Counter
api_calls = Counter('ai_api_calls', 'AI API 호출 수')
api_calls.inc()

# 6. 타임아웃 설정
response = await asyncio.wait_for(
    call_ai_api(message),
    timeout=30.0
)
```

## 요약

### 최적화 우선순위

1. **캐싱** (가장 큰 효과)
   - Redis로 중복 요청 제거
   - 의미 기반 캐싱으로 유사 질문 처리

2. **Rate Limiting**
   - API 제한 준수
   - 비용 관리

3. **배치 처리**
   - 여러 요청 묶어서 처리
   - 처리량 증가

4. **모델 선택**
   - 작업에 맞는 모델 사용
   - 간단한 작업은 저렴한 모델

5. **프롬프트 최적화**
   - 간결한 프롬프트
   - 불필요한 토큰 제거

### 성능 목표

```
응답 시간:
- 캐시 히트: < 100ms ⚡
- 간단한 작업: < 2초 ✓
- 복잡한 작업: < 5초 ⏱
- 스트리밍: 첫 토큰 < 1초 ⚡

비용:
- 사용자당 하루: < $0.10
- 한 달 총 비용: 예산 내

정확도:
- 사용자 만족도: > 80%
- 긍정 피드백: > 70%
```

### ML 팀과 협업하기

```
프론트엔드 개발자가 제공할 정보:
✓ 사용자 피드백 및 불만 사항
✓ 실제 사용 패턴 데이터
✓ 응답 속도에 대한 UX 테스트 결과
✓ 정확도 vs 속도 트레이드오프 의견
✓ 비용 최적화 아이디어

ML 엔지니어가 제공할 정보:
✓ 모델 성능 지표
✓ 최적화 가능 여부
✓ 예상 비용 및 속도
✓ 모델 한계 및 제약사항
```

이제 AI 프로젝트에서 효과적으로 협업할 준비가 되었습니다!
