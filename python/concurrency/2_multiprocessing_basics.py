"""
Multiprocessing 기초 (멀티프로세싱)

CPU-bound 작업에 적합
- 복잡한 계산
- 이미지/비디오 처리
- 데이터 분석
- 머신러닝

JavaScript 비교:
- Node.js의 Worker Threads와 유사
- 하지만 프로세스 (더 무거움)
- GIL을 우회하여 진정한 병렬 처리
"""
import multiprocessing
import time
import os
from concurrent.futures import ProcessPoolExecutor


# ============================================================
# 예제 1: Threading vs Multiprocessing 성능 비교
# ============================================================

def cpu_heavy_task(n):
    """
    CPU 집약적 작업
    복잡한 계산 시뮬레이션
    """
    result = 0
    for i in range(n):
        result += i ** 2
    return result


def example1_performance_comparison():
    """GIL의 영향 확인"""
    print("\n" + "=" * 60)
    print("예제 1: Threading vs Multiprocessing 성능 비교")
    print("=" * 60)

    n = 5_000_000
    num_tasks = 4

    # 1. 순차 실행
    print("\n[순차 실행]")
    start = time.time()
    results = [cpu_heavy_task(n) for _ in range(num_tasks)]
    sequential_time = time.time() - start
    print(f"순차 실행 시간: {sequential_time:.2f}초")

    # 2. Threading (GIL 때문에 느림!)
    print("\n[Threading 실행]")
    import threading

    start = time.time()
    threads = []
    for _ in range(num_tasks):
        thread = threading.Thread(target=cpu_heavy_task, args=(n,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    threading_time = time.time() - start
    print(f"Threading 실행 시간: {threading_time:.2f}초")
    print(f"순차 대비 속도: {sequential_time / threading_time:.2f}배")
    print("→ GIL 때문에 거의 빨라지지 않음! ❌")

    # 3. Multiprocessing (빠름!)
    print("\n[Multiprocessing 실행]")
    start = time.time()

    with ProcessPoolExecutor(max_workers=num_tasks) as executor:
        results = list(executor.map(cpu_heavy_task, [n] * num_tasks))

    multiprocessing_time = time.time() - start
    print(f"Multiprocessing 실행 시간: {multiprocessing_time:.2f}초")
    print(f"순차 대비 속도: {sequential_time / multiprocessing_time:.2f}배")
    print(f"→ GIL 우회로 실제 병렬 처리! ✅")


# ============================================================
# 예제 2: 기본 Process 사용
# ============================================================

def worker_function(worker_id, delay):
    """
    워커 프로세스가 실행할 함수

    각 프로세스는 독립적인 메모리 공간을 가짐
    """
    print(f"[프로세스 {worker_id}] PID: {os.getpid()}, 부모 PID: {os.getppid()}")
    print(f"[프로세스 {worker_id}] 작업 시작")
    time.sleep(delay)
    print(f"[프로세스 {worker_id}] 작업 완료")
    return f"결과_{worker_id}"


def example2_basic_process():
    """기본 Process 사용법"""
    print("\n" + "=" * 60)
    print("예제 2: 기본 Process 사용")
    print("=" * 60)

    print(f"메인 프로세스 PID: {os.getpid()}\n")

    processes = []
    for i in range(3):
        # Process 객체 생성
        process = multiprocessing.Process(
            target=worker_function,
            args=(i, 1),  # worker_id, delay
            name=f"Worker-{i}"
        )
        process.start()
        processes.append(process)

    # 모든 프로세스 완료 대기
    for process in processes:
        process.join()

    print("\n모든 프로세스 완료!")


# ============================================================
# 예제 3: ProcessPoolExecutor (권장 방식!)
# ============================================================

def process_image(image_id):
    """
    이미지 처리 시뮬레이션 (CPU 집약적)

    실제로는:
    - 이미지 리사이징
    - 필터 적용
    - 포맷 변환 등
    """
    print(f"이미지 {image_id} 처리 시작 (PID: {os.getpid()})")

    # CPU 집약적 작업 시뮬레이션
    result = 0
    for i in range(2_000_000):
        result += i ** 2

    print(f"이미지 {image_id} 처리 완료")
    return {"image_id": image_id, "processed": True, "size": result % 1000}


def example3_process_pool():
    """
    ProcessPoolExecutor 사용 (권장!)

    장점:
    - 프로세스 재사용
    - 자동 join()
    - 결과 반환 쉬움
    """
    print("\n" + "=" * 60)
    print("예제 3: ProcessPoolExecutor (권장)")
    print("=" * 60)

    image_ids = range(8)

    # CPU 코어 수 확인
    cpu_count = multiprocessing.cpu_count()
    print(f"사용 가능한 CPU 코어: {cpu_count}개\n")

    start = time.time()

    # ProcessPoolExecutor 사용
    # max_workers를 None으로 설정하면 CPU 코어 수만큼 사용
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        results = list(executor.map(process_image, image_ids))

    elapsed = time.time() - start

    print(f"\n처리 완료! 총 {len(results)}개 이미지")
    print(f"소요 시간: {elapsed:.2f}초")
    print(f"결과: {results[:3]}...")  # 처음 3개만 출력


# ============================================================
# 예제 4: 프로세스 간 데이터 공유
# ============================================================

def increment_shared_value(shared_value, lock, worker_id):
    """
    공유 메모리 사용

    multiprocessing.Value: 프로세스 간 공유되는 값
    multiprocessing.Lock: 동기화
    """
    for _ in range(100_000):
        with lock:
            shared_value.value += 1

    print(f"워커 {worker_id} 완료")


def example4_shared_memory():
    """프로세스 간 데이터 공유"""
    print("\n" + "=" * 60)
    print("예제 4: 프로세스 간 데이터 공유")
    print("=" * 60)

    # 공유 변수 생성
    # 'i': integer 타입
    shared_value = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()

    processes = []
    for i in range(4):
        process = multiprocessing.Process(
            target=increment_shared_value,
            args=(shared_value, lock, i)
        )
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    print(f"\n최종 값: {shared_value.value}")
    print(f"예상 값: {4 * 100_000}")
    print("Lock으로 동기화되어 정확히 일치! ✅")


# ============================================================
# 예제 5: Queue를 사용한 작업 분배
# ============================================================

def worker_with_queue(task_queue, result_queue, worker_id):
    """
    Queue를 사용한 작업-결과 패턴

    task_queue: 작업을 받아옴
    result_queue: 결과를 전달
    """
    print(f"[워커 {worker_id}] 시작")

    while True:
        try:
            # 작업 가져오기 (타임아웃 1초)
            task = task_queue.get(timeout=1)

            if task is None:  # 종료 신호
                print(f"[워커 {worker_id}] 종료")
                break

            # 작업 처리
            print(f"[워커 {worker_id}] 작업 처리: {task}")
            result = task ** 2
            time.sleep(0.5)

            # 결과 전달
            result_queue.put((task, result))

        except:
            break


def example5_queue_pattern():
    """Queue를 사용한 Producer-Consumer 패턴"""
    print("\n" + "=" * 60)
    print("예제 5: Queue를 사용한 작업 분배")
    print("=" * 60)

    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    # 작업 추가 (Producer)
    tasks = range(10)
    for task in tasks:
        task_queue.put(task)

    # 워커 프로세스 시작 (Consumer)
    num_workers = 3
    processes = []

    for i in range(num_workers):
        process = multiprocessing.Process(
            target=worker_with_queue,
            args=(task_queue, result_queue, i)
        )
        process.start()
        processes.append(process)

    # 종료 신호 전송
    for _ in range(num_workers):
        task_queue.put(None)

    # 결과 수집
    results = []
    for _ in tasks:
        results.append(result_queue.get())

    # 프로세스 종료 대기
    for process in processes:
        process.join()

    print(f"\n결과: {sorted(results)}")


# ============================================================
# JavaScript와 비교
# ============================================================

def javascript_comparison():
    """
    JavaScript Worker Threads와 비교

    JavaScript (Worker Threads):
    ```javascript
    const { Worker } = require('worker_threads');

    const worker = new Worker('./worker.js', {
        workerData: { task: 'heavy_computation' }
    });

    worker.on('message', (result) => {
        console.log(result);
    });
    ```

    Python (Multiprocessing):
    ```python
    from multiprocessing import Process

    def worker(task):
        # CPU 집약적 작업
        pass

    process = Process(target=worker, args=('heavy_computation',))
    process.start()
    process.join()
    ```

    차이점:
    - JavaScript: 스레드 (가벼움)
    - Python: 프로세스 (무거움, 독립 메모리)
    """
    print("\n" + "=" * 60)
    print("JavaScript Worker Threads vs Python Multiprocessing")
    print("=" * 60)
    print("""
JavaScript (Worker Threads):
- 스레드 기반 (가벼움)
- 메모리 공유 (SharedArrayBuffer)
- 메시지 전달 (postMessage)

Python (Multiprocessing):
- 프로세스 기반 (무거움)
- 독립 메모리 공간
- Queue, Pipe로 통신

공통점:
- 둘 다 CPU-bound 작업에 적합
- 병렬 처리 (Parallelism)
- GIL/싱글 스레드 제약 우회
    """)


# ============================================================
# 실습 문제
# ============================================================

def exercise():
    """
    실습: ProcessPoolExecutor로 대량 데이터 처리

    시나리오: 100만 개의 숫자의 소수(prime) 여부 확인
    """
    print("\n" + "=" * 60)
    print("실습 문제: 소수(Prime) 찾기")
    print("=" * 60)

    def is_prime(n):
        """
        소수 판별 (CPU 집약적)

        TODO: 이 함수를 완성하세요
        """
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    # 테스트할 숫자 범위
    numbers = range(100_000, 101_000)  # 1000개

    print(f"\n{len(numbers)}개 숫자의 소수 여부 확인\n")

    # 순차 실행
    print("[순차 실행]")
    start = time.time()
    primes_sequential = [n for n in numbers if is_prime(n)]
    sequential_time = time.time() - start
    print(f"소수 개수: {len(primes_sequential)}")
    print(f"소요 시간: {sequential_time:.2f}초")

    # TODO: ProcessPoolExecutor로 병렬 처리
    # 힌트: executor.map(is_prime, numbers)
    print("\n[병렬 실행]")
    start = time.time()

    with ProcessPoolExecutor() as executor:
        # map 결과는 이터레이터이므로 list로 변환하며 필터링
        results = executor.map(is_prime, numbers)
        primes_parallel = [n for n, is_p in zip(numbers, results) if is_p]

    parallel_time = time.time() - start
    print(f"소수 개수: {len(primes_parallel)}")
    print(f"소요 시간: {parallel_time:.2f}초")
    print(f"속도 향상: {sequential_time / parallel_time:.1f}배 ✅")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║        Python Multiprocessing 기초 학습                   ║
║                                                          ║
║  CPU-bound 작업에 적합 (계산, 이미지 처리 등)              ║
║  GIL 우회로 진정한 병렬 처리 가능                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 모든 예제 실행
    example1_performance_comparison()
    example2_basic_process()
    example3_process_pool()
    example4_shared_memory()
    example5_queue_pattern()
    javascript_comparison()

    # 실습 문제
    exercise()

    print("\n" + "=" * 60)
    print("학습 완료! 다음은 3_asyncio_basics.py를 실행해보세요.")
    print("=" * 60)
