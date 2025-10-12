# 학습 확인 QnA

멘토링 시 학생의 이해도를 확인하기 위한 질문 모음입니다.

---

## Python 기초 - 자료구조

### Q1: 리스트 vs 튜플 - 언제 무엇을 사용할까?

**질문:**
다음 시나리오에서 리스트와 튜플 중 어떤 것을 사용하는 것이 더 적절한지 설명하고, 그 이유를 말해주세요.

```python
# 시나리오 1: 사용자가 입력한 쇼핑 목록
shopping_list = ['우유', '계란', '빵']

# 시나리오 2: 위도/경도 좌표
location = (37.5665, 126.9780)

# 시나리오 3: 웹 애플리케이션의 설정값
config = ('localhost', 8000, 'production')
```

**모범 답안:**
- **시나리오 1 (쇼핑 목록)**: 리스트가 적절 → 항목을 추가/삭제/수정할 수 있어야 하므로
- **시나리오 2 (좌표)**: 튜플이 적절 → 위도/경도는 변경되면 안 되는 값이고, 항상 2개의 값만 필요하므로
- **시나리오 3 (설정값)**: 튜플이 적절 → 설정값은 실행 중 변경되면 안 되고, 고정된 개수의 값을 가지므로

**추가 질문:**
- 튜플을 딕셔너리의 키로 사용할 수 있는 이유는?
- 리스트 컴프리헨션 대신 제너레이터 표현식을 사용하는 이유는?

---

### Q2: 딕셔너리 메서드 활용

**질문:**
다음 코드의 실행 결과를 예측하고, 각 메서드의 동작을 설명해주세요.

```python
user = {'name': 'Alice', 'age': 30, 'city': 'Seoul'}

# 1
print(user.get('email'))

# 2
print(user.get('email', 'N/A'))

# 3
user.setdefault('country', 'Korea')
print(user)

# 4
user.setdefault('name', 'Bob')
print(user['name'])
```

**모범 답안:**
1. `None` → 키가 없으면 None 반환 (에러 안 남)
2. `'N/A'` → 키가 없으면 기본값 반환
3. `{'name': 'Alice', 'age': 30, 'city': 'Seoul', 'country': 'Korea'}` → 키가 없으면 추가
4. `'Alice'` → 키가 이미 있으면 기존 값 유지 (변경 안 됨)

**추가 설명:**
- `user['email']`은 KeyError 발생, `user.get('email')`은 None 반환
- `setdefault`는 키가 없을 때만 추가하므로 안전하게 기본값 설정 가능

---

### Q3: 슬라이싱 마스터하기

**질문:**
다음 슬라이싱 연산의 결과를 예측하고, 각각 어떤 상황에서 유용한지 설명해주세요.

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

a = numbers[::2]
b = numbers[1::2]
c = numbers[::-1]
d = numbers[2:8:2]
e = numbers[-3:]
```

**모범 답안:**
- `a = [0, 2, 4, 6, 8]` → 짝수 인덱스 (2칸씩 건너뛰기), 홀짝 분리할 때 유용
- `b = [1, 3, 5, 7, 9]` → 홀수 인덱스, 데이터 교차 추출할 때 유용
- `c = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]` → 역순 정렬, 리스트 뒤집기
- `d = [2, 4, 6]` → 2부터 7까지 2칸씩, 특정 범위 샘플링
- `e = [7, 8, 9]` → 마지막 3개, 최근 데이터 가져올 때 유용

**실전 활용:**
```python
# 최근 10개 로그만 표시
recent_logs = all_logs[-10:]

# 홀수/짝수 인덱스로 데이터 분할
train_data = data[::2]
test_data = data[1::2]
```

---

## Python 기초 - 제어문

### Q4: for...else의 이해

**질문:**
다음 두 코드의 차이를 설명하고, for...else가 실제로 유용한 사례를 하나 들어주세요.

```python
# 코드 A
def find_even(numbers):
    for num in numbers:
        if num % 2 == 0:
            return num
    return None

# 코드 B
def find_even(numbers):
    for num in numbers:
        if num % 2 == 0:
            return num
    else:
        return None
