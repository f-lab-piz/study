#!/usr/bin/env python3
"""
LangChain + Langfuse 통합 예시

이 스크립트는 LangChain으로 간단한 챗봇을 만들고,
Langfuse로 모든 대화를 자동으로 추적하는 예시입니다.

실행 전에 .env 파일에 다음 변수를 설정하세요:
- OPENAI_API_KEY=sk-...
- LANGFUSE_PUBLIC_KEY=pk-lf-...
- LANGFUSE_SECRET_KEY=sk-lf-...
- LANGFUSE_HOST=http://localhost:3000

실행:
python langchain_langfuse_example.py
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser

from langfuse.callback import CallbackHandler

# 환경변수 로드
load_dotenv()

# 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")


def check_env_vars():
    """환경변수 확인"""
    missing = []

    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not LANGFUSE_PUBLIC_KEY:
        missing.append("LANGFUSE_PUBLIC_KEY")
    if not LANGFUSE_SECRET_KEY:
        missing.append("LANGFUSE_SECRET_KEY")

    if missing:
        print("❌ 다음 환경변수가 설정되지 않았습니다:")
        for var in missing:
            print(f"  - {var}")
        print("\n.env 파일을 생성하거나 환경변수를 설정하세요.")
        return False

    print("✅ 환경변수 로드 완료")
    return True


def example1_simple_chain():
    """예시 1: 간단한 체인 with Langfuse"""
    print("\n" + "="*50)
    print("예시 1: 간단한 체인")
    print("="*50)

    # Langfuse 콜백 핸들러
    langfuse_handler = CallbackHandler(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST
    )

    # 체인 구성
    prompt = ChatPromptTemplate.from_template("{topic}에 대해 한 문장으로 설명해줘")
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    parser = StrOutputParser()

    chain = prompt | llm | parser

    # 실행
    result = chain.invoke(
        {"topic": "LangChain"},
        config={"callbacks": [langfuse_handler]}
    )

    print(f"\n결과: {result}")
    print(f"\n✅ Langfuse 대시보드에서 확인: {LANGFUSE_HOST}")


def example2_conversational_chatbot():
    """예시 2: 대화형 챗봇 with Memory"""
    print("\n" + "="*50)
    print("예시 2: 대화형 챗봇 (메모리 포함)")
    print("="*50)

    # Langfuse 콜백 핸들러
    langfuse_handler = CallbackHandler(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST,
        user_id="demo-user",
        session_id="demo-session-001"
    )

    # 챗봇 설정
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        callbacks=[langfuse_handler]
    )

    memory = ConversationBufferMemory()

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )

    # 대화 시뮬레이션
    test_messages = [
        "안녕! 내 이름은 철수야.",
        "Python을 배우고 싶은데 어디서 시작하면 좋을까?",
        "내 이름이 뭐였지?",
    ]

    for msg in test_messages:
        print(f"\n사용자: {msg}")
        response = conversation.predict(input=msg)
        print(f"봇: {response}")

    print(f"\n✅ 전체 대화가 Langfuse에 기록되었습니다!")
    print(f"   Session ID: demo-session-001")
    print(f"   대시보드: {LANGFUSE_HOST}")


def example3_multi_step_pipeline():
    """예시 3: 여러 단계를 거치는 파이프라인"""
    print("\n" + "="*50)
    print("예시 3: 다단계 파이프라인")
    print("="*50)

    from langfuse import Langfuse

    # Langfuse 직접 초기화
    langfuse = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST
    )

    # Trace 생성
    trace = langfuse.trace(
        name="multi-step-pipeline",
        user_id="demo-user",
        metadata={"example": 3}
    )

    llm = ChatOpenAI()

    # Step 1: 아이디어 생성
    print("\nStep 1: 아이디어 생성 중...")
    span1 = trace.span(name="generate-idea")
    idea_prompt = "헬스케어 분야의 스타트업 아이디어 하나를 제시해줘"
    idea = llm.invoke(idea_prompt).content
    span1.end(input=idea_prompt, output=idea)
    print(f"아이디어: {idea[:100]}...")

    # Step 2: 아이디어 분석
    print("\nStep 2: 아이디어 분석 중...")
    span2 = trace.span(name="analyze-idea")
    analysis_prompt = f"다음 아이디어를 분석해줘:\n{idea}\n\n장단점을 각각 2가지씩 알려줘."
    analysis = llm.invoke(analysis_prompt).content
    span2.end(input=analysis_prompt, output=analysis)
    print(f"분석: {analysis[:100]}...")

    # Step 3: 개선안 제시
    print("\nStep 3: 개선안 제시 중...")
    span3 = trace.span(name="improve-idea")
    improve_prompt = f"이 분석을 바탕으로 개선안을 제시해줘:\n{analysis}"
    improvement = llm.invoke(improve_prompt).content
    span3.end(input=improve_prompt, output=improvement)
    print(f"개선안: {improvement[:100]}...")

    # Trace 종료
    trace.update(output=improvement)
    langfuse.flush()

    print(f"\n✅ 3단계 파이프라인이 Langfuse에 기록되었습니다!")
    print(f"   Trace: multi-step-pipeline")
    print(f"   대시보드: {LANGFUSE_HOST}")


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("LangChain + Langfuse 통합 예시")
    print("="*60)

    # 환경변수 확인
    if not check_env_vars():
        return

    # 예시 실행
    try:
        example1_simple_chain()
        example2_conversational_chatbot()
        example3_multi_step_pipeline()

        print("\n" + "="*60)
        print("모든 예시 완료!")
        print("="*60)
        print(f"\nLangfuse 대시보드에서 결과를 확인하세요:")
        print(f"👉 {LANGFUSE_HOST}")
        print("\n주요 기능:")
        print("- Traces: 모든 LLM 호출 과정 확인")
        print("- Analytics: 성능 메트릭 및 비용 분석")
        print("- Users: 사용자별 활동 추적")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
