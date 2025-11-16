"""LangGraph 기반 메모 관리 MCP 에이전트."""
from __future__ import annotations

import asyncio
import json
import os
from typing import Annotated, Any, Dict, List, cast

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

load_dotenv()

EXIT_KEYWORDS = {"exit", "quit", "종료", "그만", "끝", "q"}


class AgentState(TypedDict):
    """LangGraph 상태 정의."""

    messages: Annotated[List[BaseMessage], add_messages]


def _stringify(data: Any) -> str:
    if isinstance(data, str):
        return data
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        return str(data)


def _build_system_prompt(tool_map: Dict[str, BaseTool]) -> str:
    tool_lines = []
    for tool in tool_map.values():
        description = tool.description or "설명 없음"
        tool_lines.append(f"- {tool.name}: {description}")
    tool_catalog = "\n".join(tool_lines)
    return (
        "너는 LangGraph로 구현된 메모 관리 조수다. "
        "FastAPI 메모 BE와 연결된 MCP 도구만 사용하여 사실을 확인하고 작업을 처리한다. "
        "반드시 한국어로 답하며, 도구 호출 이유와 결과를 간결하게 요약하라. "
        "직접 추측하지 말고 필요한 경우 도구를 먼저 호출한 뒤 응답한다.\n\n"
        "사용 가능한 도구 목록:\n"
        f"{tool_catalog}\n\n"
        "응답 지침:\n"
        "1) 사용자가 요청한 목표를 다시 확인하고 필요한 경우 세부 정보를 질문하라.\n"
        "2) 도구 결과에서 중요한 포인트만 요약하고, 추가 후속 행동을 제안하라.\n"
        "3) 상태 변화 작업(create/update/delete)을 수행했으면 변경 내용을 명확히 명시하라.\n"
        "4) 대화가 끝났다고 느끼더라도 사용자가 '종료'를 요청하기 전까지는 인사를 하고 다음 입력을 기다리겠다고 알려라.\n"
    )


def _create_graph(llm: ChatOpenAI, tool_map: Dict[str, BaseTool]) -> StateGraph:
    llm_with_tools = llm.bind_tools(list(tool_map.values()))

    async def call_model(state: AgentState) -> AgentState:
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    async def call_tools(state: AgentState) -> AgentState:
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None) or []
        outputs: List[ToolMessage] = []

        for call in tool_calls:
            tool_name = call.get("name")
            tool_args = call.get("args") or {}
            tool_call_id = call.get("id", tool_name or "tool-call")
            tool = tool_map.get(tool_name or "")
            if tool is None:
                error_text = f"{tool_name} 도구를 찾을 수 없습니다."
                outputs.append(ToolMessage(content=error_text, tool_call_id=tool_call_id))
                continue

            print(f"🛠️  {tool_name} 호출: {_stringify(tool_args)}")
            try:
                result = await tool.ainvoke(tool_args)
                outputs.append(
                    ToolMessage(
                        content=_stringify(result),
                        tool_call_id=tool_call_id,
                    )
                )
                print(f"✅ {tool_name} 결과: {_stringify(result)}")
            except Exception as exc:  # noqa: BLE001
                error_text = f"{tool_name} 실행 중 오류: {exc}"
                outputs.append(ToolMessage(content=error_text, tool_call_id=tool_call_id))
                print(f"❌ {error_text}")

        return {"messages": outputs}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
            return "tools"
        return "respond"

    builder = StateGraph(AgentState)
    builder.add_node("model", call_model)
    builder.add_node("tools", call_tools)

    builder.set_entry_point("model")
    builder.add_conditional_edges(
        "model",
        should_continue,
        {
            "tools": "tools",
            "respond": END,
        },
    )
    builder.add_edge("tools", "model")

    return builder.compile()


async def _ainput(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)


def _get_memo_mcp_url() -> str:
    explicit = os.getenv("MEMO_MCP_SERVER_URL") or os.getenv("MEMO_MCP_AGENT_URL")
    if explicit:
        return explicit
    host = os.getenv("MEMO_MCP_HOST", "127.0.0.1")
    port = os.getenv("MEMO_MCP_PORT", "8010")
    return f"http://{host}:{port}/mcp"


async def prepare_agent() -> tuple[StateGraph, AgentState]:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY 환경 변수를 설정하세요.")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    server_name = os.getenv("MEMO_MCP_SERVER_NAME", "memo")
    server_url = _get_memo_mcp_url()
    connection = cast(
        StreamableHttpConnection,
        {
            "transport": "streamable_http",
            "url": server_url,
        },
    )
    client = MultiServerMCPClient({server_name: connection})
    tools = await client.get_tools(server_name=server_name)
    if not tools:
        raise RuntimeError("MCP 서버에서 사용할 수 있는 도구를 찾지 못했습니다.")

    tool_map = {tool.name: tool for tool in tools}
    system_prompt = _build_system_prompt(tool_map)

    llm = ChatOpenAI(model=model_name, temperature=0.2)
    graph = _create_graph(llm, tool_map)

    base_state: AgentState = {
        "messages": [SystemMessage(content=system_prompt)],
    }
    return graph, base_state


async def run_cli() -> None:
    graph, state = await prepare_agent()
    print("✅ LangGraph 메모 에이전트가 준비되었습니다. (종료하려면 '종료', 'exit' 등을 입력하세요)\n")

    while True:
        try:
            user_text = (await _ainput("사용자> ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 대화를 종료합니다.")
            break

        if not user_text:
            continue

        if user_text.lower() in EXIT_KEYWORDS or user_text in EXIT_KEYWORDS:
            print("👋 요청에 따라 대화를 종료합니다.")
            break

        state["messages"].append(HumanMessage(content=user_text))
        try:
            new_state = await graph.ainvoke(state)
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  에이전트 실행 오류: {exc}")
            state["messages"].pop()
            continue

        state = {"messages": new_state["messages"]}
        ai_message = next(
            (msg for msg in reversed(state["messages"]) if isinstance(msg, AIMessage)),
            None,
        )
        if ai_message:
            print(f"에이전트> {ai_message.content}\n")
        else:
            print("에이전트> (응답을 생성하지 못했습니다)\n")

    print("✅ 세션 종료 완료.")


def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