```

**모범 답안:**
- 두 코드는 동일하게 동작함
- for...else는 break로 중단되지 않고 정상 종료되었을 때 실행됨
- 더 명확한 사용 예시:

```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            print(f"{n}은 {i}로 나눠떨어지므로 소수가 아닙니다")
            return False
    else:
        print(f"{n}은 소수입니다")
        return True
```

**실전 활용:**
```python
# 사용자 검색
for user in users:
    if user['id'] == target_id:
        print(f"찾음: {user}")
        break
else:
    print("사용자를 찾을 수 없습니다")  # break 없이 끝났을 때만 실행
```

---

### Q5: 제너레이터의 메모리 효율성

**질문:**
다음 두 방식의 차이를 설명하고, 각각 언제 사용하는 것이 적절한지 말해주세요.

```python
# 방식 A
def get_large_data():
    return [i for i in range(1_000_000)]

# 방식 B
def get_large_data():
    for i in range(1_000_000):
        yield i

# 사용
for num in get_large_data():
    process(num)
```

**모범 답안:**
- **방식 A (리스트)**:
  - 100만 개를 메모리에 모두 저장 (~8MB)
  - 여러 번 순회 가능
  - 인덱싱 가능 (`data[500000]`)
  - 길이 확인 가능 (`len(data)`)

- **방식 B (제너레이터)**:
  - 한 번에 하나씩만 생성 (~200 bytes)
  - 한 번만 순회 가능 (소진됨)
  - 인덱싱 불가
  - 길이 확인 불가

**사용 시나리오:**
```python
# 리스트 사용: 작은 데이터, 여러 번 사용
users = [get_user(id) for id in range(100)]
print(len(users))
print(users[50])

# 제너레이터 사용: 대용량 데이터, 한 번만 처리
def read_large_file(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

# 10GB 파일도 메모리 문제 없음
for line in read_large_file('huge.txt'):
    process(line)
```

---

### Q6: 리스트 컴프리헨션 vs map/filter

**질문:**
JavaScript의 map/filter와 Python의 리스트 컴프리헨션을 비교하고, Python에서 컴프리헨션이 선호되는 이유를 설명해주세요.

```python
numbers = [1, 2, 3, 4, 5]

# 1. 제곱 수 만들기
squared_comp = [x ** 2 for x in numbers]
squared_map = list(map(lambda x: x ** 2, numbers))

# 2. 짝수만 필터링
evens_comp = [x for x in numbers if x % 2 == 0]
evens_filter = list(filter(lambda x: x % 2 == 0, numbers))

# 3. 짝수의 제곱
result_comp = [x ** 2 for x in numbers if x % 2 == 0]
result_combined = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))
```

**모범 답안:**
- 세 가지 모두 동일한 결과를 생성
- **컴프리헨션이 선호되는 이유:**
  1. **가독성**: 한 줄로 명확하게 표현
  2. **성능**: map/filter보다 약간 빠름
  3. **pythonic**: Python 커뮤니티 표준
  4. **lambda 불필요**: 간단한 연산은 람다 없이 표현 가능

**비교:**
```python
# JS 스타일 (덜 pythonic)
result = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))

# Python 스타일 (pythonic)
result = [x ** 2 for x in numbers if x % 2 == 0]
```

---

## AI/ML 기초 개념

### Q7: 학습 vs 추론의 차이

**질문:**
프론트엔드 개발자로서 AI 프로젝트에 참여했습니다. ML 엔지니어가 "모델 학습은 완료했고, 이제 추론 API를 배포할 거예요"라고 말했습니다. 학습과 추론의 차이를 설명하고, 프론트엔드 개발자가 주로 다루게 되는 것은 무엇인지 말해주세요.

**모범 답안:**

**학습 (Training)**:
- 모델을 만드는 과정 (빌드 타임)
- 대량의 데이터로 패턴 학습
- 시간이 오래 걸림 (몇 시간 ~ 며칠)
- 강력한 GPU 필요
- ML 엔지니어가 담당

**추론 (Inference)**:
- 학습된 모델을 사용하는 과정 (런타임)
- 새로운 데이터에 대해 예측
- 빠름 (밀리초 ~ 초)
- 상대적으로 적은 리소스
- 프론트엔드가 API로 호출

**프론트엔드 비유:**
```javascript
// 학습 = Webpack 빌드
npm run build  // 몇 분 소요, 한 번만 실행

