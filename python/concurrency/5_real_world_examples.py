"""
실전 예제 (Real-World Examples)

실제 프로젝트에서 자주 사용하는 동시성 패턴
"""
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict
import json


# ============================================================
# 예제 1: 웹 스크래핑 (AsyncIO)
# ============================================================

async def scrape_github_user(session: aiohttp.ClientSession, username: str) -> Dict:
    """
    GitHub 사용자 정보 스크래핑

    실전 시나리오:
    - 수백 개의 사용자 정보 수집
    - API Rate Limit 고려
    - 에러 처리
    """
    url = f"https://api.github.com/users/{username}"

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "username": username,
                    "name": data.get("name"),
                    "repos": data.get("public_repos"),
                    "followers": data.get("followers"),
                    "success": True
                }
            else:
                return {"username": username, "error": f"Status {response.status}", "success": False}

    except asyncio.TimeoutError:
        return {"username": username, "error": "Timeout", "success": False}
    except Exception as e:
        return {"username": username, "error": str(e), "success": False}


async def example1_web_scraping():
    """웹 스크래핑 예제"""
    print("\n" + "=" * 70)
    print("예제 1: 웹 스크래핑 (AsyncIO)")
    print("=" * 70)

    # 유명 GitHub 사용자들
    usernames = [
        "torvalds", "gvanrossum", "tj", "addyosmani", "paulirish",
        "sindresorhus", "yyx990803", "taylorotwell", "fabpot", "dhh"
    ]

    print(f"\n{len(usernames)}명의 GitHub 사용자 정보 수집 중...\n")

    start = time.time()

    # Semaphore로 동시 요청 수 제한 (GitHub API Rate Limit 고려)
    semaphore = asyncio.Semaphore(5)

    async def fetch_with_limit(session, username):
        async with semaphore:
            return await scrape_github_user(session, username)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_limit(session, username) for username in usernames]
        results = await asyncio.gather(*tasks)

    elapsed = time.time() - start

    # 결과 출력
    success_count = sum(1 for r in results if r.get("success"))
    print(f"성공: {success_count}/{len(results)}명")
    print(f"소요 시간: {elapsed:.2f}초")

    print("\n상위 5명 (팔로워 기준):")
    successful_results = [r for r in results if r.get("success")]
    sorted_users = sorted(successful_results, key=lambda x: x.get("followers", 0), reverse=True)

    for user in sorted_users[:5]:
        print(f"  {user['username']:15} - {user['followers']:,} followers, {user['repos']} repos")


# ============================================================
# 예제 2: 파일 병렬 처리 (Multiprocessing)
# ============================================================

def process_log_file(file_data: tuple) -> Dict:
    """
    로그 파일 처리 (CPU 집약적)

    실전 시나리오:
    - 대용량 로그 파일 분석
    - 에러 카운팅, 통계 계산
    - 패턴 매칭
    """
    file_id, lines = file_data

    stats = {
        "file_id": file_id,
        "total_lines": len(lines),
        "errors": 0,
        "warnings": 0,
        "info": 0
    }

    # 로그 레벨 카운팅
    for line in lines:
        if "ERROR" in line:
            stats["errors"] += 1
        elif "WARN" in line:
            stats["warnings"] += 1
        elif "INFO" in line:
            stats["info"] += 1

    return stats


def example2_parallel_file_processing():
    """파일 병렬 처리 예제"""
    print("\n" + "=" * 70)
    print("예제 2: 로그 파일 병렬 처리 (Multiprocessing)")
    print("=" * 70)

    # 가상의 로그 파일 데이터 생성
    import random

    def generate_log_lines(n):
        levels = ["INFO", "WARN", "ERROR"]
        return [f"[{random.choice(levels)}] Log message {i}" for i in range(n)]

    # 10개의 로그 파일 (각 100,000 라인)
    log_files = [(i, generate_log_lines(100_000)) for i in range(10)]

    print(f"\n{len(log_files)}개 로그 파일 분석 중 (각 100,000 라인)...\n")

    # 순차 처리
    print("[순차 처리]")
    start = time.time()
    results_seq = [process_log_file(f) for f in log_files]
    sequential_time = time.time() - start
    print(f"소요 시간: {sequential_time:.2f}초")

    # 병렬 처리
    print("\n[병렬 처리]")
    start = time.time()
    with ProcessPoolExecutor() as executor:
        results_par = list(executor.map(process_log_file, log_files))
    parallel_time = time.time() - start
    print(f"소요 시간: {parallel_time:.2f}초")
    print(f"속도 향상: {sequential_time / parallel_time:.1f}배 ⚡")

    # 통계 집계
    total_stats = {
        "total_lines": sum(r["total_lines"] for r in results_par),
        "errors": sum(r["errors"] for r in results_par),
        "warnings": sum(r["warnings"] for r in results_par),
        "info": sum(r["info"] for r in results_par)
    }

    print(f"\n전체 통계:")
    print(f"  총 라인: {total_stats['total_lines']:,}")
    print(f"  에러: {total_stats['errors']:,}")
    print(f"  경고: {total_stats['warnings']:,}")
    print(f"  정보: {total_stats['info']:,}")


