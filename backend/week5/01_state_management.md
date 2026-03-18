# 01. 상태 관리

## 실행 예시

```bash
cd /Users/kihoon/Desktop/git/study/backend/week5
uv run python main.py
```

출력 중 `1. 상태 관리 예제` 부분을 보면 된다.

## 상태란?

상태는 **"지금 이 데이터가 어떤 단계에 있는가"** 를 나타내는 값이다.

물류 서비스에서는 거의 모든 것이 상태를 가진다.

예:

- 출고 요청 상태
- 작업지시 상태
- 주문 상태
- 재고 상태

---

## 왜 상태가 중요한가?

CRUD만 생각하면 데이터를 만들고, 읽고, 수정하고, 지우는 것만 보인다.

하지만 실제 서비스에서는 "수정"보다 더 중요한 질문이 있다.

> 지금 이 데이터가 어떤 흐름 위에 있는가?

예를 들어 출고 요청은 아래처럼 바뀔 수 있다.

```text
requested -> allocated -> in_progress -> completed
```

이렇게 상태를 두면 좋은 점:

- 현재 진행 상황을 알 수 있다
- 잘못된 변경을 막을 수 있다
- 화면에 보여줄 정보가 명확해진다
- 테스트가 쉬워진다

---

## 상태가 없으면 생기는 문제

예를 들어 `OutboundRequest` 에 상태가 없다고 생각해보자.

그러면 아래 질문에 답하기 어려워진다.

- 이 요청은 아직 시작 전인가?
- 재고가 이미 할당됐는가?
- 작업이 진행 중인가?
- 완료된 요청인가?
- 실패한 요청인가?

즉, **데이터는 있는데 흐름이 보이지 않는다.**

---

## 상태 관리의 핵심

상태 관리에서 중요한 것은 두 가지다.

1. 어떤 상태가 필요한가
2. 어떤 상태 전이만 허용할 것인가

### 상태 예시

```text
requested
allocated
in_progress
completed
failed
```

### 상태 전이 예시

```text
requested -> allocated
allocated -> in_progress
in_progress -> completed
requested -> failed
allocated -> failed
```

---

## 잘못된 상태 전이

아래 같은 전이는 막아야 한다.

```text
completed -> in_progress
failed -> allocated
completed -> requested
```

왜 막아야 할까?

- 완료된 작업이 다시 진행 중이 되면 기록이 꼬인다
- 실패한 요청이 갑자기 중간 상태로 점프하면 흐름을 추적하기 어렵다
- 운영자가 상태를 믿을 수 없게 된다

---

## 물류 예시로 보기

### 예시 1. 출고 요청

```text
requested -> allocated -> completed
              |
              -> failed
```

설명:

- `requested`: 출고 요청이 등록됨
- `allocated`: 재고 확인 후 처리 가능
- `completed`: 작업 완료
- `failed`: 재고 부족 또는 처리 실패

### 예시 2. 피킹 작업지시

```text
ready -> in_progress -> completed
```

설명:

- `ready`: 작업 시작 전
- `in_progress`: 작업 중
- `completed`: 작업 종료

---

## 상태 관리는 API 설계에도 연결된다

상태가 있으면 어떤 API가 필요한지도 보인다.

예:

```http
POST /outbound-requests
POST /picking-tasks
PATCH /picking-tasks/{id}/status
```

왜 `PATCH /status` 가 필요한가?

상태는 전체 데이터를 덮어쓰는 것이 아니라  
흐름의 특정 단계만 변경하는 일이 많기 때문이다.

---

## 상태 관리는 테스트에도 연결된다

테스트는 상태 전이를 기준으로 잡으면 쉽다.

예:

- `requested` 인 요청은 `allocated` 로 바뀔 수 있다
- `completed` 된 작업은 다시 `in_progress` 가 되면 안 된다
- 재고 부족이면 `allocated` 로 가지 않고 `failed` 가 되어야 한다

즉, 상태를 정하면 테스트 케이스도 자연스럽게 나온다.

---

## 상태 관리와 락

락이 필요한 이유도 상태 변경 시점에서 보인다.

예:

- 두 요청이 동시에 같은 재고를 잡으려 한다
- 둘 다 `requested -> allocated` 로 바꾸려 한다

이 순간 충돌이 생길 수 있다.

즉, 락은 추상적인 개념이 아니라  
**상태를 안전하게 바꾸기 위해 필요한 도구**라고 볼 수 있다.

---

## 정리

- 상태는 데이터의 현재 단계를 표현한다
- 상태가 있어야 서비스 흐름이 보인다
- 상태 전이는 제한해야 한다
- 상태 관리는 API, 테스트, 락과 연결된다

---

## 직접 해보기

아래를 채워보자.

### 1. 내 프로젝트에서 상태가 필요한 데이터 2개

```text
1.
2.
```

### 2. 각 데이터의 상태값

```text

```

### 3. 절대 허용하면 안 되는 상태 전이 2개

```text
1.
2.
```