// 추론 = 빌드된 앱 사용
// 사용자가 버튼 클릭 → 즉시 반응 (빠름)
```

**프론트엔드 개발자의 역할:**
- 추론 API 호출 및 결과 표시
- 로딩 상태 처리 (추론은 느릴 수 있음)
- 에러 처리 (모델 응답 실패)
- 사용자 피드백 수집 (모델 개선에 활용)

---

### Q8: 토큰과 비용의 관계

**질문:**
OpenAI API를 사용하는 챗봇 프로젝트에서 다음 두 프롬프트 중 어떤 것이 더 비용 효율적일까요? 그 이유도 함께 설명해주세요.

```python
# 프롬프트 A
prompt_a = """
안녕하세요. 저는 지금 Python 프로그래밍 언어를 공부하고 있는 학생입니다.
Python에 대해서 배우고 있는데요, 리스트와 튜플의 차이점에 대해서 잘 모르겠어서
이렇게 질문을 드립니다. 리스트와 튜플은 어떻게 다른가요?
자세하게 설명해주시면 감사하겠습니다. 제가 초보자라서 쉽게 설명해주세요.
"""

# 프롬프트 B
prompt_b = "Python 리스트와 튜플의 차이를 초보자도 이해할 수 있게 3가지로 요약해줘"
```

**모범 답안:**
- **프롬프트 B가 더 비용 효율적**
- 이유:
  1. **토큰 수 차이**: A는 약 60토큰, B는 약 15토큰 → 4배 차이
  2. **OpenAI는 토큰 수로 과금**: 토큰이 적을수록 저렴
  3. **응답 길이 제한**: "3가지로 요약"으로 출력 토큰도 절약
  4. **명확한 지시**: 불필요한 설명 없이 핵심만 요청

**비용 계산 예시:**
```python
# GPT-3.5-turbo 가격 (2025년 기준)
# 입력: $0.0005 / 1K tokens
# 출력: $0.0015 / 1K tokens

# 프롬프트 A
# 입력 60 토큰 + 출력 200 토큰 = 총 260 토큰
# 비용: (60 * 0.0005 + 200 * 0.0015) / 1000 = $0.00033

# 프롬프트 B
# 입력 15 토큰 + 출력 100 토큰 = 총 115 토큰
# 비용: (15 * 0.0005 + 100 * 0.0015) / 1000 = $0.00016

# 절약: 50% 비용 절감!
```

**프론트엔드에서 고려할 점:**
- 사용자 입력이 너무 길면 경고 표시
- 토큰 카운터 UI 제공
- 간결한 프롬프트 작성 가이드 제공

---

### Q9: 임베딩의 실전 활용

**질문:**
다음은 상품 검색 기능을 구현하는 두 가지 방식입니다. 각 방식의 장단점을 설명하고, 임베딩 검색이 더 유용한 시나리오를 말해주세요.

```python
# 방식 A: 키워드 검색
def search_products_keyword(query, products):
    results = []
    for product in products:
        if query in product['name'] or query in product['description']:
            results.append(product)
    return results

# 방식 B: 임베딩 검색
def search_products_embedding(query, products):
    query_embedding = model.encode(query)

    results = []
    for product in products:
        similarity = cosine_similarity(query_embedding, product['embedding'])
        if similarity > 0.7:
            results.append((product, similarity))

    return sorted(results, key=lambda x: x[1], reverse=True)
