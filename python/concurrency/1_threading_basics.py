"""
Threading 기초 (스레드)

I/O-bound 작업에 적합
- 파일 읽기/쓰기
- 네트워크 요청
- 데이터베이스 쿼리

JavaScript 비교:
- Web Workers보다는 가볍지만
- 단일 스레드 이벤트 루프는 아님
"""
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor


# ============================================================
# 예제 1: 기본 스레드 사용
# ============================================================

def download_file(file_id):
    """
    파일 다운로드 시뮬레이션 (I/O 작업)

    time.sleep()은 I/O 대기를 시뮬레이션
    실제로는 네트워크 요청, 파일 읽기 등
    """
    print(f"[스레드 {threading.current_thread().name}] 다운로드 시작: file_{file_id}")
    time.sleep(2)  # I/O 대기 시뮬레이션
    print(f"[스레드 {threading.current_thread().name}] 다운로드 완료: file_{file_id}")
    return f"file_{file_id}_data"


def example1_basic_threading():
    """기본 스레딩 예제"""
    print("\n" + "=" * 60)
    print("예제 1: 기본 Threading")
    print("=" * 60)

    # 순차 실행 (느림)
    print("\n[순차 실행]")
    start = time.time()
    for i in range(3):
        download_file(i)
    sequential_time = time.time() - start
    print(f"순차 실행 시간: {sequential_time:.2f}초")

    # 멀티 스레드 (빠름)
    print("\n[멀티 스레드 실행]")
    start = time.time()

    threads = []
    for i in range(3):
        # Thread 객체 생성
        thread = threading.Thread(
            target=download_file,  # 실행할 함수
            args=(i,),  # 함수 인자
            name=f"Worker-{i}"  # 스레드 이름 (디버깅용)
        )
        thread.start()  # 스레드 시작
        threads.append(thread)

    # 모든 스레드가 완료될 때까지 대기
    for thread in threads:
        thread.join()

    threaded_time = time.time() - start
    print(f"멀티 스레드 실행 시간: {threaded_time:.2f}초")
    print(f"속도 향상: {sequential_time / threaded_time:.1f}배")


# ============================================================
# 예제 2: 반환값 받기
# ============================================================

class DownloadThread(threading.Thread):
    """
    커스텀 Thread 클래스
    반환값을 받기 위해 Thread를 상속
    """

    def __init__(self, file_id):
        super().__init__()
        self.file_id = file_id
        self.result = None  # 결과 저장용

    def run(self):
        """스레드 실행 시 호출되는 메서드"""
        print(f"다운로드 시작: file_{self.file_id}")
        time.sleep(1)
        self.result = f"file_{self.file_id}_content"
        print(f"다운로드 완료: file_{self.file_id}")


def example2_thread_with_result():
    """반환값이 있는 스레딩"""
    print("\n" + "=" * 60)
    print("예제 2: 반환값 받기")
    print("=" * 60)

    threads = []
    for i in range(3):
        thread = DownloadThread(i)
        thread.start()
        threads.append(thread)

    # 모든 스레드 완료 대기
    for thread in threads:
        thread.join()

    # 결과 수집
    results = [thread.result for thread in threads]
    print(f"\n결과: {results}")


# ============================================================
# 예제 3: ThreadPoolExecutor (권장 방식!)
# ============================================================

def fetch_url(url):
    """실제 웹 요청 예시"""
    print(f"요청 시작: {url}")
    try:
        # 실제 HTTP 요청 (I/O 작업)
        # 주석 처리: 외부 API 의존성 제거
        # response = requests.get(url, timeout=5)
        # 시뮬레이션으로 대체
        time.sleep(1)
        print(f"요청 완료: {url}")
        return {"url": url, "status": 200}
    except Exception as e:
        print(f"요청 실패: {url}, 에러: {e}")
        return {"url": url, "error": str(e)}


def example3_thread_pool():
    """
    ThreadPoolExecutor 사용 (권장!)

    장점:
    - 스레드 재사용 (생성/소멸 오버헤드 감소)
    - 자동으로 join() 처리
    - 결과 반환이 쉬움 (Future 객체)
    """
    print("\n" + "=" * 60)
    print("예제 3: ThreadPoolExecutor (권장 방식)")
    print("=" * 60)

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    # ThreadPoolExecutor 사용
    # max_workers: 동시에 실행할 최대 스레드 수
    with ThreadPoolExecutor(max_workers=4) as executor:
        # map: 여러 작업을 자동으로 스레드 풀에 분배
        # results = list(executor.map(fetch_url, urls))

        # 시뮬레이션으로 대체
        print("(실제 API 호출 대신 시뮬레이션 실행)")
        time.sleep(2)
        results = [{"url": url, "status": 200} for url in urls]

    print(f"\n결과 (총 {len(results)}개):")
    for result in results:
        print(f"  - {result}")


