"""
AsyncIO 기초 (비동기)

I/O-bound 작업에 최적 (Threading보다 효율적)
- 수백~수천 개의 네트워크 요청
- WebSocket 연결
- 비동기 DB 쿼리

JavaScript 개발자에게 가장 익숙한 방식!
- async/await 문법이 거의 동일
- Promise.all = asyncio.gather
- 싱글 스레드 이벤트 루프
"""
import asyncio
import time
import aiohttp  # pip install aiohttp
from typing import List


# ============================================================
# 예제 1: async/await 기본 문법
# ============================================================

async def say_hello(name: str, delay: int):
    """
    비동기 함수 (코루틴)

    async def: 비동기 함수 정의
    await: 비동기 작업 대기 (논블로킹)
    """
    print(f"{name}: 시작")
    await asyncio.sleep(delay)  # 논블로킹 대기 (다른 작업 가능)
    print(f"{name}: {delay}초 대기 완료")
    return f"Hello, {name}!"


async def example1_basic_async():
    """기본 async/await 사용법"""
    print("\n" + "=" * 60)
    print("예제 1: async/await 기본 문법")
    print("=" * 60)

    # 순차 실행 (느림)
    print("\n[순차 실행 - await 연속]")
    start = time.time()
    result1 = await say_hello("Alice", 2)
    result2 = await say_hello("Bob", 1)
    result3 = await say_hello("Charlie", 3)
    sequential_time = time.time() - start
    print(f"순차 실행 시간: {sequential_time:.2f}초")

    # 동시 실행 (빠름) - asyncio.gather
    print("\n[동시 실행 - asyncio.gather]")
    start = time.time()

    # asyncio.gather: 여러 코루틴을 동시 실행
    # JavaScript의 Promise.all과 동일!
    results = await asyncio.gather(
        say_hello("Alice", 2),
        say_hello("Bob", 1),
        say_hello("Charlie", 3)
    )

    concurrent_time = time.time() - start
    print(f"동시 실행 시간: {concurrent_time:.2f}초")
    print(f"속도 향상: {sequential_time / concurrent_time:.1f}배")
    print(f"결과: {results}")


# ============================================================
# 예제 2: 비동기 HTTP 요청
# ============================================================

async def fetch_url(session: aiohttp.ClientSession, url: str) -> dict:
    """
    비동기 HTTP 요청

    aiohttp: async/await를 지원하는 HTTP 클라이언트
    requests는 동기식이므로 asyncio와 함께 사용 불가!
    """
    print(f"요청 시작: {url}")
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            data = await response.json()
            print(f"요청 완료: {url} (상태: {response.status})")
            return {"url": url, "status": response.status, "data": data}
    except Exception as e:
        print(f"요청 실패: {url}, 에러: {type(e).__name__}")
        return {"url": url, "error": str(e)}


async def example2_async_http():
    """비동기 HTTP 요청"""
    print("\n" + "=" * 60)
    print("예제 2: 비동기 HTTP 요청")
    print("=" * 60)

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    start = time.time()

    # ClientSession: 연결 재사용으로 성능 향상
    async with aiohttp.ClientSession() as session:
        # 모든 요청을 동시에 실행
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    elapsed = time.time() - start

    print(f"\n총 {len(urls)}개 요청 완료")
    print(f"소요 시간: {elapsed:.2f}초")
    print(f"순차 실행 예상 시간: ~{len(urls)}초")
    print(f"동시 실행으로 {len(urls) / elapsed:.1f}배 빠름!")


# ============================================================
# 예제 3: asyncio.create_task (백그라운드 실행)
# ============================================================

async def background_task(task_id: int):
    """백그라운드에서 실행될 작업"""
    print(f"[작업 {task_id}] 시작")
    await asyncio.sleep(2)
    print(f"[작업 {task_id}] 완료")
    return f"작업 {task_id} 결과"


