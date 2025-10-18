"""
통합 테스트 (Integration Tests)

통합 테스트란?
- 여러 컴포넌트가 함께 동작하는 것을 테스트
- 실제 API 엔드포인트를 호출하여 전체 플로우 검증
- HTTP 요청 → 라우터 → DB → 응답 전체 과정 테스트

이 파일에서는:
- FastAPI의 TestClient를 사용한 E2E 테스트
- HTTP 메서드별 API 테스트 (GET, POST, PUT, DELETE)
- 상태 코드 및 응답 데이터 검증
"""
import pytest
from fastapi import status


class TestTodoAPI:
    """TODO API 엔드포인트 통합 테스트"""

    def test_root_endpoint(self, client):
        """
        루트 엔드포인트 테스트

        TestClient 사용법:
        - client.get(), client.post() 등으로 HTTP 요청
        - response.status_code로 상태 코드 확인
        - response.json()으로 응답 데이터 확인
        """
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "TODO API에 오신 것을 환영합니다!" in data["message"]

    def test_health_check_endpoint(self, client):
        """헬스 체크 엔드포인트 테스트"""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestTodoCRUD:
    """TODO CRUD 작업 통합 테스트"""

    def test_create_todo(self, client, sample_todo_data):
        """
        POST /todos/ - TODO 생성 테스트

        전체 플로우:
        1. HTTP POST 요청
        2. Pydantic 검증
        3. DB에 저장
        4. 응답 반환
        """
        # Act
        response = client.post("/todos/", json=sample_todo_data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # 응답 데이터 검증
        assert data["title"] == sample_todo_data["title"]
        assert data["description"] == sample_todo_data["description"]
        assert data["completed"] == sample_todo_data["completed"]
        assert "id" in data  # ID가 생성되었는지
        assert "created_at" in data  # 타임스탬프가 있는지
        assert "updated_at" in data

    def test_create_todo_invalid_data(self, client):
        """
        POST /todos/ - 유효하지 않은 데이터로 생성 시도

        FastAPI의 자동 검증 기능 테스트
        """
        # Arrange
        invalid_data = {
            # title 필드 누락 (필수 필드)
            "description": "제목이 없음",
            "completed": False
        }

        # Act
        response = client.post("/todos/", json=invalid_data)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_todo_list_empty(self, client):
        """
        GET /todos/ - 빈 TODO 리스트 조회

        DB에 아무것도 없을 때 빈 리스트 반환하는지 확인
        """
        # Act
        response = client.get("/todos/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_todo_list_with_data(self, client, sample_todo_in_db):
        """
        GET /todos/ - TODO 리스트 조회 (데이터 있음)

        sample_todo_in_db 픽스처:
        - 테스트 전에 미리 TODO 하나가 DB에 저장되어 있음
        """
        # Act
        response = client.get("/todos/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == sample_todo_in_db.id
        assert data[0]["title"] == sample_todo_in_db.title

    def test_get_single_todo(self, client, sample_todo_in_db):
        """
        GET /todos/{todo_id} - 특정 TODO 조회
        """
        # Arrange
        todo_id = sample_todo_in_db.id

        # Act
        response = client.get(f"/todos/{todo_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == sample_todo_in_db.title

    def test_get_single_todo_not_found(self, client):
        """
        GET /todos/{todo_id} - 존재하지 않는 TODO 조회

        404 에러 처리 테스트
        """
        # Arrange
        non_existent_id = 99999

        # Act
        response = client.get(f"/todos/{non_existent_id}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data  # 에러 메시지 확인

    def test_update_todo(self, client, sample_todo_in_db):
        """
        PUT /todos/{todo_id} - TODO 수정
        """
        # Arrange
        todo_id = sample_todo_in_db.id
        update_data = {
            "title": "수정된 제목",
            "completed": True
        }

        # Act
        response = client.put(f"/todos/{todo_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == "수정된 제목"
        assert data["completed"] is True

    def test_update_todo_partial(self, client, sample_todo_in_db):
        """
        PUT /todos/{todo_id} - TODO 부분 수정

        TodoUpdate는 모든 필드가 Optional이므로 일부만 수정 가능
        """
        # Arrange
        todo_id = sample_todo_in_db.id
        update_data = {
            "completed": True
            # title, description은 수정하지 않음
        }

        # Act
        response = client.put(f"/todos/{todo_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
        assert data["title"] == sample_todo_in_db.title  # 변경되지 않음

    def test_delete_todo(self, client, sample_todo_in_db):
        """
        DELETE /todos/{todo_id} - TODO 삭제
        """
        # Arrange
        todo_id = sample_todo_in_db.id

        # Act
        response = client.delete(f"/todos/{todo_id}")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 삭제 확인: 다시 조회 시 404
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    # TODO: 다음 테스트를 작성해보세요
    def test_update_todo_not_found(self, client):
        """
        TODO: 존재하지 않는 TODO 수정 시도

        힌트:
        - 존재하지 않는 ID로 PUT 요청
        - 404 에러가 반환되는지 확인
        """
        pass

    def test_delete_todo_not_found(self, client):
        """
        TODO: 존재하지 않는 TODO 삭제 시도

        힌트:
        - 존재하지 않는 ID로 DELETE 요청
        - 404 에러가 반환되는지 확인
        """
        pass


class TestTodoPagination:
    """TODO 리스트 페이지네이션 테스트"""

    def test_pagination_skip_limit(self, client, test_db):
        """
        GET /todos/?skip=N&limit=M - 페이지네이션 테스트

        여러 TODO를 생성하고 skip, limit 파라미터 테스트
        """
        # Arrange: 10개의 TODO 생성
        from app.models import TodoDB
        for i in range(10):
            todo = TodoDB(title=f"할일 {i}", completed=False)
            test_db.add(todo)
        test_db.commit()

        # Act: skip=5, limit=3으로 조회
        response = client.get("/todos/?skip=5&limit=3")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # limit=3이므로 3개만 반환

    # TODO: 다음 테스트를 작성해보세요
    def test_pagination_default_values(self, client, test_db):
        """
        TODO: 페이지네이션 기본값 테스트

        힌트:
        1. 150개의 TODO 생성
        2. skip, limit 없이 GET /todos/ 호출
        3. 기본 limit이 100인지 확인 (100개만 반환되는지)
        """
        pass

    def test_pagination_empty_page(self, client, test_db):
        """
        TODO: 빈 페이지 조회 테스트

        힌트:
        1. 5개의 TODO 생성
        2. skip=10으로 조회 (존재하지 않는 페이지)
        3. 빈 리스트가 반환되는지 확인
        """
        pass


class TestTodoWorkflow:
    """
    TODO 전체 워크플로우 테스트

    실제 사용자 시나리오를 시뮬레이션
    """

    def test_complete_todo_workflow(self, client):
        """
        완전한 TODO 생명주기 테스트

        시나리오:
        1. TODO 생성
        2. TODO 조회
        3. TODO 수정 (완료 처리)
        4. TODO 삭제
        """
        # 1. TODO 생성
        create_data = {
            "title": "워크플로우 테스트",
            "description": "전체 플로우 테스트",
            "completed": False
        }
        create_response = client.post("/todos/", json=create_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        todo_id = create_response.json()["id"]

        # 2. TODO 조회
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "워크플로우 테스트"

        # 3. TODO 수정 (완료 처리)
        update_response = client.put(
            f"/todos/{todo_id}",
            json={"completed": True}
        )
        assert update_response.status_code == 200
        assert update_response.json()["completed"] is True

        # 4. TODO 삭제
        delete_response = client.delete(f"/todos/{todo_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 5. 삭제 확인
        final_get = client.get(f"/todos/{todo_id}")
        assert final_get.status_code == status.HTTP_404_NOT_FOUND

    # TODO: 다음 워크플로우 테스트를 작성해보세요
    def test_bulk_todo_operations(self, client):
        """
        TODO: 대량 TODO 작업 워크플로우

        시나리오:
        1. 여러 TODO 생성 (5개 이상)
        2. 전체 리스트 조회하여 개수 확인
        3. 일부 TODO 완료 처리
        4. 리스트에서 completed=True인 TODO 확인
        (힌트: 현재는 필터링 기능이 없으므로 전체 조회 후 Python에서 필터링)
        """
        pass

    def test_concurrent_updates(self, client, sample_todo_in_db):
        """
        TODO: 동시 업데이트 시나리오

        시나리오:
        1. 같은 TODO를 두 번 연속 수정
        2. 마지막 수정이 반영되었는지 확인
        3. updated_at 타임스탬프가 변경되었는지 확인
        """
        pass


# 에러 처리 테스트
class TestErrorHandling:
    """API 에러 처리 테스트"""

    def test_invalid_todo_id_type(self, client):
        """
        잘못된 타입의 ID로 요청 시 에러 처리

        FastAPI는 경로 파라미터 타입 검증도 자동으로 수행
        """
        # Act: 문자열 ID 전달 (int 타입 예상)
        response = client.get("/todos/invalid_id")

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # TODO: 다음 에러 처리 테스트를 작성해보세요
    def test_create_todo_with_extra_fields(self, client):
        """
        TODO: 추가 필드가 포함된 데이터로 생성 시도

        힌트:
        - Pydantic은 기본적으로 추가 필드를 무시함
        - 추가 필드를 포함한 데이터로 POST 요청
        - 생성은 성공하지만 추가 필드는 저장되지 않음
        """
        pass

    def test_create_todo_empty_title(self, client):
        """
        TODO: 빈 문자열 title로 생성 시도

        힌트:
        - title=""으로 POST 요청
        - 422 에러가 반환되는지 확인 (min_length=1 제약)
        """
        pass