# ============================================================
# 예제 3: API 여러 개 동시 호출 (AsyncIO)
# ============================================================

async def fetch_weather(session: aiohttp.ClientSession, city: str) -> Dict:
    """날씨 API 호출 (시뮬레이션)"""
    # 실제로는 OpenWeatherMap 등의 API 사용
    await asyncio.sleep(0.5)  # API 호출 시뮬레이션
    return {
        "city": city,
        "temperature": 20 + hash(city) % 15,  # 가상 온도
        "condition": "sunny"
    }


async def fetch_news(session: aiohttp.ClientSession, city: str) -> Dict:
    """뉴스 API 호출 (시뮬레이션)"""
    await asyncio.sleep(0.3)
    return {
        "city": city,
        "news_count": 10 + hash(city) % 20
    }


async def fetch_traffic(session: aiohttp.ClientSession, city: str) -> Dict:
    """교통 정보 API 호출 (시뮬레이션)"""
    await asyncio.sleep(0.4)
    return {
        "city": city,
        "traffic_level": ["low", "medium", "high"][hash(city) % 3]
    }


async def example3_multiple_apis():
    """여러 API 동시 호출"""
    print("\n" + "=" * 70)
    print("예제 3: 도시별 정보 수집 (여러 API 동시 호출)")
    print("=" * 70)

    cities = ["Seoul", "Tokyo", "New York", "London", "Paris"]

    print(f"\n{len(cities)}개 도시의 날씨/뉴스/교통 정보 수집 중...\n")

    async with aiohttp.ClientSession() as session:
        start = time.time()

        # 각 도시마다 3개 API 동시 호출
        tasks = []
        for city in cities:
            # 도시별로 3개 API를 그룹화
            city_tasks = asyncio.gather(
                fetch_weather(session, city),
                fetch_news(session, city),
                fetch_traffic(session, city)
            )
            tasks.append(city_tasks)

        # 모든 도시 정보 동시 수집
        results = await asyncio.gather(*tasks)

        elapsed = time.time() - start

    print(f"소요 시간: {elapsed:.2f}초")
    print("(순차 실행 예상 시간: ~{:.1f}초)\n".format(len(cities) * 1.2))

    # 결과 출력
    for i, city in enumerate(cities):
        weather, news, traffic = results[i]
        print(f"{city}:")
        print(f"  날씨: {weather['temperature']}°C, {weather['condition']}")
        print(f"  뉴스: {news['news_count']}건")
        print(f"  교통: {traffic['traffic_level']}")


# ============================================================
# 예제 4: 데이터베이스 쿼리 병렬화 (Threading)
# ============================================================

def execute_query(query_info: tuple) -> Dict:
    """
    DB 쿼리 실행 시뮬레이션

    실전에서는:
    - SQLAlchemy 세션 사용
    - Connection Pool 활용
    - 트랜잭션 처리
    """
    query_id, query, delay = query_info

    print(f"  [쿼리 {query_id}] 실행 중: {query}")
    time.sleep(delay)  # DB I/O 대기 시뮬레이션

    return {
        "query_id": query_id,
        "query": query,
        "rows": 100 + query_id * 10,
        "execution_time": delay
    }


def example4_database_queries():
    """데이터베이스 쿼리 병렬화"""
    print("\n" + "=" * 70)
    print("예제 4: 데이터베이스 쿼리 병렬화 (Threading)")
    print("=" * 70)

    # 여러 개의 독립적인 쿼리
    queries = [
        (1, "SELECT * FROM users WHERE active = true", 1.0),
        (2, "SELECT * FROM orders WHERE status = 'pending'", 1.5),
        (3, "SELECT * FROM products WHERE stock > 0", 0.8),
        (4, "SELECT * FROM payments WHERE date > '2024-01-01'", 1.2),
        (5, "SELECT * FROM reviews WHERE rating >= 4", 0.9)
    ]

    print(f"\n{len(queries)}개의 쿼리 실행\n")

    # 순차 실행
    print("[순차 실행]")
    start = time.time()
    results_seq = [execute_query(q) for q in queries]
    sequential_time = time.time() - start
    print(f"소요 시간: {sequential_time:.2f}초")

    # 병렬 실행 (Threading)
    print("\n[병렬 실행 (Threading)]")
    start = time.time()
    with ThreadPoolExecutor(max_workers=3) as executor:
        results_par = list(executor.map(execute_query, queries))
    parallel_time = time.time() - start
    print(f"소요 시간: {parallel_time:.2f}초")
    print(f"속도 향상: {sequential_time / parallel_time:.1f}배 ⚡")

    # 결과 요약
    total_rows = sum(r["rows"] for r in results_par)
    print(f"\n총 조회 행: {total_rows:,}개")


