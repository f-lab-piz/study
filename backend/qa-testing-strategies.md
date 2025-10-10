# QA 테스트 전략: 테스트 유저 관리와 외부 API 호출 개선

## 목차
1. [테스트 유저 관리](#1-테스트-유저-관리)
2. [외부 API 호출 개선](#2-외부-api-호출-개선)
3. [두 전략의 통합](#3-두-전략의-통합)

---

## 1. 테스트 유저 관리

### 문제 정의

#### 배경
실제 사용자 데이터(홈택스, 금융 정보 등)를 연동하는 서비스에서 테스트 시 다음과 같은 제약사항이 발생합니다:

- **단일 테스터의 한계**: 한 명의 테스터가 모든 비즈니스 시나리오를 테스트할 수 없음
  - 예: 환급액이 있는 경우 vs 없는 경우
  - 예: 홈택스 가입자 vs 미가입자

#### 기존 접근 방식의 문제점

```python
# 문제가 있는 기존 코드
TEST_EMAILS = [
    "test1@company.com",
    "test2@company.com",
]

if user.email in TEST_EMAILS:
    # 특정 플로우 강제 실행
    return mock_data
```

**한계점:**
- ❌ 코드 수정 없이 테스트 케이스 변경 불가
- ❌ 테스터와 시나리오 매핑 관리 어려움
- ❌ 모든 테스트 유저가 동일한 시나리오만 테스트 가능
- ❌ 새로운 테스트 케이스 추가 시 코드 배포 필요

#### "특정 플로우 강제 실행"이란?

**정의**: 테스트 계정으로 로그인했을 때, 일반 사용자가 실제 조건을 만족하지 않아도 특정 로직을 "무조건 실행"되게 만드는 것

**예시:**

```python
# 예시 1: 환급 시나리오 강제
if user.email in TEST_EMAILS:
    # 홈택스에서 실제 조회 안 하고
    # 환급 가능한 것처럼 mock 데이터 반환
    return {"refund_amount": 123456, "status": "eligible"}

# 예시 2: 가입 절차 스킵
if user.email in TEST_EMAILS:
    # 본인 인증 절차 건너뛰고 바로 다음 단계로
    user.verified = True

# 예시 3: API 응답 조작
if user.email in TEST_EMAILS:
    return {"bank_balance": 9999999, "transactions": []}
```

---

### 해결 방안: 데이터베이스 기반 동적 관리

#### 아키텍처 설계

```
┌─────────────┐      M:N       ┌──────────────┐
│    User     │◄──────────────►│  TestCase    │
└─────────────┘                └──────────────┘
       ▲                              │
       │                              │
       └──────────────────────────────┘
              UserTestCaseAssignment
```

#### 핵심 아이디어

1. **테스트 케이스를 DB에 저장**: 코드가 아닌 데이터로 관리
2. **유저-시나리오 매핑**: 유연한 M:N 관계로 다양한 조합 가능
3. **환경 분리**: 프로덕션에서는 완전히 비활성화

#### 프로젝트 구조

```
test_user_management/
├── apps/
│   ├── test_manager/
│   │   ├── models.py          # TestCase, UserTestCaseAssignment 모델
│   │   ├── admin.py           # Django Admin 설정
│   │   └── utils.py           # is_test_user_for_scenario() 유틸리티
│   └── user/
│       └── models.py          # Custom User 모델
├── services/
│   ├── external_api.py        # 외부 API 연동 (홈택스 등)
│   └── calculation.py         # 환급 계산 비즈니스 로직
└── config/
    └── settings.py            # IS_PRODUCTION 설정
```

---

### 모델 정의

```python
# apps/test_manager/models.py
from django.db import models
from django.db.models import TextChoices


class UserTestCaseNames(TextChoices):
    """
    데이터베이스 'test_cases' 테이블의 'name' 컬럼에 있는 값들을
    코드에서 안전하게 사용하기 위해 정의하는 상수 목록
    """
    NOT_HOMETAX_MEMBER = ("NotHomeTaxMember", "홈택스 미가입자")
    MONTHLY_RENT_REFUND_AMOUNT = ("MonthlyRentRefundAmount", "월세 환급액 존재")


class TestCase(models.Model):
    """테스트 시나리오 정의"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="테스트 케이스 이름",
        help_text="코드에서 사용할 테스트 케이스 키"
    )
    users = models.ManyToManyField(
        "user.User",
        through="UserTestCaseAssignment",
        related_name="test_cases",
        blank=True
    )

    class Meta:
        db_table = "test_cases"


class UserTestCaseAssignment(models.Model):
    """유저-테스트케이스 매핑"""
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    test_case = models.ForeignKey("TestCase", on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_test_case_assignments"
        unique_together = ["user", "test_case"]
```

---

### 핵심 유틸리티 함수

```python
# apps/test_manager/utils.py
from django.conf import settings
from apps.test_manager.models import UserTestCaseAssignment


def is_test_user_for_scenario(user_id: int, scenario: str) -> bool:
    """
    특정 유저가 특정 테스트 시나리오에 할당되었는지 확인
    개발/스테이징 환경에서만 동작

    Args:
        user_id: 확인할 유저 ID
        scenario: 테스트 시나리오 이름 (예: "NOT_HOMETAX_MEMBER")

    Returns:
        bool: 테스트 유저 여부
    """
    # 프로덕션에서는 항상 False 반환
    if settings.IS_PRODUCTION:
        return False

    try:
        return UserTestCaseAssignment.objects.filter(
            user_id=user_id,
            test_case__name=scenario
        ).exists()
    except Exception:
        # 테이블이 없거나 에러 발생 시 안전하게 False 반환
        return False
```

**안전 장치:**
1. ✅ 프로덕션 환경 체크 (`IS_PRODUCTION`)
2. ✅ 예외 처리로 안전한 폴백

---

### Django Admin 설정

```python
# apps/test_manager/admin.py
from django.contrib import admin
from .models import TestCase, UserTestCaseAssignment


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(UserTestCaseAssignment)
class UserTestCaseAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "test_case", "assigned_at")
    list_filter = ("test_case",)
    search_fields = ("user__email",)
```

**QA가 Admin에서 할 수 있는 작업:**
- ✅ 테스트 시나리오 추가/수정
- ✅ 유저별 시나리오 할당
- ✅ 코드 배포 없이 즉시 반영

---

### 실제 사용 예시

#### 외부 API 연동

```python
# services/external_api.py
from django.conf import settings
from apps.test_manager.utils import is_test_user_for_scenario


def check_hometax_registration(user_id: int):
    """홈택스 가입 여부 확인"""
    # 프로덕션이 아닌 경우에만 테스트 유저 체크
    if not settings.IS_PRODUCTION:
        if is_test_user_for_scenario(user_id, "NOT_HOMETAX_MEMBER"):
            return {"registered": False}

    # 실제 외부 API 호출
    response = external_api_call(user_id)
    return response
```

#### 환급 계산 로직

```python
# services/calculation.py
from django.conf import settings
from apps.test_manager.utils import is_test_user_for_scenario


def calculate_refund(user_id: int):
    """환급액 계산 - 테스트 시나리오 포함"""
    # 프로덕션이 아닌 경우에만 테스트 유저 체크
    if not settings.IS_PRODUCTION:
        if is_test_user_for_scenario(user_id, "MONTHLY_RENT_REFUND"):
            # 항상 환급액이 있는 시나리오
            return {"amount": 1_500_000, "reason": "월세 환급 테스트"}

    # 실제 계산 로직
    income = get_user_income(user_id)
    if income > 70_000_000:
        return {"amount": 0, "reason": "소득 초과"}

    return calculate_actual_refund(user_id)
```

---

### Before/After 비교

#### Before: 이메일 하드코딩 방식

```python
TEST_EMAILS = [
    "test1@company.com",
    "test2@company.com",
]

@login_required
def process_refund_legacy(request):
    user = request.user

    # 테스트 유저 체크 (이메일 기반)
    if user.email in TEST_EMAILS:
        # Mock 데이터 반환
        return JsonResponse({
            "success": True,
            "hometax_status": {"registered": False, "is_test": True},
            "refund_amount": {"amount": 1_500_000, "is_test": True}
        })

    # 실제 유저인 경우 정상 플로우
    hometax_status = check_hometax_registration(user.id)
    refund_amount = calculate_refund(user.id)

    return JsonResponse({
        "success": True,
        "hometax_status": hometax_status,
        "refund_amount": refund_amount
    })
```

**문제점:**
- ❌ 모든 테스트 유저가 동일한 시나리오만 테스트
- ❌ 코드 수정 없이 테스트 케이스 변경 불가
- ❌ 뷰 레이어에 비즈니스 로직 침투

#### After: DB 기반 동적 관리

```python
@login_required
def process_refund(request):
    """환급 처리 전체 플로우"""
    user_id = request.user.id

    try:
        # 1. 홈택스 가입 확인 (내부에서 테스트 유저 체크)
        hometax_status = check_hometax_registration(user_id)

        # 2. 환급액 계산 (내부에서 테스트 유저 체크)
        refund_amount = calculate_refund(user_id)

        return JsonResponse({
            "success": True,
            "user": request.user.username,
            "hometax_status": hometax_status,
            "refund_amount": refund_amount
        })

    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=500
        )
```

**개선 사항:**
- ✅ **유연성**: Admin에서 유저-시나리오 매핑 자유롭게 변경
- ✅ **확장성**: 새로운 테스트 케이스를 DB에만 추가
- ✅ **안전성**: 프로덕션에서 완전히 비활성화
- ✅ **책임 분리**: 비즈니스 로직이 서비스 레이어에 위치

---

### 추가 개선 포인트

#### 1. 캐싱 적용

```python
from django.core.cache import cache


def is_test_user_for_scenario(user_id: int, scenario: str) -> bool:
    if settings.IS_PRODUCTION:
        return False

    cache_key = f"test_scenario:{user_id}:{scenario}"
    cached_result = cache.get(cache_key)

    if cached_result is not None:
        return cached_result

    exists = UserTestCaseAssignment.objects.filter(
        user_id=user_id,
        test_case__name=scenario
    ).exists()

    cache.set(cache_key, exists, timeout=300)  # 5분 캐싱
    return exists
```

#### 2. Mock 데이터 설정 (선택)

```python
class TestCase(models.Model):
    name = models.CharField(max_length=100, unique=True)
    config = models.JSONField(default=dict, blank=True)
    # 예: {"refund_amount": 1000000, "registered": False}
```

#### 3. 로그 추적

```python
import logging
logger = logging.getLogger(__name__)


def check_hometax_registration(user_id: int):
    if not settings.IS_PRODUCTION:
        if is_test_user_for_scenario(user_id, "NOT_HOMETAX_MEMBER"):
            logger.info(f"[TEST_FLOW] user={user_id} NOT_HOMETAX_MEMBER triggered")
            return {"registered": False}

    return external_api_call(user_id)
```

---

## 2. 외부 API 호출 개선

### 문제점 분석

현재 외부 API Helper 구조의 세 가지 주요 문제:

#### 1. 하드코딩된 API 요청 데이터

```python
class APIHelper:
    def get_tax_report_detail(self, auth_method: str, name: str, ...):
        body_data = {
            "loginMethod": login_method,
            "resNm": name,
            "resNo": birth_date,
            # ... 20개 이상의 하드코딩된 필드
            "inqrDtStrt": "20230101",  # 하드코딩
            "inqrDtEnd": "20231231",   # 하드코딩
        }
```

**문제점:**
- ❌ 데이터 구조가 메서드 내부에 숨겨져 있음
- ❌ 타입 검증이 런타임에만 가능
- ❌ 테스트 시 데이터 구조 파악이 어려움

#### 2. Dependency Injection 부재

```python
class HomeTaxDataFetchView(APIView):
    def perform_post_logic(self, request, *args, **kwargs) -> Response:
        # View 내부에서 직접 인스턴스화
        api_helper = WorkerAPIHelper(
            EXTERNAL_API_USER_ID,
            EXTERNAL_API_KEY
        )

        # 비즈니스 로직
        api_helper.get_tax_report_data(...)
```

**문제점:**
- ❌ 테스트 시 실제 API를 호출하거나 복잡한 패치 필요
- ❌ Mock 객체 주입이 어려움
- ❌ **가장 큰 문제**

#### 3. 응답 데이터 검증 부재

```python
async def download_year_end_reconciliation_pdf(self, ...):
    response_json = await self.async_api_call(...)

    # 타입 검증 없이 딕셔너리 접근
    common = response_json["common"]  # KeyError 가능
    err_yn = common["errYn"]          # 타입 불명확
    err_msg = common["errMsg"]        # 필드 누락 시 에러

    if err_yn == "Y":  # 문자열 비교로 에러 처리
        logger.error(f"{err_msg}")
        return None
```

**문제점:**
- ❌ 응답 데이터 구조 파악이 어려움
- ❌ 타입 검증 없어 잘못된 데이터 타입 처리 불가
- ❌ 에러 응답 처리 로직이 분산됨

---

### 해결 방안

#### Pydantic 스키마 도입

**요청 데이터:**

```python
# services/weather_api/schemas.py
from pydantic import BaseModel, Field


class WeatherForecastRequestSchema(BaseModel):
    """날씨 예보 요청 스키마"""
    city: str = Field(..., description="도시 이름")
    country_code: str = Field(..., description="국가 코드 (예: KR)")
    start_date: str = Field(..., description="시작 날짜 (YYYYMMDD)")
    end_date: str = Field(..., description="종료 날짜 (YYYYMMDD)")

    class Config:
        # 자동 타입 변환
        validate_assignment = True
```

**응답 데이터:**

```python
from typing import Optional


class WeatherForecastResponseSchema(BaseModel):
    """날씨 예보 응답 스키마"""
    temperature: float
    humidity: int
    condition: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def is_error(self) -> bool:
        """에러 여부 확인"""
        return self.error_code is not None
```

---

### Dependency Injection 패턴 적용

#### Interface 정의

```python
# services/weather_api/interface.py
from abc import ABC, abstractmethod
from typing import Dict


class IWeatherAPIClient(ABC):
    """날씨 API 클라이언트 인터페이스"""

    @abstractmethod
    def get_weather_forecast(
        self,
        request: WeatherForecastRequestSchema
    ) -> WeatherForecastResponseSchema:
        """날씨 예보 조회"""
        pass
```

#### 실제 구현

```python
# services/weather_api/api_helper.py
class WeatherAPIHelper(IWeatherAPIClient):
    """실제 날씨 API 호출 클래스"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weather.com"

    def get_weather_forecast(
        self,
        request: WeatherForecastRequestSchema
    ) -> WeatherForecastResponseSchema:
        """날씨 예보 조회"""
        # 1. Pydantic 모델 → dict 변환
        body_data = request.dict()

        # 2. API 호출
        response = self._post("/forecast", data=body_data)

        # 3. 응답을 Pydantic 모델로 검증
        return WeatherForecastResponseSchema(**response)
```

#### View에서 DI 활용

```python
# api/v1/weather/views.py
from typing import Optional


class WeatherForecastView(APIView):
    """날씨 예보 조회 뷰 - DI 적용"""

    def __init__(
        self,
        weather_api_client: Optional[IWeatherAPIClient] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        # DI: 외부에서 주입 가능, 기본값은 실제 구현체
        self.weather_api_client = weather_api_client or WeatherAPIHelper(
            api_key=settings.WEATHER_API_KEY
        )

    def post(self, request):
        """날씨 예보 조회"""
        # 1. 요청 데이터를 Pydantic 모델로 검증
        request_data = WeatherForecastRequestSchema(
            city=request.data.get("city"),
            country_code=request.data.get("country_code"),
            start_date=request.data.get("start_date"),
            end_date=request.data.get("end_date")
        )

        # 2. API 호출 (주입된 클라이언트 사용)
        weather_data = self.weather_api_client.get_weather_forecast(request_data)

        # 3. 에러 처리
        if weather_data.is_error:
            return Response(
                {"error": weather_data.error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. 정상 응답
        return Response({
            "temperature": weather_data.temperature,
            "humidity": weather_data.humidity,
            "condition": weather_data.condition
        })
```

---

### 테스트 코드 개선

#### Before: 복잡한 패치

```python
class TestWeatherViewLegacy(TestCase):
    @patch("services.weather_api.api_helper.WeatherAPIHelper")
    def test_get_weather_forecast(self, mock_helper_class):
        # Mock 클래스와 인스턴스 모두 설정 필요
        mock_instance = MagicMock()
        mock_helper_class.return_value = mock_instance
        mock_instance.get_weather_forecast.return_value = {...}

        # 테스트 실행
        response = self.client.post("/api/weather/", {...})

        # 검증
        self.assertEqual(response.status_code, 200)
```

#### After: 간단한 DI

```python
class TestWeatherView(TestCase):
    def test_get_weather_forecast(self):
        # 1. Mock 클라이언트 생성
        mock_client = MagicMock(spec=IWeatherAPIClient)
        mock_client.get_weather_forecast.return_value = WeatherForecastResponseSchema(
            temperature=25.5,
            humidity=60,
            condition="sunny"
        )

        # 2. View에 Mock 주입
        view = WeatherForecastView(weather_api_client=mock_client)

        # 3. 테스트 실행
        request = self.factory.post("/api/weather/", {
            "city": "Seoul",
            "country_code": "KR",
            "start_date": "20250101",
            "end_date": "20250107"
        })

        response = view.post(request)

        # 4. 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["temperature"], 25.5)
```

**개선 사항:**
- ✅ Mock 객체를 직접 주입 - 간단명료
- ✅ 복잡한 패치 불필요
- ✅ View 내부 구현 변경에 영향 없음

---

### Before/After 전체 비교

| 항목 | Before (레거시) | After (개선) |
|-----|----------------|-------------|
| **요청 데이터** | dict 하드코딩, 타입 불명확 | Pydantic 스키마, 자동 검증 |
| **응답 데이터** | dict 접근, KeyError 위험 | Pydantic 모델, 타입 안전 |
| **에러 처리** | if문 분산, 구조 불명확 | 스키마 속성 (`is_error`) |
| **의존성 주입** | View 내부 인스턴스화 | 생성자 주입, 인터페이스 기반 |
| **테스트** | 복잡한 패치 필요 | Mock 직접 주입 |
| **IDE 지원** | ❌ 자동완성 없음 | ✅ 자동완성, 타입 체크 |

---

## 3. 두 전략의 통합

### 연결점 분석

| 구분 | 테스트 유저 관리 | 외부 API 구조 개선 |
|-----|----------------|------------------|
| **핵심 문제** | 테스트 시나리오를 코드 수정 없이 바꾸고 싶다 | 외부 API 호출을 안정적으로 테스트하고 싶다 |
| **기술적 병목** | 코드 내부 하드코딩, 시나리오 변경 시 배포 필요 | 외부 API 직접 호출, Mock 주입 불가 |
| **개선 목표** | 테스트 환경을 동적으로 제어 | 테스트 환경을 안전하게 격리 |
| **도입 기술** | DB 기반 시나리오 + Admin 관리 | Pydantic (스키마화) + Dependency Injection |

**결론**:
- 전자는 **"테스트 입력"**을 통제
- 후자는 **"테스트 환경(의존성)"**을 통제
- 두 방향 모두 **테스트 독립성과 유지보수성 확보**를 목표

---

### 통합 예시 1: 테스트 시나리오 → API 요청 데이터

```python
# services/tax_api/api_helper.py
from apps.test_manager.utils import is_test_user_for_scenario


class TaxAPIHelper(ITaxAPIClient):
    def get_tax_report(
        self,
        user_id: int,
        request: TaxReportRequestSchema
    ) -> TaxReportResponseSchema:
        """세금 보고서 조회"""

        # 테스트 유저 시나리오에 따라 요청 데이터 수정
        if not settings.IS_PRODUCTION:
            if is_test_user_for_scenario(user_id, "NOT_HOMETAX_MEMBER"):
                # 홈택스 미가입자 시나리오: loginMethod 변경
                request.login_method = "NONE"

            if is_test_user_for_scenario(user_id, "HIGH_INCOME"):
                # 고소득자 시나리오: 소득 금액 변경
                request.annual_income = 100_000_000

        # API 호출
        response = self._post("/tax/report", data=request.dict())
        return TaxReportResponseSchema(**response)
```

**효과:**
- QA가 Admin에서 시나리오를 선택하면
- API 요청 파라미터가 자동으로 변경됨
- 코드 수정, 배포 불필요

---

### 통합 예시 2: 시나리오별 Mock API 주입

```python
# services/tax_api/mock_helper.py
class MockTaxAPIHelper(ITaxAPIClient):
    """테스트용 Mock API Helper"""

    def get_tax_report(
        self,
        user_id: int,
        request: TaxReportRequestSchema
    ) -> TaxReportResponseSchema:
        """Mock 응답 반환"""
        return TaxReportResponseSchema(
            refund_amount=1_500_000,
            is_error=False,
            error_message=None
        )


class ErrorMockTaxAPIHelper(ITaxAPIClient):
    """에러 시나리오용 Mock API Helper"""

    def get_tax_report(
        self,
        user_id: int,
        request: TaxReportRequestSchema
    ) -> TaxReportResponseSchema:
        """에러 응답 반환"""
        return TaxReportResponseSchema(
            refund_amount=0,
            is_error=True,
            error_message="API 서버 장애"
        )
```

```python
# api/v1/tax/views.py
def get_api_client_for_user(user_id: int) -> ITaxAPIClient:
    """유저의 테스트 시나리오에 따라 적절한 API 클라이언트 반환"""
    if settings.IS_PRODUCTION:
        return RealTaxAPIHelper(api_key=settings.TAX_API_KEY)

    # 테스트 환경에서만 시나리오 체크
    if is_test_user_for_scenario(user_id, "API_SUCCESS"):
        return MockTaxAPIHelper()
    elif is_test_user_for_scenario(user_id, "API_FAILURE"):
        return ErrorMockTaxAPIHelper()
    else:
        return RealTaxAPIHelper(api_key=settings.TAX_API_KEY)


class TaxReportView(APIView):
    def post(self, request):
        user_id = request.user.id

        # 1. 유저 시나리오에 맞는 API 클라이언트 선택
        api_client = get_api_client_for_user(user_id)

        # 2. 요청 데이터 준비
        request_data = TaxReportRequestSchema(
            name=request.data.get("name"),
            birth_date=request.data.get("birth_date"),
            # ...
        )

        # 3. API 호출 (실제 또는 Mock)
        tax_data = api_client.get_tax_report(user_id, request_data)

        # 4. 응답 처리
        if tax_data.is_error:
            return Response({"error": tax_data.error_message}, status=400)

        return Response({"refund_amount": tax_data.refund_amount})
```

**효과:**
- QA가 Admin에서 "API 장애" 시나리오 선택
- 해당 유저 로그인 시 Mock API가 자동으로 주입됨
- 실제 외부 API 없이도 에러 상황 테스트 가능

---

### 통합 예시 3: 응답 검증 자동화

```python
# tests/test_tax_report_scenarios.py
from apps.test_manager.models import TestCase, UserTestCaseAssignment


class TestTaxReportScenarios(TestCase):
    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create(email="qa@test.com")

        # 시나리오 생성
        self.success_case = TestCase.objects.create(name="API_SUCCESS")
        self.failure_case = TestCase.objects.create(name="API_FAILURE")

    def test_success_scenario(self):
        """성공 시나리오 테스트"""
        # 1. 시나리오 할당
        UserTestCaseAssignment.objects.create(
            user=self.user,
            test_case=self.success_case
        )

        # 2. API 호출
        response = self.client.post(
            "/api/tax/report/",
            {"name": "홍길동", "birth_date": "19900101"}
        )

        # 3. Pydantic 모델로 응답 검증
        data = TaxReportResponseSchema(**response.json())
        self.assertFalse(data.is_error)
        self.assertGreater(data.refund_amount, 0)

    def test_failure_scenario(self):
        """실패 시나리오 테스트"""
        # 1. 시나리오 할당
        UserTestCaseAssignment.objects.create(
            user=self.user,
            test_case=self.failure_case
        )

        # 2. API 호출
        response = self.client.post(
            "/api/tax/report/",
            {"name": "홍길동", "birth_date": "19900101"}
        )

        # 3. Pydantic 모델로 응답 검증
        data = TaxReportResponseSchema(**response.json())
        self.assertTrue(data.is_error)
        self.assertIsNotNone(data.error_message)
```

---

### 전체 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                       QA Admin 페이지                        │
│                                                              │
│  "qa@test.com 유저에게 'API_FAILURE' 시나리오 할당"         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Database (MySQL)                        │
│                                                              │
│  user_test_case_assignments 테이블:                         │
│  ┌─────────┬──────────────┬──────────────┐                 │
│  │ user_id │ test_case_id │ assigned_at  │                 │
│  ├─────────┼──────────────┼──────────────┤                 │
│  │   123   │      5       │  2025-10-10  │                 │
│  └─────────┴──────────────┴──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Django View Layer                        │
│                                                              │
│  def post(self, request):                                   │
│      user_id = request.user.id  # 123                       │
│                                                              │
│      # 1. 시나리오 확인 (DB 조회)                           │
│      api_client = get_api_client_for_user(user_id)         │
│      # → ErrorMockTaxAPIHelper 반환                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Dependency Injection                       │
│                                                              │
│  if is_test_user_for_scenario(user_id, "API_FAILURE"):     │
│      return ErrorMockTaxAPIHelper()  ← Mock 주입            │
│  else:                                                       │
│      return RealTaxAPIHelper()       ← 실제 API             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Pydantic 스키마                         │
│                                                              │
│  request_data = TaxReportRequestSchema(...)                 │
│  response_data = api_client.get_report(request_data)        │
│  # → TaxReportResponseSchema 반환                           │
│                                                              │
│  if response_data.is_error:                                 │
│      return error_response                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 핵심 요약

### 테스트 유저 관리

| 항목 | Before | After |
|-----|--------|-------|
| **관리 방식** | 코드 하드코딩 | DB + Admin UI |
| **시나리오 변경** | 코드 수정 + 배포 | Admin에서 즉시 반영 |
| **유연성** | 모든 테스트 유저 동일 시나리오 | 유저별 다양한 시나리오 조합 |
| **프로덕션 안전성** | 위험 | IS_PRODUCTION 체크로 완전 격리 |

### 외부 API 호출 개선

| 항목 | Before | After |
|-----|--------|-------|
| **요청 데이터** | dict 하드코딩 | Pydantic 스키마 |
| **응답 검증** | 타입 불명확, KeyError 위험 | Pydantic 자동 검증 |
| **의존성 주입** | View 내부 인스턴스화 | 생성자 주입 |
| **테스트** | 복잡한 패치 | Mock 직접 주입 |
| **IDE 지원** | ❌ | ✅ 자동완성, 타입 체크 |

### 통합 효과

```
테스트 유저 DB 설정 (시나리오)
         ↓
   Pydantic Request (입력 제어)
         ↓
Dependency Injection (환경 제어)
         ↓
   Pydantic Response (결과 검증)
```

**최종 결과:**
- ✅ QA가 코드 수정 없이 다양한 시나리오 테스트 가능
- ✅ 외부 API 없이도 모든 상황 재현 가능
- ✅ 프로덕션 환경 완전 격리
- ✅ 타입 안정성 확보
- ✅ 테스트 코드 간소화

---

## 구현 체크리스트

### Phase 1: 테스트 유저 관리 구축
- [ ] `TestCase`, `UserTestCaseAssignment` 모델 생성
- [ ] `is_test_user_for_scenario()` 유틸리티 함수 구현
- [ ] Django Admin 설정
- [ ] `IS_PRODUCTION` 환경 변수 설정
- [ ] 비즈니스 로직에 시나리오 체크 추가

### Phase 2: 외부 API 개선
- [ ] Pydantic Request/Response 스키마 정의
- [ ] `IAPIClient` 인터페이스 정의
- [ ] 실제 API Helper에 Pydantic 적용
- [ ] View에 Dependency Injection 적용
- [ ] 테스트 코드 리팩토링

### Phase 3: 통합
- [ ] 시나리오별 Mock API Helper 구현
- [ ] `get_api_client_for_user()` 팩토리 함수 구현
- [ ] 시나리오별 요청 데이터 자동 변경 로직 추가
- [ ] 통합 테스트 작성
- [ ] 캐싱 적용 (선택)
- [ ] 로그 추적 기능 추가 (선택)

---

## 참고 자료

- **Pydantic 공식 문서**: https://docs.pydantic.dev/
- **Django Admin 커스터마이징**: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
- **Dependency Injection 패턴**: https://en.wikipedia.org/wiki/Dependency_injection
- **Django Testing Best Practices**: https://docs.djangoproject.com/en/stable/topics/testing/overview/
