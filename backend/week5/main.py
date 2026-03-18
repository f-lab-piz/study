"""
5주차 실행 예제
- 상태 관리
- 멱등성
- MVP 설계

실행:
uv run python main.py
"""

from __future__ import annotations


def print_section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show_state_management() -> None:
    print_section("1. 상태 관리 예제")

    allowed_transitions = {
        "requested": {"allocated", "failed"},
        "allocated": {"in_progress", "failed"},
        "in_progress": {"completed", "failed"},
        "completed": set(),
        "failed": set(),
    }

    current_status = "requested"
    print(f"현재 상태: {current_status}")

    next_status = "allocated"
    if next_status in allowed_transitions[current_status]:
        current_status = next_status
        print(f"정상 전이: requested -> {current_status}")

    next_status = "in_progress"
    if next_status in allowed_transitions[current_status]:
        current_status = next_status
        print(f"정상 전이: allocated -> {current_status}")

    next_status = "completed"
    if next_status in allowed_transitions[current_status]:
        current_status = next_status
        print(f"정상 전이: in_progress -> {current_status}")

    invalid_next_status = "requested"
    print(f"잘못된 전이 시도: {current_status} -> {invalid_next_status}")
    if invalid_next_status not in allowed_transitions[current_status]:
        print("차단: completed 상태는 다시 requested 로 되돌릴 수 없음")


def show_idempotency() -> None:
    print_section("2. 멱등성 예제")

    processed_requests: dict[str, dict[str, str | int]] = {}

    def create_picking_task(idempotency_key: str, outbound_request_id: int) -> dict[str, str | int]:
        if idempotency_key in processed_requests:
            print(f"중복 요청 감지: {idempotency_key}")
            return processed_requests[idempotency_key]

        task = {
            "task_id": len(processed_requests) + 1,
            "outbound_request_id": outbound_request_id,
            "status": "ready",
        }
        processed_requests[idempotency_key] = task
        print(f"새 작업지시 생성: {task}")
        return task

    first = create_picking_task("req-1001", 101)
    second = create_picking_task("req-1001", 101)

    print(f"첫 번째 응답: {first}")
    print(f"두 번째 응답: {second}")
    print("결과: 같은 요청 키로 두 번 호출해도 작업지시는 하나만 유지됨")


def show_mvp_design() -> None:
    print_section("3. MVP 설계 예제")

    service_line = (
        "창고 담당자가 출고 요청을 등록하고 재고를 확인한 뒤 "
        "피킹 작업을 진행할 수 있는 시스템"
    )
    included = [
        "상품 조회",
        "재고 조회",
        "출고 요청 생성",
        "작업지시 생성",
        "작업 상태 변경",
    ]
    excluded = [
        "로그인/권한관리",
        "멀티 창고",
        "알림 자동화",
        "대시보드",
        "AI 자동 실행",
    ]
    first_apis = [
        "GET /products",
        "GET /inventory",
        "POST /outbound-requests",
        "POST /picking-tasks",
        "PATCH /picking-tasks/{id}/status",
    ]

    print("서비스 한 줄:")
    print(f"- {service_line}")

    print("\nMVP에 넣을 것:")
    for item in included:
        print(f"- {item}")

    print("\nMVP에서 뺄 것:")
    for item in excluded:
        print(f"- {item}")

    print("\n처음 열 API:")
    for item in first_apis:
        print(f"- {item}")

    print("\n핵심 메시지:")
    print("- 처음부터 모든 기능을 만들지 않는다")
    print("- 핵심 흐름 하나가 끝까지 도는지 먼저 확인한다")


def main() -> None:
    print("5주차 실행 예제")
    print("주제: 상태 관리 -> 멱등성 -> MVP 설계")

    show_state_management()
    show_idempotency()
    show_mvp_design()


if __name__ == "__main__":
    main()