# ============================================================
# 예제 4: 스레드 동기화 (Lock)
# ============================================================

# 공유 변수
counter = 0
counter_lock = threading.Lock()


def increment_counter_unsafe():
    """
    Race Condition 발생 가능!
    여러 스레드가 동시에 counter를 수정
    """
    global counter
    for _ in range(100_000):
        counter += 1  # 안전하지 않음!


def increment_counter_safe():
    """
    Lock을 사용한 안전한 방식
    한 번에 하나의 스레드만 실행
    """
    global counter
    for _ in range(100_000):
        with counter_lock:  # Lock 획득
            counter += 1  # 안전함!
        # with 블록 종료 시 자동으로 Lock 해제


def example4_thread_safety():
    """스레드 안전성"""
    print("\n" + "=" * 60)
    print("예제 4: 스레드 동기화 (Lock)")
    print("=" * 60)

    # 안전하지 않은 방식
    global counter
    counter = 0

    threads = [threading.Thread(target=increment_counter_unsafe) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print(f"안전하지 않은 방식: counter = {counter}")
    print(f"예상값: {4 * 100_000}, 실제값: {counter}")
    print(f"차이: {4 * 100_000 - counter} (Race Condition!)")

    # 안전한 방식
    counter = 0

    threads = [threading.Thread(target=increment_counter_safe) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print(f"\n안전한 방식 (Lock): counter = {counter}")
    print(f"예상값: {4 * 100_000}, 실제값: {counter}")
    print("정확히 일치! ✅")


# ============================================================
# JavaScript와 비교
# ============================================================

def javascript_comparison():
    """
    JavaScript와의 비교

    JavaScript (Promise.all):
    ```javascript
    const urls = ['url1', 'url2', 'url3'];
    const results = await Promise.all(
        urls.map(url => fetch(url))
    );
    ```

    Python (ThreadPoolExecutor):
    ```python
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_url, urls))
    ```

    차이점:
    - JavaScript: 싱글 스레드, 이벤트 루프
    - Python Threading: 멀티 스레드, GIL 있음
    """
    print("\n" + "=" * 60)
    print("JavaScript와 Python Threading 비교")
    print("=" * 60)
    print("""
JavaScript (Promise.all):
- 싱글 스레드 + 이벤트 루프
- 논블로킹 I/O
- async/await 문법

Python (Threading):
- 멀티 스레드
- GIL (Global Interpreter Lock)
- with ThreadPoolExecutor 패턴

공통점:
- 둘 다 I/O-bound 작업에 적합
- 동시성 (Concurrency) 제공
    """)


# ============================================================
# 실습 문제
# ============================================================

def exercise():
    """
    실습: ThreadPoolExecutor로 여러 파일 다운로드

    TODO: 아래 코드를 완성하세요!
    """
    print("\n" + "=" * 60)
    print("실습 문제")
    print("=" * 60)

    def download_and_process(file_id):
        """
        파일 다운로드 + 처리

        TODO: 이 함수를 완성하세요
        1. 다운로드 시뮬레이션 (time.sleep 1초)
        2. 처리 시뮬레이션 (time.sleep 0.5초)
        3. 결과 반환: {"id": file_id, "size": random한 크기}
        """
        import random

        # 여기에 코드 작성
        print(f"다운로드 시작: file_{file_id}")
        time.sleep(1)
        print(f"처리 시작: file_{file_id}")
        time.sleep(0.5)

        return {
            "id": file_id,
            "size": random.randint(100, 1000)
        }

    # TODO: ThreadPoolExecutor로 10개 파일 동시 다운로드
    # 힌트: with ThreadPoolExecutor(max_workers=5) as executor:
    file_ids = range(10)

    start = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(download_and_process, file_ids))

    elapsed = time.time() - start

    print(f"\n다운로드 완료! 총 {len(results)}개 파일")
    print(f"소요 시간: {elapsed:.2f}초")
    print(f"총 크기: {sum(r['size'] for r in results)} bytes")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║          Python Threading 기초 학습                       ║
║                                                          ║
║  I/O-bound 작업에 적합 (파일, 네트워크 등)                ║
║  GIL 때문에 CPU-bound 작업에는 효과 없음                  ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 모든 예제 실행
    example1_basic_threading()
    example2_thread_with_result()
    example3_thread_pool()
    example4_thread_safety()
    javascript_comparison()

    # 실습 문제
    exercise()

    print("\n" + "=" * 60)
    print("학습 완료! 다음은 2_multiprocessing_basics.py를 실행해보세요.")
    print("=" * 60)
