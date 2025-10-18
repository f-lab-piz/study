"""
Threading vs Multiprocessing vs AsyncIO 성능 비교

실제 벤치마크를 통해 각 방식의 특성 이해
"""
import asyncio
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import aiohttp
import requests


# ============================================================
# I/O-bound 작업 테스트 (네트워크 요청)
# ============================================================

def io_bound_sync(url: str) -> dict:
    """동기식 HTTP 요청 (requests)"""
    try:
        response = requests.get(url, timeout=10)
        return {"url": url, "status": response.status_code}
    except Exception as e:
        return {"url": url, "error": str(e)}


async def io_bound_async(session: aiohttp.ClientSession, url: str) -> dict:
    """비동기 HTTP 요청 (aiohttp)"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            return {"url": url, "status": response.status}
    except Exception as e:
        return {"url": url, "error": str(e)}


def benchmark_io_bound():
    """I/O-bound 작업 벤치마크"""
    print("\n" + "=" * 70)
    print("벤치마크 1: I/O-bound 작업 (HTTP 요청 20개)")
    print("=" * 70)

    # 테스트 URL (지연 시간 1초)
    urls = ["https://httpbin.org/delay/1"] * 20

    # 1. 순차 실행
    print("\n[1] 순차 실행 (Synchronous)")
    start = time.time()
    results = [io_bound_sync(url) for url in urls]
    sequential_time = time.time() - start
    print(f"   시간: {sequential_time:.2f}초")
    print(f"   성공: {sum(1 for r in results if 'status' in r)}개")

    # 2. Threading
    print("\n[2] Threading (ThreadPoolExecutor)")
    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(io_bound_sync, urls))
    threading_time = time.time() - start
    print(f"   시간: {threading_time:.2f}초")
    print(f"   성공: {sum(1 for r in results if 'status' in r)}개")
    print(f"   속도: {sequential_time / threading_time:.1f}배 빠름 ⚡")

    # 3. AsyncIO
    print("\n[3] AsyncIO (asyncio.gather)")

    async def async_test():
        async with aiohttp.ClientSession() as session:
            tasks = [io_bound_async(session, url) for url in urls]
            return await asyncio.gather(*tasks)

    start = time.time()
    results = asyncio.run(async_test())
    asyncio_time = time.time() - start
    print(f"   시간: {asyncio_time:.2f}초")
    print(f"   성공: {sum(1 for r in results if 'status' in r)}개")
    print(f"   속도: {sequential_time / asyncio_time:.1f}배 빠름 ⚡⚡")

    # 4. Multiprocessing (비교용 - 비효율적!)
    print("\n[4] Multiprocessing (참고용 - 비효율적!)")
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(io_bound_sync, urls[:8]))  # 적은 수만 테스트
    multiprocessing_time = time.time() - start
    print(f"   시간: {multiprocessing_time:.2f}초 (8개만 테스트)")
    print(f"   → 프로세스 생성 오버헤드 때문에 느림 ❌")

    # 결과 요약
    print("\n" + "-" * 70)
    print("결과 요약 (I/O-bound 작업):")
    print(f"  순차 실행:        {sequential_time:.2f}초 (기준)")
    print(f"  Threading:        {threading_time:.2f}초 ({sequential_time/threading_time:.1f}배)")
    print(f"  AsyncIO:          {asyncio_time:.2f}초 ({sequential_time/asyncio_time:.1f}배) ⭐ 가장 빠름!")
    print(f"  Multiprocessing:  비효율적 (오버헤드 큼)")


# ============================================================
# CPU-bound 작업 테스트 (복잡한 계산)
# ============================================================

def cpu_bound_task(n: int) -> int:
    """CPU 집약적 작업"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result


async def cpu_bound_async(n: int) -> int:
    """AsyncIO로 CPU 작업 (효과 없음!)"""
    return cpu_bound_task(n)


