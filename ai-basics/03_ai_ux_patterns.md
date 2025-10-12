# AI UX 패턴 - 프론트엔드 개발자 필수 가이드

AI 기능은 일반적인 API와 다른 특성이 있어 특별한 UX 고려사항이 필요합니다. 이 문서는 프론트엔드 개발자 관점에서 AI 기능을 어떻게 UI/UX로 표현할지 다룹니다.

## 1. AI의 특수한 특성 이해하기

### 일반 API vs AI API

```javascript
// 일반 API
const user = await fetch('/api/user/123');
// → 항상 동일한 결과, 빠름 (< 100ms), 확정적

// AI API
const response = await fetch('/api/chat', { message: '안녕' });
// → 매번 다른 결과, 느림 (1-5초), 확률적
```

**AI API의 특징**:
1. **느린 응답 시간**: 1-10초 (일반 API는 < 1초)
2. **비결정적**: 같은 입력에도 다른 결과
3. **실패 가능성**: Rate limit, 서버 오류 가능성 높음
4. **점진적 결과**: 스트리밍으로 조금씩 도착
5. **불확실성**: 100% 정확하지 않음

이러한 특성을 UX로 어떻게 다룰지가 핵심입니다.

## 2. 로딩 상태 처리

### 일반 로딩 vs AI 로딩

```javascript
// ❌ 나쁜 예: 일반 로딩만 표시
function ChatMessage() {
    const [loading, setLoading] = useState(false);

    if (loading) return <Spinner />;  // 너무 단순
    return <div>{message}</div>;
}

// ✅ 좋은 예: AI 특성 반영
function ChatMessage() {
    const [status, setStatus] = useState('idle');
    // 상태: idle, thinking, streaming, done, error

    return (
        <div>
            {status === 'thinking' && (
                <div className="thinking">
                    <ThinkingAnimation />
                    <p>답변을 생성하고 있습니다...</p>
                    <ProgressBar /> {/* 예상 시간 표시 */}
                </div>
            )}

            {status === 'streaming' && (
                <div className="streaming">
                    <StreamingText text={currentText} />
                    <TypingIndicator />
                </div>
            )}

            {status === 'done' && (
                <div className="done">
                    {message}
                    <ActionButtons /> {/* 복사, 재생성, 피드백 */}
                </div>
            )}
        </div>
    );
}
```

### 로딩 상태의 단계별 피드백

```javascript
// 사용자에게 진행 상황을 알려주기
const loadingStages = {
    'connecting': '서버에 연결하는 중...',
    'processing': '질문을 분석하는 중...',
    'generating': '답변을 생성하는 중...',
    'finalizing': '답변을 정리하는 중...',
};

function AILoadingIndicator({ stage, elapsed }) {
    return (
        <div className="ai-loading">
            <div className="dots-animation">
                <span>●</span><span>●</span><span>●</span>
            </div>
            <p>{loadingStages[stage]}</p>
            {elapsed > 3000 && (
                <p className="patience-message">
                    조금만 더 기다려주세요...
                </p>
            )}
            {elapsed > 8000 && (
                <button onClick={handleCancel}>
                    취소하기
                </button>
            )}
        </div>
    );
}
```

### Python 백엔드에서 진행 상황 전달

```python
# streaming_with_progress.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.post("/api/chat/progress")
async def chat_with_progress(message: str):
    """진행 상황을 포함한 스트리밍"""

    async def generate():
        # 1. 시작 알림
        yield f"data: {json.dumps({'type': 'status', 'stage': 'connecting'})}\n\n"

        # 2. 질문 분석
        yield f"data: {json.dumps({'type': 'status', 'stage': 'processing'})}\n\n"

        # 3. 답변 생성 시작
        yield f"data: {json.dumps({'type': 'status', 'stage': 'generating'})}\n\n"

        # 4. 스트리밍 응답
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({
                    'type': 'content',
                    'text': chunk.choices[0].delta.content
                })}\n\n"

        # 5. 완료
        yield f"data: {json.dumps({'type': 'status', 'stage': 'done'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## 3. 스트리밍 응답 표시

### 타이핑 효과 구현

```javascript
// React 예시
function StreamingText({ finalText, speed = 30 }) {
    const [displayedText, setDisplayedText] = useState('');
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        if (currentIndex < finalText.length) {
            const timeout = setTimeout(() => {
                setDisplayedText(finalText.slice(0, currentIndex + 1));
                setCurrentIndex(currentIndex + 1);
            }, speed);

            return () => clearTimeout(timeout);
        }
    }, [finalText, currentIndex, speed]);

    return (
        <div className="streaming-text">
            {displayedText}
            {currentIndex < finalText.length && (
                <span className="cursor-blink">▊</span>
            )}
        </div>
    );
}
```

### 마크다운 실시간 렌더링

```javascript
import ReactMarkdown from 'react-markdown';