```

**모범 답안:**

**키워드 검색 (방식 A):**
- 장점: 간단, 빠름, 정확한 매칭
- 단점: 동의어 못 찾음, 오타 처리 안 됨, 의미 이해 불가

```python
# 검색어: "편안한 신발"
# 찾음: 상품명에 "편안한 신발" 포함된 것만
# 못 찾음: "comfortable shoes", "안락한 운동화" (동의어)
```

**임베딩 검색 (방식 B):**
- 장점: 의미 기반 검색, 동의어 인식, 다국어 지원
- 단점: 초기 설정 복잡, 임베딩 생성 비용

```python
# 검색어: "편안한 신발"
# 찾음: "comfortable shoes", "안락한 운동화", "푹신한 슬리퍼" (의미상 유사)
```

**임베딩이 유용한 시나리오:**
1. **의미 기반 검색**
   ```python
   # 사용자 검색: "아침에 먹기 좋은 음식"
   # 찾아야 할 것: "시리얼", "토스트", "요거트" (키워드 없지만 의미상 관련)
   ```

2. **다국어 검색**
   ```python
   # 한국어 검색: "편안한 의자"
   # 찾음: "comfortable chair", "편안椅子" (영어, 중국어 상품도 검색)
   ```

3. **추천 시스템**
   ```python
   # 사용자가 본 상품: "나이키 런닝화"
   # 추천: "아디다스 조깅화", "운동용 양말" (의미상 관련 상품)
   ```

---

## FastAPI 기초

### Q10: Pydantic의 자동 검증

**질문:**
다음 Pydantic 모델이 있을 때, 각 요청에 대한 FastAPI의 처리 결과를 예측하고 설명해주세요.

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str
    age: int = Field(..., ge=18, le=100)

@app.post("/users")
def create_user(user: UserCreate):
    return user

# 요청 1
{"username": "ab", "email": "test@example.com", "age": 25}

# 요청 2
{"username": "alice", "email": "test@example.com", "age": "25"}

# 요청 3
{"username": "alice", "email": "test@example.com", "age": 15}

# 요청 4
{"username": "alice", "email": "test@example.com"}
```

**모범 답안:**

**요청 1**: ❌ **ValidationError**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "type": "string_too_short"
    }
  ]
}
```
→ username이 최소 3자 미만

**요청 2**: ✅ **성공**
```json
{
  "username": "alice",
  "email": "test@example.com",
  "age": 25
}
```
→ age가 문자열 "25"지만 자동으로 int 25로 변환

**요청 3**: ❌ **ValidationError**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "Input should be greater than or equal to 18",
      "type": "greater_than_equal"
    }
  ]
}
```
→ age가 18 미만

**요청 4**: ❌ **ValidationError**
```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```
→ 필수 필드 age가 누락

**Pydantic의 장점:**
- 자동 타입 검증 및 변환
- 명확한 에러 메시지
- API 문서에 자동 반영
- 개발자가 수동으로 검증 코드 작성 불필요

---

### Q11: Dependency Injection의 이점

**질문:**
다음 두 방식을 비교하고, Dependency Injection이 테스트와 유지보수에 어떻게 도움이 되는지 설명해주세요.

```python
# 방식 A: DI 없이
@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = Database()  # 함수 내부에서 직접 생성
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    return user

# 방식 B: DI 사용
def get_database():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Database = Depends(get_database)):
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    return user
```

**모범 답안:**

**방식 A의 문제점:**
```python
# 1. 테스트 어려움
def test_get_user():
    # 실제 DB가 필요함 (느리고 위험)
    result = get_user(1)
    assert result['name'] == 'Alice'

# 2. DB 변경 어려움
# PostgreSQL → MongoDB로 변경 시
# 모든 엔드포인트 함수를 일일이 수정해야 함

# 3. 연결 관리 어려움
# DB 연결을 닫는 코드를 매번 작성해야 함
```

**방식 B의 장점:**
```python
# 1. 테스트 용이
def test_get_user():
    # Mock DB를 주입할 수 있음
    mock_db = MockDatabase()
    result = get_user(user_id=1, db=mock_db)
    assert result['name'] == 'Alice'

# 2. 유지보수 용이
# DB 변경 시 get_database() 함수만 수정
def get_database():
    db = MongoDB()  # PostgreSQL → MongoDB 변경
    yield db

# 3. 자동 리소스 관리
# try/finally로 자동으로 연결 종료
```