def benchmark_cpu_bound():
    """CPU-bound 작업 벤치마크"""
    print("\n" + "=" * 70)
    print("벤치마크 2: CPU-bound 작업 (복잡한 계산 4개)")
    print("=" * 70)

    n = 5_000_000
    num_tasks = 4

    # 1. 순차 실행
    print("\n[1] 순차 실행")
    start = time.time()
    results = [cpu_bound_task(n) for _ in range(num_tasks)]
    sequential_time = time.time() - start
    print(f"   시간: {sequential_time:.2f}초")

    # 2. Threading (GIL 때문에 느림!)
    print("\n[2] Threading")
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_bound_task, [n] * num_tasks))
    threading_time = time.time() - start
    print(f"   시간: {threading_time:.2f}초")
    print(f"   속도: {sequential_time / threading_time:.1f}배")
    print(f"   → GIL 때문에 거의 빨라지지 않음 ❌")

    # 3. AsyncIO (효과 없음!)
    print("\n[3] AsyncIO")

    async def async_test():
        tasks = [cpu_bound_async(n) for _ in range(num_tasks)]
        return await asyncio.gather(*tasks)

    start = time.time()
    results = asyncio.run(async_test())
    asyncio_time = time.time() - start
    print(f"   시간: {asyncio_time:.2f}초")
    print(f"   → CPU 작업에는 효과 없음 ❌")

    # 4. Multiprocessing (빠름!)
    print("\n[4] Multiprocessing")
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_bound_task, [n] * num_tasks))
    multiprocessing_time = time.time() - start
    print(f"   시간: {multiprocessing_time:.2f}초")
    print(f"   속도: {sequential_time / multiprocessing_time:.1f}배 ⚡")
    print(f"   → GIL 우회로 진짜 병렬 처리! ✅")

    # 결과 요약
    print("\n" + "-" * 70)
    print("결과 요약 (CPU-bound 작업):")
    print(f"  순차 실행:        {sequential_time:.2f}초 (기준)")
    print(f"  Threading:        {threading_time:.2f}초 ({sequential_time/threading_time:.1f}배) - GIL로 효과 없음")
    print(f"  AsyncIO:          {asyncio_time:.2f}초 - CPU 작업엔 부적합")
    print(f"  Multiprocessing:  {multiprocessing_time:.2f}초 ({sequential_time/multiprocessing_time:.1f}배) ⭐ 가장 빠름!")


# ============================================================
# 혼합 작업 테스트
# ============================================================

def mixed_task(task_id: int):
    """혼합 작업: I/O + CPU"""
    # I/O 작업 시뮬레이션
    time.sleep(0.5)

    # CPU 작업
    result = 0
    for i in range(1_000_000):
        result += i ** 2

    return {"task_id": task_id, "result": result}


def benchmark_mixed():
    """혼합 작업 벤치마크"""
    print("\n" + "=" * 70)
    print("벤치마크 3: 혼합 작업 (I/O + CPU, 8개)")
    print("=" * 70)

    num_tasks = 8

    # 1. 순차 실행
    print("\n[1] 순차 실행")
    start = time.time()
    results = [mixed_task(i) for i in range(num_tasks)]
    sequential_time = time.time() - start
    print(f"   시간: {sequential_time:.2f}초")

    # 2. Threading
    print("\n[2] Threading")
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(mixed_task, range(num_tasks)))
    threading_time = time.time() - start
    print(f"   시간: {threading_time:.2f}초")
    print(f"   속도: {sequential_time / threading_time:.1f}배")
    print(f"   → I/O 부분만 병렬화 (부분적 개선)")

    # 3. Multiprocessing
    print("\n[3] Multiprocessing")
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(mixed_task, range(num_tasks)))
    multiprocessing_time = time.time() - start
    print(f"   시간: {multiprocessing_time:.2f}초")
    print(f"   속도: {sequential_time / multiprocessing_time:.1f}배")
    print(f"   → I/O + CPU 모두 병렬화 ✅")

    # 결과 요약
    print("\n" + "-" * 70)
    print("결과 요약 (혼합 작업):")
    print(f"  순차 실행:        {sequential_time:.2f}초")
    print(f"  Threading:        {threading_time:.2f}초 ({sequential_time/threading_time:.1f}배)")
    print(f"  Multiprocessing:  {multiprocessing_time:.2f}초 ({sequential_time/multiprocessing_time:.1f}배) ⭐")