function StreamingMarkdown({ content }) {
    // 스트리밍 중에도 마크다운 렌더링
    return (
        <div className="markdown-content">
            <ReactMarkdown>{content}</ReactMarkdown>
            <TypingCursor />
        </div>
    );
}

// CSS
.markdown-content {
    /* 스트리밍 중 레이아웃이 흔들리지 않게 */
    min-height: 100px;
    transition: height 0.3s ease;
}

.typing-cursor {
    display: inline-block;
    width: 8px;
    height: 1em;
    background: #333;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
```

### 코드 블록 하이라이팅

```javascript
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

function StreamingCodeBlock({ code, language, isComplete }) {
    return (
        <div className="code-block">
            {isComplete ? (
                // 완료되면 하이라이팅
                <SyntaxHighlighter language={language}>
                    {code}
                </SyntaxHighlighter>
            ) : (
                // 스트리밍 중에는 기본 스타일
                <pre className="code-streaming">
                    <code>{code}</code>
                    <span className="cursor">▊</span>
                </pre>
            )}
            {isComplete && (
                <button onClick={() => copyToClipboard(code)}>
                    복사
                </button>
            )}
        </div>
    );
}
```

## 4. 에러 처리 및 재시도

### 사용자 친화적인 에러 메시지

```javascript
// ❌ 나쁜 예
function ErrorDisplay({ error }) {
    return <div>Error: {error.message}</div>;
}

// ✅ 좋은 예
function AIErrorDisplay({ error, onRetry }) {
    const errorMessages = {
        'rate_limit': {
            title: '잠시만 기다려주세요',
            message: '많은 요청으로 인해 대기 중입니다. 곧 다시 시도됩니다.',
            action: 'auto-retry',
            icon: '⏳'
        },
        'server_error': {
            title: '일시적인 문제가 발생했습니다',
            message: '서버에 문제가 있습니다. 잠시 후 다시 시도해주세요.',
            action: 'manual-retry',
            icon: '⚠️'
        },
        'token_limit': {
            title: '입력이 너무 깁니다',
            message: '메시지를 짧게 줄여주세요. (현재: 5000자, 최대: 4000자)',
            action: 'edit',
            icon: '📝'
        },
        'content_filter': {
            title: '부적절한 내용이 감지되었습니다',
            message: '다른 방식으로 질문해주세요.',
            action: 'none',
            icon: '🚫'
        }
    };

    const errorInfo = errorMessages[error.type] || {
        title: '오류가 발생했습니다',
        message: '다시 시도해주세요.',
        action: 'manual-retry',
        icon: '❌'
    };

    return (
        <div className="ai-error">
            <span className="error-icon">{errorInfo.icon}</span>
            <h3>{errorInfo.title}</h3>
            <p>{errorInfo.message}</p>

            {errorInfo.action === 'manual-retry' && (
                <button onClick={onRetry}>다시 시도</button>
            )}

            {errorInfo.action === 'auto-retry' && (
                <div className="auto-retry">
                    <Spinner />
                    <p>자동으로 재시도 중... ({retryCount}/3)</p>
                </div>
            )}
        </div>
    );
}
```

### 재시도 로직 with UX

```javascript
function useChatWithRetry() {
    const [retrying, setRetrying] = useState(false);
    const [retryCount, setRetryCount] = useState(0);

    const sendMessage = async (message, maxRetries = 3) => {
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                setRetryCount(attempt + 1);
                setRetrying(attempt > 0);

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message }),
                    signal: AbortSignal.timeout(30000), // 30초 타임아웃
                });

                if (!response.ok) {
                    if (response.status === 429) {
                        // Rate limit: 대기 후 재시도
                        const waitTime = Math.pow(2, attempt) * 1000;
                        await new Promise(resolve => setTimeout(resolve, waitTime));
                        continue;
                    }
                    throw new Error(`HTTP ${response.status}`);
                }

                setRetrying(false);
                setRetryCount(0);
                return await response.json();

            } catch (error) {
                if (attempt === maxRetries - 1) {
                    // 마지막 시도 실패
                    setRetrying(false);
                    throw error;
                }
                // 다음 시도 전 대기
                await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
            }
        }
    };

    return { sendMessage, retrying, retryCount };
}
```

## 5. 신뢰도 및 확률 표시

AI는 100% 정확하지 않으므로 신뢰도를 표시하는 것이 좋습니다.

### 신뢰도 표시 UI

```javascript
function AIResponse({ response, confidence }) {
    // confidence: 0.0 ~ 1.0

    const getConfidenceLevel = (score) => {
        if (score > 0.9) return { level: 'high', text: '매우 확실', color: 'green' };
        if (score > 0.7) return { level: 'medium', text: '확실', color: 'blue' };
        if (score > 0.5) return { level: 'low', text: '불확실', color: 'orange' };
        return { level: 'very-low', text: '매우 불확실', color: 'red' };
    };

    const confidenceInfo = getConfidenceLevel(confidence);

    return (
        <div className="ai-response">
            <div className="response-content">
                {response}
            </div>

            <div className="confidence-indicator">
                <span className={`badge ${confidenceInfo.color}`}>
                    {confidenceInfo.text}
                </span>
                <div className="confidence-bar">
                    <div
                        className="confidence-fill"
                        style={{
                            width: `${confidence * 100}%`,
                            backgroundColor: confidenceInfo.color
                        }}
                    />
                </div>
                <span className="confidence-score">
                    {(confidence * 100).toFixed(0)}%
                </span>
            </div>

            {confidence < 0.7 && (
                <div className="warning">
                    ⚠️ 이 답변은 불확실할 수 있습니다. 추가 확인을 권장합니다.
                </div>
            )}
        </div>
    );
}
```

### Python 백엔드에서 신뢰도 계산

```python
# confidence_calculation.py
from openai import OpenAI
import re

