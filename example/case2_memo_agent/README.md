# Case2 Memo Agent

FastMCP 기반 MCP 서버를 통해 `fastapi-example`의 TODO(메모) API를 도구로 노출합니다. MCP 클라이언트는 이 서버를 통해 BE REST API를 호출하여 메모를 조회/생성/수정/삭제할 수 있습니다.

## 요구사항

- Python 3.11+
- FastAPI 메모 앱이 실행 중이어야 합니다. (예: `fastapi-example`에서 `uv run uvicorn app.main:app --reload`)

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `MEMO_MCP_HOST` | `127.0.0.1` | MCP 서버 호스트 |
| `MEMO_MCP_PORT` | `8010` | MCP 서버 포트 |
| `MEMO_BE_API_URL` | `http://127.0.0.1:8000` | FastAPI 메모 앱의 베이스 URL |
| `MEMO_BE_TIMEOUT` | `30` | BE API 호출 타임아웃(초) |
| `OPENAI_API_KEY` | 없음 | LangGraph 에이전트에서 사용할 OpenAI API 키 |
| `OPENAI_MODEL` | `gpt-4o-mini` | ChatOpenAI가 사용할 모델명 |
| `MEMO_MCP_SERVER_URL` | `http://127.0.0.1:8010/mcp` | LangGraph 에이전트가 접속할 MCP endpoint |
| `MEMO_MCP_SERVER_NAME` | `memo` | MultiServerMCPClient에서 MCP 서버를 식별할 이름 |

`.env` 또는 쉘 환경에 값을 설정한 뒤 실행하세요.

## 실행

```bash
cd example/case2_memo_agent
uv run python memo_mcp_server.py
```

서버가 시작되면 MCP 호스트/포트 및 연결된 BE API 주소가 로그로 출력됩니다.

## LangGraph 메모 에이전트

1. FastAPI 메모 앱과 위 MCP 서버를 실행합니다.
2. OpenAI 키와 MCP endpoint 값을 `.env`에 채웁니다.
3. LangGraph 기반 에이전트 실행:

```bash
uv run python memo_agent.py
```

CLI에서 사용자 질문을 입력하면 ChatOpenAI + MultiServerMCPClient 조합으로 MCP 도구를 호출해 응답합니다.  
`종료`, `exit`, `quit` 등의 명령을 입력할 때까지 루프가 계속됩니다.

## 컴포넌트별 동작 흐름

1. **FastAPI 메모 앱 (`fastapi-example/app`)**
   - PostgreSQL(or SQLite)과 통신하며 `/todos` CRUD 및 `/health` 엔드포인트를 제공합니다.
2. **Memo MCP 서버 (`memo_mcp_server.py`)**
   - FastAPI 앱을 HTTP 클라이언트로 호출하는 MCP 도구 세트를 등록합니다.  
   - LangGraph 에이전트 등 MCP 클라이언트는 `streamable-http`(기본 `/mcp`)로 연결해 도구를 사용합니다.
3. **LangGraph 에이전트 (`memo_agent.py`)**
   - `MultiServerMCPClient`로 MCP 도구 메타데이터를 로드하고, 사용자 입력에 따라 ChatOpenAI → MCP 도구 호출 → 결과 요약 순서로 응답을 생성합니다.

전체 요청 플로우는 아래와 같습니다:

```
사용자 입력 → LangGraph 에이전트 ↔ ChatOpenAI
    ↳ 필요한 경우 MCP 도구 호출 (MultiServerMCPClient)
        ↳ Memo MCP 서버 → FastAPI 메모 앱 → DB
    ↳ 도구 결과 요약 → 사용자에게 응답
```

## LangGraph 노드 구성

LangGraph는 직접 정의한 2개의 노드와 조건 분기로 구성했습니다.

| 노드 | 설명 | 주요 입출력 |
|------|------|-------------|
| `model` | ChatOpenAI (`ChatOpenAI(model=OPENAI_MODEL, temperature=0.2)`)에 현재 메시지 히스토리를 전달해 다음 행동을 생성합니다. | 입력: `AgentState.messages`<br>출력: AIMessage (필요 시 tool_calls 포함) |
| `tools` | `model` 노드가 반환한 tool_calls를 순차 실행합니다. | 입력: 마지막 AIMessage의 `tool_calls`<br>출력: 각 호출 결과를 JSON 문자열로 입력한 `ToolMessage` 목록 |

분기 조건은 `model` 노드의 마지막 메시지가 tool call을 포함하는지 여부로 결정되며, `tools` 노드가 끝나면 다시 `model`로 돌아가 (필요 시 재요약) 최종 응답을 생성합니다.

### 프롬프트 구성

- **System Prompt** (`_build_system_prompt`): 사용 가능한 MCP 도구 목록과 행동 지침(한국어 응답, 도구 사용 전 추측 금지, 상태 변경 시 명시 등)을 명문화했습니다. 이 프롬프트는 `AgentState.messages`의 첫 메시지로 항상 유지됩니다.
- **User Prompt**: CLI 입력이 그대로 `HumanMessage`로 저장되어 LLM에 전달됩니다.
- **Tool Feedback**: 각 MCP 도구 결과는 `_stringify`된 JSON 문자열로 `ToolMessage`에 기록되어 LLM이 후속 reasoning에 활용합니다.

## 대화 히스토리 관리 방식

`AgentState`는 `messages: Annotated[List[BaseMessage], add_messages]`를 사용해 LangGraph가 메시지 리스트를 자동 병합하도록 구성했습니다.

1. 시작 시 `SystemMessage`만 포함된 상태로 그래프를 컴파일합니다.
2. 사용자 입력이 있을 때마다 `HumanMessage`를 `messages`에 append합니다.
3. `model` 노드와 `tools` 노드가 생성하는 `AIMessage` / `ToolMessage`는 `add_messages` 덕분에 리스트 끝에 추가되며, LangGraph가 상태를 반환할 때도 누적 유지됩니다.
4. 반복 루프 종료 전까지 같은 state 객체를 계속 넘겨 동일 세션 히스토리가 유지되며, 사용자가 `종료`를 입력하면 루프를 빠져나가면서 세션을 종료합니다.