# ============================================================
# 메모리 및 오버헤드 비교
# ============================================================

def compare_overhead():
    """각 방식의 오버헤드 비교"""
    print("\n" + "=" * 70)
    print("오버헤드 비교")
    print("=" * 70)

    def dummy_task():
        time.sleep(0.1)

    num_tasks = 100

    # Threading
    print("\n[Threading]")
    start = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(lambda _: dummy_task(), range(num_tasks)))
    threading_overhead = time.time() - start
    print(f"   100개 작업: {threading_overhead:.2f}초")

    # Multiprocessing
    print("\n[Multiprocessing]")
    start = time.time()
    with ProcessPoolExecutor(max_workers=10) as executor:
        list(executor.map(lambda _: dummy_task(), range(num_tasks)))
    multiprocessing_overhead = time.time() - start
    print(f"   100개 작업: {multiprocessing_overhead:.2f}초")
    print(f"   → Threading보다 {multiprocessing_overhead/threading_overhead:.1f}배 느림 (프로세스 생성 오버헤드)")

    print("\n" + "-" * 70)
    print("결론:")
    print("  - Threading: 가볍고 빠른 시작")
    print("  - Multiprocessing: 무겁지만 진짜 병렬 처리")
    print("  - AsyncIO: 매우 가볍고 수천 개 작업 가능 (I/O만)")


# ============================================================
# 의사결정 가이드
# ============================================================

def decision_guide():
    """어떤 방식을 선택할지 가이드"""
    print("\n" + "=" * 70)
    print("의사결정 가이드")
    print("=" * 70)
    print("""
┌─────────────────────────────────────────────────────────────┐
│                작업 종류별 최적 방식                          │
├─────────────────────────────────────────────────────────────┤
│ I/O-bound (네트워크, 파일 등)                                 │
│   ├─ 작업 100개 이상     → AsyncIO ⭐⭐⭐                     │
│   ├─ 작업 10~100개       → AsyncIO 또는 Threading            │
│   └─ 작업 10개 미만      → Threading (간단함)                │
│                                                              │
│ CPU-bound (계산, 이미지 처리 등)                              │
│   └─ 항상               → Multiprocessing ⭐⭐⭐             │
│                                                              │
│ 혼합 (I/O + CPU)                                             │
│   ├─ CPU 작업 많음      → Multiprocessing                    │
│   └─ I/O 작업 많음      → AsyncIO                           │
└─────────────────────────────────────────────────────────────┘

성능 요약:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
작업 종류    │ 순차 │ Threading │ AsyncIO │ Multiprocessing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I/O-bound    │  1x  │   3-5x    │  5-10x  │   1-2x (오버헤드)
CPU-bound    │  1x  │    1x     │   1x    │   3-4x (코어 수)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

특징 비교:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         │ Threading │  AsyncIO   │ Multiprocessing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
오버헤드  │   낮음    │  매우 낮음 │    높음
동시성    │  수십개   │  수천개    │   수십개
복잡도    │   낮음    │   중간     │    중간
GIL 영향  │   있음    │   있음     │    없음
메모리    │  공유     │   공유     │   독립
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║        Threading vs AsyncIO vs Multiprocessing           ║
║               성능 벤치마크 비교                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    try:
        # I/O-bound 벤치마크
        benchmark_io_bound()

        # CPU-bound 벤치마크
        benchmark_cpu_bound()

        # 혼합 작업 벤치마크
        benchmark_mixed()

        # 오버헤드 비교
        compare_overhead()

        # 의사결정 가이드
        decision_guide()

    except KeyboardInterrupt:
        print("\n\n벤치마크 중단")

    print("\n" + "=" * 70)
    print("벤치마크 완료! 다음은 5_real_world_examples.py를 실행해보세요.")
    print("=" * 70)