client = OpenAI()

def chat_with_confidence(message):
    """신뢰도 점수를 포함한 응답"""

    # 1. 일반 응답 생성
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
        temperature=0.7,
        n=1,  # 응답 개수
        logprobs=True,  # 확률 정보 포함
    )

    answer = response.choices[0].message.content

    # 2. 신뢰도 계산 (간단한 방법)
    # - 짧은 답변: 낮은 신뢰도
    # - "모르겠습니다", "확실하지 않습니다" 포함: 낮은 신뢰도
    # - 명확한 답변: 높은 신뢰도

    confidence = 0.8  # 기본값

    # 길이 기반
    if len(answer) < 50:
        confidence -= 0.2

    # 불확실 표현 감지
    uncertain_phrases = [
        "모르", "확실하지 않", "아마도", "~것 같", "추측",
        "정확하지 않", "불분명", "확인이 필요"
    ]

    for phrase in uncertain_phrases:
        if phrase in answer:
            confidence -= 0.3
            break

    # 명확한 답변 패턴
    if re.search(r'^\d+\.', answer):  # 번호 매긴 리스트
        confidence += 0.1

    if "입니다" in answer or "습니다" in answer:  # 단정적 어미
        confidence += 0.05

    # 0~1 범위로 제한
    confidence = max(0.0, min(1.0, confidence))

    return {
        "response": answer,
        "confidence": confidence,
        "tokens": response.usage.total_tokens
    }

# FastAPI 엔드포인트
@app.post("/api/chat/confidence")
async def chat_endpoint(message: str):
    result = chat_with_confidence(message)
    return result
