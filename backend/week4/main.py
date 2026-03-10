#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
내용
1. curl로 LLM 호출 예시
2. requests로 LLM 호출
3. OpenAI SDK로 LLM 호출
4. Tool Calling 간단 예제
5. LangChain LLM 호출
6. LangGraph Agent 예제
7. Git 협업 명령어

준비
uv venv
source .venv/bin/activate

uv pip install openai python-dotenv requests langchain-openai langchain-core langgraph

.env
OPENAI_API_KEY=sk-xxxx
"""

import os
import json

import requests
from dotenv import load_dotenv

# OpenAI SDK
from openai import OpenAI

# LangChain
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# LangGraph
from langgraph.prebuilt import create_react_agent

# ---------------------------------------------------
# 환경 설정
# ---------------------------------------------------

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise Exception("OPENAI_API_KEY 없음 (.env 확인)")

client = OpenAI()


# ---------------------------------------------------
# 1. curl 예시
# ---------------------------------------------------
def show_curl():
    print("\n===== CURL 호출 예시 =====\n")
    print(
        """
curl https://api.openai.com/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $OPENAI_API_KEY" \\
  -d '{
    "model": "gpt-4.1",
    "input": "hello"
  }'
"""
    )


# ---------------------------------------------------
# 2. requests로 호출
# ---------------------------------------------------
def call_requests():
    print("\n===== requests 호출 =====\n")
    url = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4.1",
        "input": "tool을 한 문장으로 설명해줘",
    }
    r = requests.post(url, headers=headers, json=payload)
    data = r.json()
    print(json.dumps(data, indent=2)[:500])


# ---------------------------------------------------
# 3. OpenAI SDK 호출
# ---------------------------------------------------
def call_openai():
    print("\n===== OpenAI SDK 호출 =====\n")
    resp = client.responses.create(
        model="gpt-4.1",
        input="LLM이 무엇인지 한 문장으로 설명해줘",
    )
    print(resp.output_text)


# ---------------------------------------------------
# 4. Tool Calling (아주 단순 예제)
# ---------------------------------------------------
# tool 함수
def add(a, b):
    return a + b

def tool_call_demo():
    print("\n===== Tool Calling =====\n")
    tools = [
        {
            "type": "function",
            "name": "add",
            "description": "두 숫자를 더한다",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        }
    ]
    resp = client.responses.create(
        model="gpt-4.1",
        input="3 + 7 계산해줘",
        tools=tools,
    )
    print(resp)


# ---------------------------------------------------
# 5. LangChain LLM 호출
# ---------------------------------------------------
def langchain_demo():
    print("\n===== LangChain =====\n")
    llm = ChatOpenAI(model="gpt-4o-mini")
    msg = llm.invoke("LangChain을 한 문장으로 설명해줘")
    print(msg.content)


# ---------------------------------------------------
# 6. LangGraph Agent
# ---------------------------------------------------
def langgraph_demo():
    print("\n===== LangGraph Agent =====\n")
    llm = ChatOpenAI(model="gpt-4o-mini")

    @tool
    def weather(city: str) -> str:
        """도시 날씨 조회"""
        return f"{city}는 맑음"
    agent = create_react_agent(llm, tools=[weather])
    result = agent.invoke({"messages": [("user", "서울 날씨 어때?")]})
    print(result["messages"][-1].content)


# ---------------------------------------------------
# 7. Git 협업 명령어
# ---------------------------------------------------
def git_help():
    print("\n===== Git 협업 =====\n")
    print(
        """
# 상태 확인
git status

# 브랜치 생성
git switch -c feature/test

# 커밋
git add .
git commit -m "feat: add feature"

# push
git push origin feature/test

# reset
git reset --soft HEAD~1
git reset --hard HEAD~1

# cherry-pick
git cherry-pick <commit>

# rebase
git fetch origin
git rebase origin/main
"""
    )


# ---------------------------------------------------
# main
# ---------------------------------------------------
def main():
    show_curl()
    call_requests()
    call_openai()
    tool_call_demo()
    langchain_demo()
    langgraph_demo()
    git_help()


if __name__ == "__main__":
    main()