# ============================================================
# 예제 5: 이미지 배치 처리 (Multiprocessing)
# ============================================================

def resize_image_simulation(image_id: int) -> Dict:
    """
    이미지 리사이징 시뮬레이션

    실전에서는:
    - PIL/Pillow 사용
    - 썸네일 생성
    - 워터마크 추가
    - 포맷 변환
    """
    # CPU 집약적 작업 시뮬레이션
    result = 0
    for i in range(2_000_000):
        result += i ** 2

    return {
        "image_id": image_id,
        "original_size": (1920, 1080),
        "resized_size": (800, 600),
        "processing_time": 0.5
    }


def example5_image_processing():
    """이미지 배치 처리"""
    print("\n" + "=" * 70)
    print("예제 5: 이미지 배치 처리 (Multiprocessing)")
    print("=" * 70)

    image_ids = range(12)  # 12개 이미지

    print(f"\n{len(image_ids)}개 이미지 리사이징 중...\n")

    # 순차 처리
    print("[순차 처리]")
    start = time.time()
    results_seq = [resize_image_simulation(img_id) for img_id in image_ids]
    sequential_time = time.time() - start
    print(f"소요 시간: {sequential_time:.2f}초")

    # 병렬 처리
    print("\n[병렬 처리 (Multiprocessing)]")
    start = time.time()
    with ProcessPoolExecutor() as executor:
        results_par = list(executor.map(resize_image_simulation, image_ids))
    parallel_time = time.time() - start
    print(f"소요 시간: {parallel_time:.2f}초")
    print(f"속도 향상: {sequential_time / parallel_time:.1f}배 ⚡")

    print(f"\n처리 완료: {len(results_par)}개 이미지")


# ============================================================
# 실전 팁 & 베스트 프랙티스
# ============================================================

def best_practices():
    """실전 팁"""
    print("\n" + "=" * 70)
    print("실전 팁 & 베스트 프랙티스")
    print("=" * 70)
    print("""
1. AsyncIO 사용 시:
   ✅ async/await 전용 라이브러리 사용 (aiohttp, asyncpg 등)
   ✅ Semaphore로 동시 연결 수 제한
   ✅ 타임아웃 설정 (asyncio.wait_for)
   ✅ 에러 처리 (return_exceptions=True)
   ❌ 블로킹 함수 호출 금지 (time.sleep, requests 등)

2. Multiprocessing 사용 시:
   ✅ ProcessPoolExecutor 사용 (권장)
   ✅ CPU 코어 수 고려 (multiprocessing.cpu_count())
   ✅ 직렬화 가능한 데이터만 전달
   ❌ 너무 많은 프로세스 생성 금지 (오버헤드)

3. Threading 사용 시:
   ✅ ThreadPoolExecutor 사용 (권장)
   ✅ Lock으로 공유 자원 보호
   ✅ I/O-bound 작업에만 사용
   ❌ CPU-bound 작업에 사용 금지 (GIL)

4. 일반적인 팁:
   ✅ 벤치마크로 성능 측정 후 선택
   ✅ 프로파일링으로 병목 지점 파악
   ✅ 에러 처리 철저히
   ✅ 리소스 정리 (context manager 사용)

5. 실전 시나리오별 추천:
   - 웹 스크래핑 (100+ URLs)     → AsyncIO
   - API 여러 개 호출              → AsyncIO
   - 대용량 파일 처리              → Multiprocessing
   - 이미지/비디오 처리            → Multiprocessing
   - DB 쿼리 병렬화               → Threading or AsyncIO
   - 데이터 분석                   → Multiprocessing
    """)


# ============================================================
# 메인 실행
# ============================================================

async def main():
    """모든 예제 실행"""
    print("""
╔══════════════════════════════════════════════════════════╗
║              Python 동시성 실전 예제                      ║
║                                                          ║
║  실제 프로젝트에서 자주 사용하는 패턴                      ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 예제 1: 웹 스크래핑
    await example1_web_scraping()

    # 예제 2: 파일 병렬 처리
    example2_parallel_file_processing()

    # 예제 3: 여러 API 동시 호출
    await example3_multiple_apis()

    # 예제 4: DB 쿼리 병렬화
    example4_database_queries()

    # 예제 5: 이미지 배치 처리
    example5_image_processing()

    # 베스트 프랙티스
    best_practices()

    print("\n" + "=" * 70)
    print("모든 예제 완료! 🎉")
    print("=" * 70)
    print("""
다음 단계:
1. 자신의 프로젝트에 적용해보기
2. 성능 측정 및 최적화
3. AsyncIO + FastAPI로 고성능 API 서버 만들기
4. Celery를 사용한 비동기 작업 큐 학습
    """)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n프로그램 종료")