```

### 다중 응답 비교 (더 정확한 신뢰도)

```python
def chat_with_multiple_responses(message, n=3):
    """여러 응답을 생성하고 일치도로 신뢰도 측정"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
        temperature=0.7,
        n=n,  # 3개의 응답 생성
    )

    answers = [choice.message.content for choice in response.choices]

    # 가장 긴 답변을 대표 답변으로
    best_answer = max(answers, key=len)

    # 유사도 계산 (간단하게 공통 단어 비율)
    def calculate_similarity(answers):
        words_sets = [set(ans.split()) for ans in answers]
        common_words = words_sets[0].intersection(*words_sets[1:])
        all_words = set().union(*words_sets)

        return len(common_words) / len(all_words) if all_words else 0

    similarity = calculate_similarity(answers)

    return {
        "response": best_answer,
        "confidence": similarity,
        "alternative_count": n
    }
```

## 6. 사용자 피드백 수집

사용자 피드백은 AI 모델 개선에 필수적입니다.

### 피드백 UI 패턴

```javascript
function AIMessageWithFeedback({ message, messageId }) {
    const [feedback, setFeedback] = useState(null);
    const [showDetail, setShowDetail] = useState(false);

    const handleFeedback = async (type) => {
        setFeedback(type);

        // 간단한 피드백은 바로 전송
        if (type === 'good') {
            await fetch('/api/feedback', {
                method: 'POST',
                body: JSON.stringify({
                    messageId,
                    type: 'thumbs_up',
                })
            });
        } else {
            // 부정적 피드백은 상세 이유 수집
            setShowDetail(true);
        }
    };

    return (
        <div className="ai-message">
            <div className="message-content">
                {message}
            </div>

            <div className="feedback-buttons">
                <button
                    onClick={() => handleFeedback('good')}
                    className={feedback === 'good' ? 'active' : ''}
                >
                    👍 도움됨
                </button>
                <button
                    onClick={() => handleFeedback('bad')}
                    className={feedback === 'bad' ? 'active' : ''}
                >
                    👎 도움 안됨
                </button>

                <button onClick={() => handleCopy(message)}>
                    📋 복사
                </button>

                <button onClick={() => handleRegenerate(messageId)}>
                    🔄 다시 생성
                </button>
            </div>

            {showDetail && (
                <div className="feedback-detail">
                    <h4>어떤 점이 문제였나요?</h4>
                    <label>
                        <input type="checkbox" value="incorrect" />
                        잘못된 정보
                    </label>
                    <label>
                        <input type="checkbox" value="irrelevant" />
                        질문과 관련 없음
                    </label>
                    <label>
                        <input type="checkbox" value="incomplete" />
                        불완전한 답변
                    </label>
                    <label>
                        <input type="checkbox" value="harmful" />
                        부적절한 내용
                    </label>

                    <textarea
                        placeholder="추가 의견을 입력해주세요 (선택사항)"
                    />

                    <button onClick={submitDetailedFeedback}>
                        제출
                    </button>
                </div>
            )}
        </div>
    );
}
```

### Python 백엔드 피드백 저장

```python
# feedback_collection.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI()

class Feedback(BaseModel):
    message_id: str
    type: str  # 'thumbs_up', 'thumbs_down'
    reasons: list[str] = []
    comment: str = ""
    user_id: str = None

@app.post("/api/feedback")
async def collect_feedback(feedback: Feedback):
    """피드백 수집 및 저장"""

    feedback_data = {
        "message_id": feedback.message_id,
        "type": feedback.type,
        "reasons": feedback.reasons,
        "comment": feedback.comment,
        "user_id": feedback.user_id,
        "timestamp": datetime.now().isoformat(),
    }

    # 실제로는 데이터베이스에 저장
    # db.feedbacks.insert_one(feedback_data)

    # 로그 파일에 저장 (임시)
    with open("feedbacks.jsonl", "a") as f:
        f.write(json.dumps(feedback_data, ensure_ascii=False) + "\n")

    # 부정적 피드백이 많으면 알림
    if feedback.type == "thumbs_down":
        # 슬랙/이메일 알림
        await notify_team(f"부정적 피드백: {feedback.message_id}")

    return {"success": True}

@app.get("/api/feedback/stats")
async def feedback_stats():
    """피드백 통계"""
    # 실제로는 DB에서 집계
    return {
        "total": 1523,
        "thumbs_up": 1234,
        "thumbs_down": 289,
        "satisfaction_rate": 0.81,
        "common_issues": [
            {"issue": "incorrect", "count": 120},
            {"issue": "irrelevant", "count": 89},
            {"issue": "incomplete", "count": 80},
        ]
    }
```

## 7. 입력 제한 및 가이드

사용자가 효과적인 질문을 하도록 돕습니다.

### 입력 가이드 UI

```javascript
function ChatInput({ onSend, maxTokens = 4000 }) {
    const [input, setInput] = useState('');
    const [tokenCount, setTokenCount] = useState(0);

    // 간단한 토큰 추정 (실제로는 tiktoken 사용)
    const estimateTokens = (text) => {
        return Math.ceil(text.length / 4);  // 한글: ~4자당 1토큰
    };

    useEffect(() => {
        setTokenCount(estimateTokens(input));
    }, [input]);

    const isOverLimit = tokenCount > maxTokens;

    return (
        <div className="chat-input">
            <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="메시지를 입력하세요..."
                maxLength={maxTokens * 4}
            />

            <div className="input-info">
                <div className={`token-count ${isOverLimit ? 'over-limit' : ''}`}>
                    {tokenCount} / {maxTokens} 토큰
                    {isOverLimit && (
                        <span className="warning">⚠️ 입력이 너무 깁니다</span>
                    )}
                </div>

                <button
                    onClick={() => onSend(input)}
                    disabled={!input.trim() || isOverLimit}
                >
                    전송
                </button>
            </div>

            {!input && (
                <div className="suggestions">
                    <p>이렇게 질문해보세요:</p>
                    <button onClick={() => setInput("Python 리스트와 튜플의 차이를 예시와 함께 설명해줘")}>
                        Python 리스트와 튜플의 차이는?
                    </button>
                    <button onClick={() => setInput("FastAPI로 간단한 REST API 만드는 방법을 알려줘")}>
                        FastAPI 사용법
                    </button>
                </div>
            )}
        </div>
    );
}
```

## 8. 실전 예시: 완전한 챗봇 UI

모든 패턴을 종합한 예시입니다.

```javascript
// ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';

function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [status, setStatus] = useState('idle');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(scrollToBottom, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = {
            id: Date.now(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setStatus('thinking');

        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input }),
            });

            const aiMessage = {
                id: Date.now() + 1,
                role: 'assistant',
                content: '',
                timestamp: new Date(),
                confidence: null,
            };

            setMessages(prev => [...prev, aiMessage]);
            setStatus('streaming');

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
                        if (content === '[DONE]') {
                            setStatus('done');
                            break;
                        }

                        setMessages(prev => {
                            const updated = [...prev];
                            updated[updated.length - 1].content += content;
                            return updated;
                        });
                    }
                }
            }

        } catch (error) {
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                role: 'error',
                content: '오류가 발생했습니다. 다시 시도해주세요.',
                error: error.message,
            }]);
            setStatus('error');
        }
    };

    return (
        <div className="chat-interface">
            <div className="messages">
                {messages.map(msg => (
                    <Message
                        key={msg.id}
                        message={msg}
                        isStreaming={status === 'streaming' && msg.role === 'assistant'}
                    />
                ))}

                {status === 'thinking' && (
                    <div className="thinking-indicator">
                        <div className="dots">●●●</div>
                        <p>답변을 생성하고 있습니다...</p>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            <ChatInput
                value={input}
                onChange={setInput}
                onSend={sendMessage}
                disabled={status !== 'idle' && status !== 'done'}
            />
        </div>
    );
}
```

## 요약

### AI UX의 핵심 원칙
1. **투명성**: AI가 무엇을 하고 있는지 명확히 알려주기
2. **피드백**: 진행 상황을 지속적으로 표시
3. **에러 관리**: 실패를 우아하게 처리하고 대안 제시
4. **신뢰도**: AI의 한계를 명시하고 확률 표시
5. **학습**: 사용자 피드백으로 지속적 개선

### 체크리스트
- [ ] 로딩 상태 (3단계: 대기, 생성, 완료)
- [ ] 스트리밍 응답 (타이핑 효과)
- [ ] 에러 처리 (재시도, 폴백)
- [ ] 신뢰도 표시
- [ ] 사용자 피드백 수집
- [ ] 토큰 제한 안내
- [ ] 응답 복사/재생성 기능
- [ ] 접근성 (키보드 네비게이션, 스크린 리더)

다음 문서에서는 성능 최적화를 다룹니다!