**실전 활용:**
```python
# 인증이 필요한 엔드포인트
def get_current_user(token: str = Depends(get_token)):
    return verify_token(token)

@app.get("/me")
def read_users_me(user: User = Depends(get_current_user)):
    # 모든 인증 로직이 get_current_user에 캡슐화됨
    return user

# 테스트 시 Mock 사용자 주입 가능
def test_read_users_me():
    mock_user = User(id=1, name="Test")
    result = read_users_me(user=mock_user)
    assert result.name == "Test"
```

**DI의 핵심 이점:**
1. **테스트 가능**: Mock 객체 주입 가능
2. **재사용성**: 같은 의존성을 여러 엔드포인트에서 사용
3. **유지보수성**: 의존성 변경 시 한 곳만 수정
4. **관심사 분리**: 비즈니스 로직과 의존성 분리

---

### Q12: FastAPI의 자동 문서화

**질문:**
팀 동료가 "FastAPI는 문서를 자동으로 만들어주니까 따로 API 명세서를 작성할 필요가 없어!"라고 말했습니다. 이 말이 맞는지, 그리고 개발자가 추가로 해야 할 일은 무엇인지 설명해주세요.

**모범 답안:**

**부분적으로 맞음** - FastAPI는 기본적인 문서를 자동 생성하지만, 좋은 문서를 위해서는 추가 작업이 필요합니다.

**자동 생성되는 것:**
```python
@app.post("/users")
def create_user(user: UserCreate):
    return user

# Swagger UI에 자동 표시:
# - 엔드포인트: POST /users
# - 요청 스키마: UserCreate 필드들
# - 응답 스키마: (추론됨)
```

**개발자가 추가해야 할 것:**
```python
@app.post(
    "/users",
    response_model=UserResponse,  # 1. 응답 모델 명시
    status_code=status.HTTP_201_CREATED,  # 2. 상태 코드 명시
    summary="새 사용자 생성",  # 3. 요약
    description="이메일과 비밀번호로 새 사용자를 등록합니다.",  # 4. 설명
    response_description="생성된 사용자 정보",  # 5. 응답 설명
    tags=["users"]  # 6. 카테고리
)
def create_user(user: UserCreate):
    """
    새 사용자를 생성합니다.

    - **username**: 3~20자의 고유한 사용자명
    - **email**: 유효한 이메일 주소
    - **age**: 18세 이상

    등록 후 자동으로 환영 이메일이 발송됩니다.
    """
    return user
```

**Pydantic 모델에 예시 추가:**
```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="사용자명")
    email: str = Field(..., description="이메일 주소")
    age: int = Field(..., ge=18, le=100, description="나이")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "alice",
                "email": "alice@example.com",
                "age": 25
            }
        }
```

**결과:**
- 훨씬 더 명확한 API 문서
- 팀원들이 쉽게 이해
- 프론트엔드 개발자가 바로 사용 가능

**추가 팁:**
```python
# 여러 응답 상태 문서화
@app.get(
    "/users/{user_id}",
    responses={
        200: {"description": "성공", "model": UserResponse},
        404: {"description": "사용자를 찾을 수 없음"},
        500: {"description": "서버 오류"}
    }
)
def get_user(user_id: int):
    pass
```

---

## 종합 시나리오 질문

### Q13: 실전 프로젝트 설계

**질문:**
다음 요구사항을 가진 "할 일 관리 API"를 FastAPI로 구현한다고 가정합니다. 어떤 Pydantic 모델과 엔드포인트가 필요할지 설계해주세요.

**요구사항:**
- 사용자는 할 일을 생성, 조회, 수정, 삭제할 수 있다
- 할 일에는 제목, 설명, 마감일, 우선순위(높음/보통/낮음), 완료 여부가 있다
- 제목은 필수, 나머지는 선택
- 마감일은 과거 날짜 불가
- 완료된 할 일은 수정 불가

**모범 답안:**

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from typing import Optional