async def example3_create_task():
    """
    asyncio.create_task: 태스크를 즉시 시작

    create_task vs await:
    - create_task: 즉시 시작, 나중에 결과 확인
    - await: 완료될 때까지 대기
    """
    print("\n" + "=" * 60)
    print("예제 3: asyncio.create_task (백그라운드 실행)")
    print("=" * 60)

    # 태스크 생성 (즉시 시작)
    task1 = asyncio.create_task(background_task(1))
    task2 = asyncio.create_task(background_task(2))
    task3 = asyncio.create_task(background_task(3))

    print("모든 태스크 시작됨!")

    # 다른 작업 수행 가능
    print("다른 작업 수행 중...")
    await asyncio.sleep(1)
    print("다른 작업 완료")

    # 태스크 결과 대기
    results = await asyncio.gather(task1, task2, task3)
    print(f"\n태스크 결과: {results}")


# ============================================================
# 예제 4: asyncio.wait_for (타임아웃)
# ============================================================

async def slow_operation():
    """느린 작업 (3초 소요)"""
    print("느린 작업 시작...")
    await asyncio.sleep(3)
    return "완료!"


async def example4_timeout():
    """타임아웃 처리"""
    print("\n" + "=" * 60)
    print("예제 4: asyncio.wait_for (타임아웃)")
    print("=" * 60)

    # 타임아웃 2초
    try:
        print("타임아웃 2초로 설정")
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
        print(f"결과: {result}")
    except asyncio.TimeoutError:
        print("타임아웃 발생! ⏰")

    # 타임아웃 5초 (성공)
    try:
        print("\n타임아웃 5초로 설정")
        result = await asyncio.wait_for(slow_operation(), timeout=5.0)
        print(f"결과: {result}")
    except asyncio.TimeoutError:
        print("타임아웃 발생!")


# ============================================================
# 예제 5: 동시 실행 제한 (Semaphore)
# ============================================================

async def limited_task(task_id: int, semaphore: asyncio.Semaphore):
    """
    Semaphore로 동시 실행 수 제한

    너무 많은 동시 연결은:
    - 서버 과부하
    - 메모리 부족
    - Rate Limit 초과
    """
    async with semaphore:  # 세마포어 획득
        print(f"[작업 {task_id}] 시작 (현재 실행 중: {semaphore._value})")
        await asyncio.sleep(1)
        print(f"[작업 {task_id}] 완료")
        return f"결과_{task_id}"


async def example5_semaphore():
    """Semaphore로 동시 실행 제한"""
    print("\n" + "=" * 60)
    print("예제 5: Semaphore (동시 실행 제한)")
    print("=" * 60)

    # 최대 3개까지만 동시 실행
    semaphore = asyncio.Semaphore(3)

    # 10개 작업 생성
    tasks = [limited_task(i, semaphore) for i in range(10)]

    print("10개 작업 시작 (최대 3개씩 동시 실행)\n")
    results = await asyncio.gather(*tasks)

    print(f"\n모든 작업 완료: {len(results)}개")


# ============================================================
# 예제 6: 에러 처리
# ============================================================

async def task_with_error(task_id: int):
    """에러가 발생할 수 있는 작업"""
    await asyncio.sleep(1)
    if task_id == 2:
        raise ValueError(f"작업 {task_id}에서 에러 발생!")
    return f"작업 {task_id} 성공"


async def example6_error_handling():
    """비동기 에러 처리"""
    print("\n" + "=" * 60)
    print("예제 6: 에러 처리")
    print("=" * 60)

    # gather의 return_exceptions=True: 에러를 예외로 던지지 않고 결과에 포함
    results = await asyncio.gather(
        task_with_error(1),
        task_with_error(2),  # 에러 발생
        task_with_error(3),
        return_exceptions=True  # 중요!
    )

    print("\n결과:")
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"  작업 {i}: 에러 - {result}")
        else:
            print(f"  작업 {i}: {result}")


# ============================================================
# JavaScript와 비교
# ============================================================

