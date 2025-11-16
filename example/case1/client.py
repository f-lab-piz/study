import argparse
import asyncio
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Tuple

import httpx


class TokenBucket:
    """단순 토큰 버킷. 초당 fill_rate 만큼 토큰이 채워지고 capacity 이상으로는 쌓이지 않는다."""

    def __init__(self, capacity: int, fill_rate: float) -> None:
        self.capacity = capacity
        self.tokens = float(capacity)
        self.fill_rate = fill_rate
        self.last_fill = time.monotonic()
        self.lock = asyncio.Lock()

    async def take(self) -> bool:
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_fill
            if elapsed > 0:
                self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
                self.last_fill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class ResultTracker:
    """API 성공/실패를 별도로 기록."""

    def __init__(self) -> None:
        self.success = 0
        self.failure = 0
        self.failed_items: list[Tuple[int, Dict[str, Any]]] = []

    def record(self, item_id: int, success: bool, detail: Dict[str, Any]) -> None:
        if success:
            self.success += 1
        else:
            self.failure += 1
            self.failed_items.append((item_id, detail))

    def report(self) -> None:
        print(f"[Result] success={self.success} failure={self.failure}")
        if self.failed_items:
            preview = ", ".join(f"id={item} detail={detail}" for item, detail in self.failed_items[:5])
            print(f"[Result] failed samples: {preview}")


class MetricsMonitor:
    """초당 처리 건수, API 요청 수, 큐 사이즈 모니터링"""

    def __init__(self) -> None:
        self.api_request_count = 0  # API 요청 횟수
        self.processed_count = 0  # 실제 처리 완료 건수
        self.lock = asyncio.Lock()

    async def record_api_request(self) -> None:
        async with self.lock:
            self.api_request_count += 1

    async def record_processed(self) -> None:
        async with self.lock:
            self.processed_count += 1

    async def get_counts(self) -> Tuple[int, int]:
        async with self.lock:
            return self.api_request_count, self.processed_count

    async def reset_counts(self) -> Tuple[int, int]:
        """현재 카운트를 반환하고 리셋"""
        async with self.lock:
            api_count = self.api_request_count
            proc_count = self.processed_count
            self.api_request_count = 0
            self.processed_count = 0
            return api_count, proc_count


def cpu_bound_work(payload: Dict[str, Any], response_data: Dict[str, Any], work_time: float) -> Dict[str, Any]:
    """CPU-bound 작업 시뮬레이션 (워커 스레드에서 실행)"""
    # CPU 집약적인 작업을 time.sleep으로 시뮬레이션
    time.sleep(work_time)

    # 작업 결과 반환
    return {
        "item_id": payload["item_id"],
        "processed": True,
        "response": response_data,
        "worker_thread": True
    }


async def send_request(
    client: httpx.AsyncClient, endpoint: str, payload: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    try:
        response = await client.post(endpoint, json=payload)
        ok = response.status_code == 200
        body = response.json() if ok else {"status_code": response.status_code, "body": response.text}
        return ok, body
    except httpx.HTTPError as exc:
        return False, {"error": str(exc)}


async def producer(
    queue: asyncio.Queue,
    bucket: TokenBucket,
    total_requests: int,
    queue_limit: int,
) -> None:
    produced = 0
    while produced < total_requests:
        if queue.qsize() >= queue_limit:
            await asyncio.sleep(0.01)
            continue

        has_token = await bucket.take()
        if not has_token:
            await asyncio.sleep(0.01)
            continue

        payload = {"item_id": produced, "payload": str(uuid.uuid4())}
        await queue.put(payload)
        produced += 1

    print(f"[Producer] queued {produced} items")


async def consumer(
    name: str,
    queue: asyncio.Queue,
    endpoint: str,
    tracker: ResultTracker,
    executor: ThreadPoolExecutor,
    metrics: MetricsMonitor,
    work_time: float,
) -> None:
    loop = asyncio.get_event_loop()
    async with httpx.AsyncClient(timeout=1.0) as client:
        while True:
            payload = await queue.get()

            # 1. API 요청 (I/O-bound, async로 처리)
            success, data = await send_request(client, endpoint, payload)
            await metrics.record_api_request()  # API 요청 카운트

            if success:
                # 2. CPU-bound 작업을 ThreadPoolExecutor에서 실행
                try:
                    processed_data = await loop.run_in_executor(
                        executor,
                        cpu_bound_work,
                        payload,
                        data,
                        work_time
                    )
                    tracker.record(payload["item_id"], True, processed_data)
                    await metrics.record_processed()  # 처리 완료 카운트
                except Exception as e:
                    tracker.record(payload["item_id"], False, {"error": str(e)})
                    print(f"[Consumer {name}] worker error id={payload['item_id']} error={e}")
            else:
                tracker.record(payload["item_id"], False, data)
                print(f"[Consumer {name}] failure id={payload['item_id']} detail={data}")

            queue.task_done()


async def monitor_stats(queue: asyncio.Queue, metrics: MetricsMonitor, stop_event: asyncio.Event) -> None:
    """1초마다 통계 출력"""
    while not stop_event.is_set():
        await asyncio.sleep(1.0)

        # 지난 1초간의 통계 수집
        api_count, proc_count = await metrics.reset_counts()
        queue_size = queue.qsize()

        print(f"[Stats] API 요청/초: {api_count:3d} | 처리완료/초: {proc_count:3d} | 큐 작업수: {queue_size:3d}")


async def main(max_workers: int, work_time: float, rate_limit: int, queue_size: int, num_consumers: int) -> None:
    endpoint = "http://127.0.0.1:8000/work"
    total_requests = 500

    queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
    bucket = TokenBucket(capacity=rate_limit, fill_rate=rate_limit)
    tracker = ResultTracker()
    metrics = MetricsMonitor()
    stop_event = asyncio.Event()

    # ThreadPoolExecutor 생성
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        print(f"[Main] 설정: 워커={max_workers}, 컨슈머={num_consumers}, 작업시간={work_time}초, API제한={rate_limit}/초, 큐크기={queue_size}")

        # 모니터링 태스크 시작
        monitor_task = asyncio.create_task(monitor_stats(queue, metrics, stop_event))

        # 컨슈머에 work_time 전달
        consumers = [
            asyncio.create_task(consumer(f"C{i}", queue, endpoint, tracker, executor, metrics, work_time))
            for i in range(num_consumers)
        ]

        await producer(queue, bucket, total_requests, queue_size)
        await queue.join()

        # 모니터 중지
        stop_event.set()
        await monitor_task

        for task in consumers:
            task.cancel()
        await asyncio.gather(*consumers, return_exceptions=True)

    tracker.report()
    print("[Main] demo finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Adaptive TPS 클라이언트 - ThreadPoolExecutor 기반 CPU-bound 작업 처리"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="ThreadPoolExecutor 워커 스레드 수 (기본값: 8)"
    )
    parser.add_argument(
        "--consumers",
        type=int,
        default=4,
        help="동시 실행할 컨슈머 수 (기본값: 4)"
    )
    parser.add_argument(
        "--work-time",
        type=float,
        default=0.2,
        help="워커에서 처리하는 작업 시간(초) (기본값: 0.2)"
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=60,
        help="초당 API 호출 제한 횟수 (기본값: 60)"
    )
    parser.add_argument(
        "--queue-size",
        type=int,
        default=200,
        help="작업 큐의 최대 크기 (기본값: 200)"
    )

    args = parser.parse_args()
    asyncio.run(main(args.workers, args.work_time, args.rate_limit, args.queue_size, args.consumers))
