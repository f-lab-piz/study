"""
통합 테스트 - HTTP API 레벨 테스트

통합 테스트란?
- TestClient로 실제 HTTP 요청을 시뮬레이션
- 전체 요청/응답 흐름을 검증 (라우터 → 비즈니스 로직 → DB → 응답)
- status_code, response body, 에러 메시지까지 확인

TestClient:
- FastAPI가 제공하는 테스트용 HTTP 클라이언트
- 실제 서버를 띄우지 않고 HTTP 요청/응답을 테스트
- 내부적으로 httpx 사용
"""


# ===========================================
# 1. 기본 엔드포인트 테스트
# ===========================================


class TestHealthEndpoints:
    """루트, 헬스체크 엔드포인트 테스트"""

    def test_root_endpoint(self, client):
        """GET / → 200, 메시지 포함"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"

    def test_health_check(self, client):
        """GET /health → 200, DB 연결 확인"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"

    def test_stats_empty(self, client):
        """GET /stats → 빈 DB에서 total_users = 0"""
        response = client.get("/stats")

        assert response.status_code == 200
        assert response.json()["total_users"] == 0


# ===========================================
# 2. 유저 생성 (POST) 테스트
# ===========================================


class TestCreateUser:
    """POST /users 엔드포인트 테스트"""

    def test_create_user_success(self, client, sample_user_data):
        """정상적인 유저 생성 → 201"""
        response = client.post("/users", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_user_data["name"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert data["id"] > 0

    def test_create_user_duplicate_email(self, client, sample_user_data):
        """같은 이메일로 두 번 생성 → 400"""
        # 첫 번째 생성: 성공
        client.post("/users", json=sample_user_data)

        # 두 번째 생성: 중복 이메일
        response = client.post("/users", json=sample_user_data)

        assert response.status_code == 400
        assert "이미 존재하는 이메일" in response.json()["detail"]

    def test_create_user_missing_name(self, client):
        """name 누락 → 422 (Validation Error)"""
        response = client.post("/users", json={"email": "test@example.com"})

        assert response.status_code == 422

    def test_create_user_missing_email(self, client):
        """email 누락 → 422 (Validation Error)"""
        response = client.post("/users", json={"name": "테스트"})

        assert response.status_code == 422

    def test_create_user_empty_body(self, client):
        """빈 body → 422"""
        response = client.post("/users", json={})

        assert response.status_code == 422

    def test_create_user_extra_fields_ignored(self, client, sample_user_data):
        """
        TODO: 추가 필드가 있어도 무시되고 정상 생성

        힌트:
        1. sample_user_data에 "age": 25 추가
        2. POST /users 요청
        3. 201 응답 확인
        4. 응답에 "age" 필드가 없는지 확인
        """
        pass


# ===========================================
# 3. 유저 조회 (GET) 테스트
# ===========================================


class TestReadUsers:
    """GET /users, GET /users/{id} 엔드포인트 테스트"""

    def test_get_all_users_empty(self, client):
        """빈 DB → 빈 리스트 반환"""
        response = client.get("/users")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_users_with_data(self, client, sample_user_in_db):
        """데이터 있는 DB → 유저 리스트 반환"""
        response = client.get("/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_user_in_db.name

    def test_get_user_by_id_success(self, client, sample_user_in_db):
        """존재하는 ID로 조회 → 200"""
        response = client.get(f"/users/{sample_user_in_db.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_user_in_db.id
        assert data["name"] == sample_user_in_db.name
        assert data["email"] == sample_user_in_db.email

    def test_get_user_by_id_not_found(self, client):
        """존재하지 않는 ID → 404"""
        response = client.get("/users/99999")

        assert response.status_code == 404
        assert "유저를 찾을 수 없습니다" in response.json()["detail"]

    def test_get_user_invalid_id_type(self, client):
        """잘못된 ID 타입 (문자열) → 422"""
        response = client.get("/users/abc")

        assert response.status_code == 422

    def test_pagination_skip_limit(self, client, test_db):
        """
        TODO: 페이지네이션 테스트

        힌트:
        1. 10명의 유저를 생성 (for loop + client.post)
        2. GET /users?skip=3&limit=5 요청
        3. 응답 리스트 길이가 5인지 확인
        4. GET /users?skip=8&limit=5 요청
        5. 응답 리스트 길이가 2인지 확인 (10 - 8 = 2)
        """
        pass


# ===========================================
# 4. 유저 수정 (PUT) 테스트
# ===========================================


class TestUpdateUser:
    """PUT /users/{id} 엔드포인트 테스트"""

    def test_update_user_name_only(self, client, sample_user_in_db):
        """이름만 수정 → 이름 변경, 이메일 유지"""
        response = client.put(
            f"/users/{sample_user_in_db.id}",
            json={"name": "새이름"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "새이름"
        assert data["email"] == sample_user_in_db.email  # 이메일 변경 없음

    def test_update_user_email_only(self, client, sample_user_in_db):
        """이메일만 수정"""
        response = client.put(
            f"/users/{sample_user_in_db.id}",
            json={"email": "new@example.com"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == sample_user_in_db.name  # 이름 변경 없음

    def test_update_user_not_found(self, client):
        """존재하지 않는 유저 수정 → 404"""
        response = client.put(
            "/users/99999",
            json={"name": "없는유저"},
        )

        assert response.status_code == 404

    def test_update_user_duplicate_email(
        self, client, sample_user_in_db, second_user_data
    ):
        """다른 유저의 이메일로 수정 → 400"""
        # 두 번째 유저 생성
        client.post("/users", json=second_user_data)

        # 첫 번째 유저의 이메일을 두 번째 유저 이메일로 변경 시도
        response = client.put(
            f"/users/{sample_user_in_db.id}",
            json={"email": second_user_data["email"]},
        )

        assert response.status_code == 400
        assert "이미 존재하는 이메일" in response.json()["detail"]

    def test_update_user_own_email(self, client, sample_user_in_db):
        """
        TODO: 자기 자신의 이메일로 수정 → 200 (에러 아님)

        힌트:
        1. sample_user_in_db의 현재 이메일로 PUT 요청
        2. 200 응답 확인
        3. 이메일이 변경되지 않았는지 확인
        """
        pass


# ===========================================
# 5. 유저 삭제 (DELETE) 테스트
# ===========================================


class TestDeleteUser:
    """DELETE /users/{id} 엔드포인트 테스트"""

    def test_delete_user_success(self, client, sample_user_in_db):
        """유저 삭제 → 200, 이후 조회 시 404"""
        # 삭제
        response = client.delete(f"/users/{sample_user_in_db.id}")
        assert response.status_code == 200
        assert response.json()["deleted_id"] == sample_user_in_db.id

        # 삭제 확인: 같은 ID로 조회하면 404
        get_response = client.get(f"/users/{sample_user_in_db.id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client):
        """
        TODO: 존재하지 않는 유저 삭제 → 404

        힌트:
        1. DELETE /users/99999 요청
        2. 404 응답 확인
        3. "유저를 찾을 수 없습니다" 메시지 확인
        """
        pass


# ===========================================
# 6. 전체 워크플로우 테스트
# ===========================================


class TestUserWorkflow:
    """여러 API를 조합한 시나리오 테스트"""

    def test_complete_user_lifecycle(self, client):
        """
        전체 생명주기 테스트: 생성 → 조회 → 수정 → 삭제 → 확인

        실제 사용자가 앱을 사용하는 흐름을 시뮬레이션
        """
        # 1. 생성 (Create)
        create_response = client.post(
            "/users",
            json={"name": "김철수", "email": "kim@example.com"},
        )
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # 2. 조회 (Read)
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "김철수"

        # 3. 수정 (Update)
        update_response = client.put(
            f"/users/{user_id}",
            json={"name": "김영희", "email": "younghee@example.com"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "김영희"
        assert update_response.json()["email"] == "younghee@example.com"

        # 4. 삭제 (Delete)
        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 200

        # 5. 삭제 확인
        verify_response = client.get(f"/users/{user_id}")
        assert verify_response.status_code == 404

        # 6. 통계 확인
        stats_response = client.get("/stats")
        assert stats_response.json()["total_users"] == 0

    def test_bulk_user_operations(self, client):
        """
        TODO: 대량 유저 작업 테스트

        힌트:
        1. for 루프로 5명 유저 생성
        2. GET /stats → total_users == 5 확인
        3. GET /users → 리스트 길이 5 확인
        4. 2명 삭제
        5. GET /stats → total_users == 3 확인
        """
        pass