async def javascript_comparison():
    """
    JavaScript async/await와 비교

    JavaScript:
    ```javascript
    // 비동기 함수
    async function fetchData() {
        const response = await fetch('https://api.example.com');
        const data = await response.json();
        return data;
    }

    // 동시 실행
    const results = await Promise.all([
        fetchData(),
        fetchData(),
        fetchData()
    ]);

    // 타임아웃
    const result = await Promise.race([
        fetchData(),
        new Promise((_, reject) =>
            setTimeout(() => reject('Timeout'), 5000)
        )
    ]);
    ```

    Python:
    ```python
    # 비동기 함수
    async def fetch_data():
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.example.com') as response:
                data = await response.json()
                return data

    # 동시 실행
    results = await asyncio.gather(
        fetch_data(),
        fetch_data(),
        fetch_data()
    )

    # 타임아웃
    result = await asyncio.wait_for(fetch_data(), timeout=5.0)
    ```

    차이점:
    - Python은 명시적으로 이벤트 루프 실행 필요 (asyncio.run)
    - Python은 async 전용 라이브러리 필요 (aiohttp, asyncpg 등)
    - JavaScript는 기본적으로 비동기 (Node.js)
    """
    print("\n" + "=" * 60)
    print("JavaScript vs Python AsyncIO 비교")
    print("=" * 60)
    print("""
JavaScript:
- async/await 문법
- Promise.all() = asyncio.gather()
- Promise.race() = asyncio.wait(..., return_when=FIRST_COMPLETED)
- fetch() API (기본 제공)

Python:
- async/await 문법 (거의 동일!)
- asyncio.gather() = Promise.all()
- asyncio.wait_for() = 타임아웃
- aiohttp (별도 설치 필요)

공통점:
- 싱글 스레드 이벤트 루프
- 논블로킹 I/O
- I/O-bound 작업에 최적
    """)


# ============================================================
# 실습 문제
# ============================================================

async def exercise():
    """
    실습: 여러 API 동시 호출하기

    JSONPlaceholder API를 사용하여 여러 사용자 정보 가져오기
    """
    print("\n" + "=" * 60)
    print("실습 문제: 여러 API 동시 호출")
    print("=" * 60)

    async def fetch_user(session: aiohttp.ClientSession, user_id: int):
        """
        TODO: 이 함수를 완성하세요

        1. GET https://jsonplaceholder.typicode.com/users/{user_id}
        2. JSON 응답 파싱
        3. 사용자 이름 반환
        """
        url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
        async with session.get(url) as response:
            user = await response.json()
            return user.get("name", "Unknown")

    # TODO: 1~10번 사용자 정보를 동시에 가져오기
    # 힌트: asyncio.gather 사용
    user_ids = range(1, 11)

    start = time.time()

    async with aiohttp.ClientSession() as session:
        # 여기에 코드 작성
        tasks = [fetch_user(session, user_id) for user_id in user_ids]
        names = await asyncio.gather(*tasks)

    elapsed = time.time() - start

    print(f"\n가져온 사용자: {len(names)}명")
    print(f"소요 시간: {elapsed:.2f}초")
    print(f"사용자 이름: {names[:3]}...")  # 처음 3명만 출력


# ============================================================
# 메인 실행
# ============================================================

async def main():
    """
    모든 예제 실행

    asyncio.run(main())으로 이벤트 루프 시작
    """
    print("""
╔══════════════════════════════════════════════════════════╗
║           Python AsyncIO 기초 학습                        ║
║                                                          ║
║  JavaScript 개발자에게 가장 익숙한 방식!                  ║
║  async/await 문법, 싱글 스레드 이벤트 루프                 ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 모든 예제 실행
    await example1_basic_async()
    await example2_async_http()
    await example3_create_task()
    await example4_timeout()
    await example5_semaphore()
    await example6_error_handling()
    await javascript_comparison()

    # 실습 문제
    await exercise()

    print("\n" + "=" * 60)
    print("학습 완료! 다음은 4_comparison.py를 실행해보세요.")
    print("=" * 60)


if __name__ == "__main__":
    # asyncio.run(): 이벤트 루프 생성 및 실행
    # JavaScript와 달리 명시적으로 이벤트 루프 시작 필요
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n프로그램 종료")