# 1. Enum 정의
class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# 2. Base 모델
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="할 일 제목")
    description: Optional[str] = Field(None, max_length=500, description="상세 설명")
    due_date: Optional[datetime] = Field(None, description="마감일")
    priority: Priority = Field(Priority.MEDIUM, description="우선순위")

    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < datetime.now():
            raise ValueError('마감일은 과거 날짜일 수 없습니다')
        return v

# 3. 생성 요청
class TodoCreate(TodoBase):
    pass

# 4. 수정 요청 (모든 필드 선택적)
class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

# 5. 응답
class TodoResponse(TodoBase):
    id: int
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "FastAPI 공부하기",
                "description": "Pydantic 모델 설계 연습",
                "due_date": "2025-12-31T23:59:59",
                "priority": "high",
                "completed": False,
                "created_at": "2025-10-12T10:00:00",
                "updated_at": "2025-10-12T10:00:00"
            }
        }

# 6. 엔드포인트
from fastapi import HTTPException, status

@router.get("/todos", response_model=List[TodoResponse])
def list_todos(
    completed: Optional[bool] = None,
    priority: Optional[Priority] = None,
    db: Dict = Depends(get_db)
):
    """할 일 목록 조회 (필터링 가능)"""
    todos = list(db.values())

    if completed is not None:
        todos = [t for t in todos if t['completed'] == completed]
    if priority is not None:
        todos = [t for t in todos if t['priority'] == priority]

    return todos

@router.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Dict = Depends(get_db)):
    """새 할 일 생성"""
    new_todo = {
        "id": get_next_id(),
        **todo.model_dump(),
        "completed": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    db[new_todo["id"]] = new_todo
    return new_todo

@router.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Dict = Depends(get_db)
):
    """할 일 수정"""
    todo = get_todo_or_404(todo_id, db)

    # 완료된 할 일은 수정 불가
    if todo['completed']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="완료된 할 일은 수정할 수 없습니다"
        )

    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        todo[key] = value

    todo['updated_at'] = datetime.now()
    return todo
```

---

## 보너스: 디버깅 질문

### Q14: 흔한 실수 찾기

**질문:**
다음 코드에는 여러 문제가 있습니다. 문제를 찾아 설명하고 수정해주세요.

```python
# 문제 있는 코드
@app.get("/users/{user_id}")
def get_user(user_id: str):
    users = {1: "Alice", 2: "Bob"}
    return users[user_id]

@app.post("/todos/")
def create_todo(title: str, description: str):
    return {"title": title, "description": description}

@app.get("/search")
def search(query):
    results = search_database(query)
    return results
```

**모범 답안:**

**문제 1: 타입 불일치**
```python
# ❌ 문제
def get_user(user_id: str):  # user_id는 문자열
    users = {1: "Alice", 2: "Bob"}  # 키는 int
    return users[user_id]  # KeyError 발생!

# ✅ 수정
def get_user(user_id: int):  # int로 변경
    users = {1: "Alice", 2: "Bob"}
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, "name": user}
```

**문제 2: Pydantic 모델 미사용**
```python
# ❌ 문제
def create_todo(title: str, description: str):  # 개별 파라미터
    # FastAPI가 이를 query parameter로 인식!
    # POST 요청인데도 request body가 아님
    return {"title": title, "description": description}

# ✅ 수정
class TodoCreate(BaseModel):
    title: str
    description: str

def create_todo(todo: TodoCreate):  # Pydantic 모델 사용
    return todo
```

**문제 3: 타입 힌트 누락**
```python
# ❌ 문제
def search(query):  # 타입 힌트 없음
    results = search_database(query)
    return results

# ✅ 수정
from typing import List

class SearchResult(BaseModel):
    id: int
    title: str
    score: float

def search(
    query: str,  # 타입 명시
    limit: int = 10  # 기본값 제공
) -> List[SearchResult]:  # 반환 타입 명시
    results = search_database(query, limit)
    return results
```

---

이 QnA를 활용하여 학생들의 이해도를 체크하고, 부족한 부분을 파악하여 추가 설명할 수 있습니다!
