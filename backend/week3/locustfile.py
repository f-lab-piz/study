"""
Locust 부하 테스트 시나리오 - User CRUD API

Locust란?
- Python 기반 부하 테스트 도구
- 사용자 행동을 시뮬레이션하여 시스템 성능 측정
- 웹 UI 제공으로 실시간 모니터링 가능

사전 준비:
1. week2 서버 실행 (PostgreSQL + FastAPI)
   cd ../week2
   docker compose up -d
   uv run uvicorn main:app --reload --host 0.0.0.0

2. Locust 실행
   cd ../week3
   uv run locust

3. 브라우저에서 http://localhost:8089 접속
   - Host: http://localhost:8000 입력
   - Number of users: 10 (시작은 적게)
   - Spawn rate: 2
   - Start!
"""

import random
import uuid
from locust import HttpUser, task, between


class UserCRUDUser(HttpUser):
    """
    User CRUD 애플리케이션 사용자 시뮬레이션

    HttpUser: Locust의 기본 사용자 클래스
    - HTTP 요청을 보내는 가상 사용자 정의
    - @task 데코레이터로 수행할 작업 정의
    - 가중치(weight)로 실행 빈도 조절
    """

    # 각 태스크 사이 대기 시간 (초)
    # 실제 사용자처럼 1~3초 대기
    wait_time = between(1, 3)

    # 생성된 유저 ID 저장 (조회/수정/삭제에 사용)
    created_user_ids = []

    def on_start(self):
        """
        각 가상 사용자 시작 시 한 번 실행
        - 서버 연결 확인
        """
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"서버 헬스체크 실패: {response.status_code}")

    # -----------------------------------------
    # 유저 생성 (POST /users)
    # -----------------------------------------
    @task(1)
    def create_user(self):
        """
        유저 생성 시나리오

        @task(1): 가중치 1
        - 다른 task와의 실행 비율 결정
        - 예: list(3) : get(2) : create(1) = 3:2:1

        주의: 동시 유저가 많으므로 이메일을 고유하게 생성!
        → uuid로 매번 다른 이메일 생성
        """
        unique_id = uuid.uuid4().hex[:8]
        user_data = {
            "name": f"테스트유저_{unique_id}",
            "email": f"user_{unique_id}@loadtest.com",
        }

        # catch_response=True: 응답을 직접 성공/실패로 판정
        with self.client.post(
            "/users",
            json=user_data,
            name="/users [POST - Create]",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                user_id = response.json().get("id")
                if user_id:
                    self.created_user_ids.append(user_id)
                response.success()
            else:
                response.failure(f"유저 생성 실패: {response.status_code}")

    # -----------------------------------------
    # 유저 리스트 조회 (GET /users)
    # -----------------------------------------
    @task(3)
    def list_users(self):
        """
        유저 리스트 조회 시나리오

        @task(3): 가중치 3 (가장 빈번)
        - 실제 서비스에서 조회가 가장 많이 발생
        - 읽기:쓰기 비율을 반영
        """
        skip = random.randint(0, 50)
        limit = random.choice([10, 20, 50])

        with self.client.get(
            f"/users?skip={skip}&limit={limit}",
            name="/users [GET - List]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                else:
                    response.failure("응답이 리스트가 아님")
            else:
                response.failure(f"리스트 조회 실패: {response.status_code}")

    # -----------------------------------------
    # 유저 단건 조회 (GET /users/{id})
    # -----------------------------------------
    @task(2)
    def get_single_user(self):
        """
        특정 유저 조회 시나리오

        @task(2): 가중치 2
        - 생성된 유저 중 랜덤으로 조회
        """
        if not self.created_user_ids:
            return

        user_id = random.choice(self.created_user_ids)

        with self.client.get(
            f"/users/{user_id}",
            name="/users/{id} [GET - Detail]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # 이미 삭제된 유저일 수 있음 → 에러 아님
                response.success()
            else:
                response.failure(f"유저 조회 실패: {response.status_code}")

    # -----------------------------------------
    # 통계 조회 (GET /stats)
    # -----------------------------------------
    @task(1)
    def get_stats(self):
        """통계 조회 시나리오"""
        with self.client.get(
            "/stats",
            name="/stats [GET]",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"통계 조회 실패: {response.status_code}")

    # -----------------------------------------
    # 유저 수정 (PUT /users/{id})
    # -----------------------------------------
    @task(1)
    def update_user(self):
        """
        TODO: 유저 수정 시나리오를 완성해보세요!

        힌트:
        1. created_user_ids가 비어있으면 return
        2. random.choice로 유저 ID 하나 선택
        3. 업데이트 데이터 작성:
           update_data = {
               "name": f"수정된유저_{uuid.uuid4().hex[:6]}",
           }
        4. self.client.put() 요청:
           - URL: f"/users/{user_id}"
           - json=update_data
           - name="/users/{id} [PUT - Update]"
           - catch_response=True
        5. 200이면 success(), 404면 success() (삭제된 유저)
        6. 그 외는 failure()
        """
        if not self.created_user_ids:
            return

        # TODO: 여기에 코드를 작성하세요
        pass

    # -----------------------------------------
    # 유저 삭제 (DELETE /users/{id})
    # -----------------------------------------
    @task(1)
    def delete_user(self):
        """
        TODO: 유저 삭제 시나리오를 완성해보세요!

        힌트:
        1. created_user_ids가 비어있으면 return
        2. random.choice로 유저 ID 하나 선택
        3. self.client.delete() 요청:
           - URL: f"/users/{user_id}"
           - name="/users/{id} [DELETE]"
           - catch_response=True
        4. 200이면:
           - self.created_user_ids에서 해당 ID 제거
           - response.success()
        5. 404면 success() (이미 삭제됨)
        6. 그 외는 failure()
        """
        pass


# ===========================================
# 워크플로우 시나리오
# ===========================================


class MixedWorkloadUser(HttpUser):
    """
    TODO: 복합 워크플로우 시나리오

    실제 사용자의 행동 패턴을 시뮬레이션:
    1. 유저 생성
    2. 생성된 유저 조회
    3. 유저 정보 수정
    4. 유저 삭제

    하나의 @task에서 순차적으로 실행
    """

    wait_time = between(2, 5)

    @task
    def complete_workflow(self):
        """
        TODO: 전체 워크플로우를 하나의 태스크로 작성

        힌트:
        1. POST /users 로 유저 생성, ID 저장
        2. GET /users/{id} 로 생성 확인
        3. PUT /users/{id} 로 이름 수정
        4. DELETE /users/{id} 로 삭제
        5. 각 단계에서 status_code 확인
        """
        pass


# ===========================================
# 스트레스 테스트 시나리오
# ===========================================


class StressTestUser(HttpUser):
    """
    TODO: 스트레스 테스트 시나리오

    시스템의 한계를 테스트:
    - wait_time을 최소화 (연속 요청)
    - 대량 유저 생성 (쓰기 위주 부하)

    힌트:
    - wait_time = between(0.1, 0.5)
    - @task에서 유저 생성만 반복
    - uuid로 고유 이메일 생성
    """

    pass


# ===========================================
# Locust 테스트 설정 가이드
# ===========================================

"""
시나리오별 권장 설정:

1. 부하 테스트 (Load Test):
   - Users: 10~50
   - Spawn rate: 5 users/sec
   - Duration: 3~5분
   - 목적: 정상 부하에서의 성능 측정

2. 스트레스 테스트 (Stress Test):
   - Users: 100~500
   - Spawn rate: 20 users/sec
   - Duration: 5~10분
   - 목적: 시스템 한계점 파악

3. 스파이크 테스트 (Spike Test):
   - Users: 급격히 증가 (0 → 200)
   - Spawn rate: 50 users/sec
   - Duration: 2~3분
   - 목적: 갑작스런 트래픽 대응 능력

주요 메트릭 해석:
┌──────────────────────┬──────────────────────────────┐
│ 메트릭               │ 설명                          │
├──────────────────────┼──────────────────────────────┤
│ RPS                  │ 초당 처리 요청 수              │
│ Avg Response Time    │ 평균 응답 시간 (ms)            │
│ P50 (Median)         │ 50% 요청이 이 시간 내에 완료   │
│ P95                  │ 95% 요청이 이 시간 내에 완료   │
│ P99                  │ 99% 요청이 이 시간 내에 완료   │
│ Error Rate           │ 에러 발생 비율 (%)             │
└──────────────────────┴──────────────────────────────┘

좋은 성능 기준 (참고):
- P95 응답 시간 < 200ms
- 에러율 < 1%
- RPS가 유저 수 증가에 비례
"""
