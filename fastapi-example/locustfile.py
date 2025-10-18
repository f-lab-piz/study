"""
Locust 성능 테스트 시나리오

Locust란?
- Python 기반 부하 테스트 도구
- 사용자 행동을 시뮬레이션하여 시스템 성능 측정
- 웹 UI 제공으로 실시간 모니터링 가능

실행 방법:
1. docker-compose exec fastapi-app locust
2. 브라우저에서 http://localhost:8089 접속
3. 테스트 설정 입력 (사용자 수, 증가율 등)
4. 테스트 시작 및 결과 확인
"""
from locust import HttpUser, task, between
import random


class TodoUser(HttpUser):
    """
    TODO 애플리케이션 사용자 시뮬레이션

    HttpUser:
    - Locust의 기본 사용자 클래스
    - HTTP 요청을 보내는 가상 사용자를 정의
    """

    # 각 태스크 실행 사이 대기 시간 (초)
    # 실제 사용자처럼 1~3초 대기
    wait_time = between(1, 3)

    # 생성된 TODO의 ID를 저장 (나중에 조회/수정/삭제에 사용)
    created_todo_ids = []

    def on_start(self):
        """
        각 사용자 시작 시 한 번만 실행

        용도:
        - 로그인 시뮬레이션
        - 초기 데이터 설정
        - 테스트 환경 준비
        """
        # 헬스 체크로 서버 연결 확인
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"서버 헬스체크 실패: {response.status_code}")

    @task(3)
    def create_todo(self):
        """
        TODO 생성 시나리오

        @task(3):
        - 이 태스크의 실행 빈도 (가중치)
        - 3:1:1 비율로 실행됨 (생성:조회:수정)
        - 실제 사용 패턴과 유사하게 설정

        성능 측정:
        - 응답 시간
        - 처리량 (TPS: Transactions Per Second)
        - 에러율
        """
        # 랜덤 데이터로 TODO 생성 (실제 사용자처럼)
        todo_data = {
            "title": f"성능 테스트 TODO {random.randint(1, 10000)}",
            "description": f"Locust로 생성된 테스트 데이터 {random.randint(1, 10000)}",
            "completed": random.choice([True, False])
        }

        # name: Locust UI에 표시될 이름 (그룹화)
        with self.client.post(
            "/todos/",
            json=todo_data,
            name="/todos/ [POST - Create]",
            catch_response=True
        ) as response:
            if response.status_code == 201:
                # 생성 성공
                todo_id = response.json().get("id")
                if todo_id:
                    self.created_todo_ids.append(todo_id)
                response.success()
            else:
                # 생성 실패 (에러로 기록)
                response.failure(f"TODO 생성 실패: {response.status_code}")

    @task(2)
    def list_todos(self):
        """
        TODO 리스트 조회 시나리오

        @task(2): 가중치 2
        - 생성보다는 덜 자주 실행

        성능 포인트:
        - 페이지네이션 성능
        - DB 쿼리 최적화
        - 대량 데이터 조회 성능
        """
        # 랜덤 페이지네이션 파라미터
        skip = random.randint(0, 100)
        limit = random.choice([10, 20, 50, 100])

        with self.client.get(
            f"/todos/?skip={skip}&limit={limit}",
            name="/todos/ [GET - List]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                todos = response.json()
                if isinstance(todos, list):
                    response.success()
                else:
                    response.failure("응답이 리스트가 아님")
            else:
                response.failure(f"리스트 조회 실패: {response.status_code}")

    @task(1)
    def get_single_todo(self):
        """
        특정 TODO 조회 시나리오

        @task(1): 가중치 1
        - 가장 낮은 빈도

        조건:
        - created_todo_ids에 TODO가 있을 때만 실행
        """
        if not self.created_todo_ids:
            # 아직 생성된 TODO가 없으면 스킵
            return

        # 랜덤하게 하나 선택
        todo_id = random.choice(self.created_todo_ids)

        with self.client.get(
            f"/todos/{todo_id}",
            name="/todos/{id} [GET - Detail]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # 404는 에러가 아님 (이미 삭제된 TODO일 수 있음)
                response.success()
            else:
                response.failure(f"TODO 조회 실패: {response.status_code}")

    @task(1)
    def update_todo(self):
        """
        TODO 수정 시나리오

        TODO: 이 메서드를 완성해보세요!

        힌트:
        1. created_todo_ids에서 랜덤하게 하나 선택
        2. PUT /todos/{id} 요청
        3. 업데이트 데이터: title, description, completed 중 일부 또는 전체
        4. catch_response=True로 성공/실패 처리
        5. 404는 성공으로 처리 (이미 삭제된 TODO)
        """
        if not self.created_todo_ids:
            return

        todo_id = random.choice(self.created_todo_ids)

        # TODO: 업데이트 데이터 작성
        update_data = {
            # 여기에 업데이트할 데이터 작성
        }

        # TODO: PUT 요청 작성
        pass

    @task(1)
    def delete_todo(self):
        """
        TODO 삭제 시나리오

        TODO: 이 메서드를 완성해보세요!

        힌트:
        1. created_todo_ids에서 랜덤하게 하나 선택
        2. DELETE /todos/{id} 요청
        3. 204 응답이 성공
        4. 삭제 후 created_todo_ids에서 제거
        5. 404도 성공으로 처리
        """
        pass


# 추가 시나리오 예시
class MixedWorkloadUser(HttpUser):
    """
    TODO: 복잡한 워크플로우 시나리오

    실제 사용자의 행동 패턴을 시뮬레이션:
    1. TODO 여러 개 생성
    2. 리스트 조회하여 확인
    3. 일부 TODO 완료 처리
    4. 완료된 TODO 삭제

    힌트:
    - @task 대신 일반 메서드로 작성
    - 하나의 @task에서 여러 단계 실행
    """
    wait_time = between(2, 5)

    @task
    def complete_workflow(self):
        """
        TODO: 전체 워크플로우를 하나의 태스크로 작성

        예시 흐름:
        1. TODO 3개 생성
        2. 전체 리스트 조회
        3. 첫 번째 TODO 완료 처리
        4. 완료된 TODO 삭제
        """
        pass


class StressTestUser(HttpUser):
    """
    TODO: 스트레스 테스트 시나리오

    시스템의 한계를 테스트:
    - wait_time을 최소화 (연속 요청)
    - 대량 데이터 생성
    - 긴 description (대용량 페이로드)

    힌트:
    - wait_time = between(0.1, 0.5)
    - description에 긴 텍스트 (1000자 이상)
    """
    pass


# Locust 설정 팁

"""
성능 테스트 시나리오별 설정:

1. 부하 테스트 (Load Test):
   - Users: 50~100
   - Spawn rate: 10 users/sec
   - 목적: 정상 부하에서의 성능 측정

2. 스트레스 테스트 (Stress Test):
   - Users: 500~1000
   - Spawn rate: 50 users/sec
   - 목적: 시스템 한계점 파악

3. 스파이크 테스트 (Spike Test):
   - Users: 급격히 증가 (0 → 500)
   - Spawn rate: 100 users/sec
   - 목적: 갑작스런 트래픽 대응 능력

4. 내구성 테스트 (Endurance Test):
   - Users: 50~100
   - Duration: 1시간 이상
   - 목적: 메모리 누수, 성능 저하 확인

주요 메트릭:
- RPS (Requests Per Second): 초당 처리 요청 수
- Response Time: 응답 시간 (평균, P50, P95, P99)
- Error Rate: 에러 발생률
- Concurrent Users: 동시 사용자 수
"""

# 고급 기능 예시
"""
1. 순차 실행 (SequentialTaskSet):
   from locust import SequentialTaskSet

   class UserJourney(SequentialTaskSet):
       @task
       def step1_create(self):
           # 먼저 생성

       @task
       def step2_update(self):
           # 그 다음 수정

2. 이벤트 훅:
   from locust import events

   @events.test_start.add_listener
   def on_test_start(environment, **kwargs):
       print("테스트 시작!")

3. 커스텀 메트릭:
   from locust import events

   @events.request.add_listener
   def on_request(request_type, name, response_time, **kwargs):
       # 커스텀 로직
"""
