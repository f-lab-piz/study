# Python 제어문 - JS 개발자를 위한 가이드

Python의 조건문과 반복문은 JavaScript와 매우 유사하지만, 문법적 차이가 있습니다. 가장 큰 차이는 **중괄호 대신 들여쓰기**를 사용한다는 점입니다.

## 1. 조건문 (Conditionals)

### if, elif, else

```python
# Python
age = 20

if age < 18:
    print("미성년자")
elif age < 65:
    print("성인")
else:
    print("노인")
```

```javascript
// JavaScript
const age = 20;

if (age < 18) {
    console.log("미성년자");
} else if (age < 65) {
    console.log("성인");
} else {
    console.log("노인");
}
```

### 주요 차이점

| 항목 | Python | JavaScript |
|------|--------|------------|
| 중괄호 | 사용 안 함 | `{ }` 필수 |
| 조건문 괄호 | 괄호 선택사항 | `( )` 필요 |
| else if | `elif` | `else if` |
| 들여쓰기 | 문법의 일부 (필수) | 가독성용 (선택) |

### 비교 연산자

```python
# Python
x = 10
y = 20

# 같음/다름
x == y  # False
x != y  # True

# 크기 비교
x < y   # True
x <= y  # True
x > y   # False
x >= y  # False

# 범위 비교 (Python만의 기능!)
15 < x < 25  # False (10은 15보다 작음)
5 < x < 15   # True (10은 5와 15 사이)

# 논리 연산자
x > 5 and y < 30  # True (and, or, not 키워드 사용)
x > 15 or y > 15  # True
not (x > 15)      # True
```

```javascript
// JavaScript
const x = 10;
const y = 20;

// 같음/다름 (엄격한 비교 사용 권장)
x === y  // false
x !== y  // true

// 크기 비교
x < y   // true
x <= y  // true
x > y   // false
x >= y  // false

// 범위 비교 (두 개의 비교 필요)
15 < x && x < 25  // false
5 < x && x < 15   // true

// 논리 연산자 (&&, ||, ! 기호 사용)
x > 5 && y < 30  // true
x > 15 || y > 15  // true
!(x > 15)         // true
```

### Truthy와 Falsy 값

Python과 JavaScript 모두 특정 값들이 조건문에서 자동으로 True/False로 평가됩니다.

```python
# Python의 Falsy 값
if not None:        # True (None은 falsy)
    print("None은 falsy")

if not 0:           # True (0은 falsy)
    print("0은 falsy")

if not "":          # True (빈 문자열은 falsy)
    print("빈 문자열은 falsy")

if not []:          # True (빈 리스트는 falsy)
    print("빈 리스트는 falsy")

if not {}:          # True (빈 딕셔너리는 falsy)
    print("빈 딕셔너리는 falsy")

# Truthy 값
if "hello":         # True
    print("문자열은 truthy")

if [1, 2, 3]:       # True
    print("리스트는 truthy")
```

```javascript
// JavaScript의 Falsy 값
if (!null) {        // true (null은 falsy)
    console.log("null은 falsy");
}

if (!undefined) {   // true (undefined는 falsy)
    console.log("undefined는 falsy");
}

if (!0) {           // true (0은 falsy)
    console.log("0은 falsy");
}

if (!"") {          // true (빈 문자열은 falsy)
    console.log("빈 문자열은 falsy");
}

if (!NaN) {         // true (NaN은 falsy)
    console.log("NaN은 falsy");
}

// 주의: 빈 배열과 객체는 truthy!
if ([]) {           // true (Python과 다름!)
    console.log("빈 배열은 truthy");
}

if ({}) {           // true (Python과 다름!)
    console.log("빈 객체는 truthy");
}
```

### 삼항 연산자

```python
# Python
age = 20
status = "성인" if age >= 18 else "미성년자"
print(status)  # "성인"

# 중첩도 가능하지만 비추천
result = "A" if score >= 90 else "B" if score >= 80 else "C"
```

```javascript
// JavaScript
const age = 20;
const status = age >= 18 ? "성인" : "미성년자";
console.log(status);  // "성인"

// 중첩 (Python보다 더 읽기 쉬움)
const result = score >= 90 ? "A" : score >= 80 ? "B" : "C";
```

### match-case (Python 3.10+) - JS의 switch

```python
# Python 3.10+
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Internal Server Error"
        case _:  # default (와일드카드)
            return "Unknown"

# 패턴 매칭 (더 강력한 기능)
def process_command(command):
    match command.split():
        case ["quit"]:
            return "Goodbye!"
        case ["load", filename]:
            return f"Loading {filename}"
        case ["save", filename]:
            return f"Saving {filename}"
        case _:
            return "Unknown command"
```

```javascript
// JavaScript
function httpStatus(status) {
    switch (status) {
        case 200:
            return "OK";
        case 404:
            return "Not Found";
        case 500:
            return "Internal Server Error";
        default:
            return "Unknown";
    }
}

// JavaScript는 패턴 매칭이 없음
function processCommand(command) {
    const parts = command.split(' ');

    if (parts[0] === "quit") {
        return "Goodbye!";
    } else if (parts[0] === "load" && parts[1]) {
        return `Loading ${parts[1]}`;
    } else if (parts[0] === "save" && parts[1]) {
        return `Saving ${parts[1]}`;
    } else {
        return "Unknown command";
    }
}
```

## 2. 반복문 (Loops)

### for 문 - 컬렉션 순회

Python의 for 문은 JavaScript의 `for...of`와 유사합니다.

```python
# Python - 리스트 순회
fruits = ['apple', 'banana', 'cherry']

for fruit in fruits:
    print(fruit)

# 인덱스와 함께 순회 (enumerate)
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry

# 딕셔너리 순회
user = {'name': 'Alice', 'age': 30, 'city': 'Seoul'}

# 키만
for key in user:
    print(key)

# 키와 값
for key, value in user.items():
    print(f"{key}: {value}")
# name: Alice
# age: 30
# city: Seoul
```

```javascript
// JavaScript - 배열 순회
const fruits = ['apple', 'banana', 'cherry'];

// for...of
for (const fruit of fruits) {
    console.log(fruit);
}

// entries()로 인덱스와 함께
for (const [index, fruit] of fruits.entries()) {
    console.log(`${index}: ${fruit}`);
}

// 객체 순회
const user = {name: 'Alice', age: 30, city: 'Seoul'};

// 키만
for (const key in user) {
    console.log(key);
}

// 키와 값
for (const [key, value] of Object.entries(user)) {
    console.log(`${key}: ${value}`);
}
```

### range() - 숫자 범위 반복

```python
# Python
# 0부터 4까지
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# 1부터 5까지
for i in range(1, 6):
    print(i)  # 1, 2, 3, 4, 5

# 0부터 10까지 2씩 증가
for i in range(0, 11, 2):
    print(i)  # 0, 2, 4, 6, 8, 10

# 역순
for i in range(5, 0, -1):
    print(i)  # 5, 4, 3, 2, 1
```

```javascript
// JavaScript - 전통적인 for 문 사용
// 0부터 4까지
for (let i = 0; i < 5; i++) {
    console.log(i);  // 0, 1, 2, 3, 4
}

// 1부터 5까지
for (let i = 1; i <= 5; i++) {
    console.log(i);  // 1, 2, 3, 4, 5
}

// 0부터 10까지 2씩 증가
for (let i = 0; i <= 10; i += 2) {
    console.log(i);  // 0, 2, 4, 6, 8, 10
}

// 역순
for (let i = 5; i > 0; i--) {
    console.log(i);  // 5, 4, 3, 2, 1
}
```

### while 문

```python
# Python
count = 0
while count < 5:
    print(count)
    count += 1

# 무한 루프
while True:
    user_input = input("Enter 'quit' to exit: ")
    if user_input == 'quit':
        break
    print(f"You entered: {user_input}")
```

```javascript
// JavaScript
let count = 0;
while (count < 5) {
    console.log(count);
    count++;
}

// 무한 루프
while (true) {
    const userInput = prompt("Enter 'quit' to exit:");
    if (userInput === 'quit') {
        break;
    }
    console.log(`You entered: ${userInput}`);
}
```

### break, continue, else

```python
# Python
# break: 루프 종료
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: 다음 반복으로
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0, 1, 3, 4

# else: break 없이 정상 종료되면 실행 (Python만의 기능!)
for i in range(5):
    if i == 10:  # 이 조건은 거짓
        break
else:
    print("루프가 정상적으로 완료됨")
# 출력: "루프가 정상적으로 완료됨"

# break가 실행되면 else는 실행 안 됨
for i in range(5):
    if i == 3:
        break
else:
    print("이 메시지는 출력 안 됨")
```

```javascript
// JavaScript
// break: 루프 종료
for (let i = 0; i < 10; i++) {
    if (i === 5) {
        break;
    }
    console.log(i);  // 0, 1, 2, 3, 4
}

// continue: 다음 반복으로
for (let i = 0; i < 5; i++) {
    if (i === 2) {
        continue;
    }
    console.log(i);  // 0, 1, 3, 4
}

// JavaScript에는 for...else가 없음
// 플래그 변수로 구현 가능
let completed = true;
for (let i = 0; i < 5; i++) {
    if (i === 3) {
        completed = false;
        break;
    }
}
if (completed) {
    console.log("루프가 정상적으로 완료됨");
}
```

### 실용적인 for...else 사용 예시

```python
# Python - 검색 작업에 유용
def find_user(users, target_name):
    for user in users:
        if user['name'] == target_name:
            print(f"Found: {user}")
            break
    else:
        print(f"User {target_name} not found")

users = [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25}
]

find_user(users, 'Charlie')  # User Charlie not found

# 소수 판별
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    else:
        return True  # 루프를 끝까지 돌았으면 소수

print(is_prime(17))  # True
print(is_prime(18))  # False
```

## 3. 리스트 컴프리헨션 vs 반복문

많은 경우, 반복문 대신 컴프리헨션을 사용하면 더 간결합니다.

```python
# Python - 일반 for 문
squares = []
for i in range(10):
    squares.append(i ** 2)

# 리스트 컴프리헨션 (더 pythonic!)
squares = [i ** 2 for i in range(10)]

# 조건 포함
evens = [i for i in range(20) if i % 2 == 0]

# 중첩 루프
matrix = [[i * j for j in range(3)] for i in range(3)]
# [[0, 0, 0], [0, 1, 2], [0, 2, 4]]
```

```javascript
// JavaScript - map과 filter
const squares = Array.from({length: 10}, (_, i) => i ** 2);
// 또는
const squares2 = [...Array(10)].map((_, i) => i ** 2);

// 조건 포함
const evens = [...Array(20)].map((_, i) => i).filter(i => i % 2 === 0);

// 중첩 루프
const matrix = Array.from({length: 3}, (_, i) =>
    Array.from({length: 3}, (_, j) => i * j)
);
```

## 4. 고급 반복 패턴

### zip() - 여러 리스트 동시 순회

```python
# Python
names = ['Alice', 'Bob', 'Charlie']
scores = [85, 92, 78]
grades = ['B', 'A', 'C']

for name, score, grade in zip(names, scores, grades):
    print(f"{name}: {score} ({grade})")
# Alice: 85 (B)
# Bob: 92 (A)
# Charlie: 78 (C)
```

```javascript
// JavaScript - 직접 구현 필요
const names = ['Alice', 'Bob', 'Charlie'];
const scores = [85, 92, 78];
const grades = ['B', 'A', 'C'];

for (let i = 0; i < names.length; i++) {
    console.log(`${names[i]}: ${scores[i]} (${grades[i]})`);
}

// 또는 map 사용
names.forEach((name, i) => {
    console.log(`${name}: ${scores[i]} (${grades[i]})`);
});
```

### 딕셔너리/객체 변환

```python
# Python - zip으로 딕셔너리 생성
keys = ['name', 'age', 'city']
values = ['Alice', 30, 'Seoul']
user = dict(zip(keys, values))
print(user)  # {'name': 'Alice', 'age': 30, 'city': 'Seoul'}
```

```javascript
// JavaScript
const keys = ['name', 'age', 'city'];
const values = ['Alice', 30, 'Seoul'];
const user = Object.fromEntries(
    keys.map((key, i) => [key, values[i]])
);
console.log(user);  // {name: 'Alice', age: 30, city: 'Seoul'}
```

## 5. 제너레이터 (Generator)

제너레이터는 **메모리 효율적으로 값을 하나씩 생성**하는 특별한 이터레이터입니다. JavaScript의 Generator와 유사하지만 Python에서 더 자주 사용됩니다.

### 일반 함수 vs 제너레이터 함수

```python
# Python - 일반 함수
def get_numbers():
    """모든 값을 메모리에 저장"""
    result = []
    for i in range(5):
        result.append(i)
    return result  # [0, 1, 2, 3, 4]

numbers = get_numbers()  # 메모리에 전체 리스트 생성
print(numbers)

# Python - 제너레이터 함수
def generate_numbers():
    """값을 하나씩 생성 (yield 사용)"""
    for i in range(5):
        yield i  # 값을 하나씩 반환

numbers = generate_numbers()  # 제너레이터 객체 생성 (메모리 적게 사용)
print(numbers)  # <generator object generate_numbers at 0x...>

# 값을 하나씩 가져오기
for num in numbers:
    print(num)  # 0, 1, 2, 3, 4
```

```javascript
// JavaScript - 제너레이터 (ES6+)
function* generateNumbers() {
    for (let i = 0; i < 5; i++) {
        yield i;
    }
}

const numbers = generateNumbers();
console.log(numbers);  // Object [Generator] {}

// 값을 하나씩 가져오기
for (const num of numbers) {
    console.log(num);  // 0, 1, 2, 3, 4
}

// 또는 next() 사용
const gen = generateNumbers();
console.log(gen.next());  // {value: 0, done: false}
console.log(gen.next());  // {value: 1, done: false}
```

### 왜 제너레이터를 사용할까?

```python
# ❌ 나쁜 예: 메모리 낭비
def get_large_data():
    """100만 개의 숫자를 메모리에 모두 저장"""
    return [i for i in range(1_000_000)]

data = get_large_data()  # 메모리 ~8MB 사용
for num in data:
    print(num)

# ✅ 좋은 예: 메모리 효율적
def generate_large_data():
    """100만 개의 숫자를 하나씩 생성"""
    for i in range(1_000_000):
        yield i

data = generate_large_data()  # 메모리 거의 사용 안 함
for num in data:
    print(num)  # 필요할 때만 생성
```

**메모리 비교**:
- 일반 리스트: 100만 개 → 약 8MB
- 제너레이터: 상수 메모리 (~200 bytes)

### 제너레이터의 실전 활용

```python
# 1. 큰 파일 읽기
def read_large_file(file_path):
    """파일을 한 줄씩 읽기 (메모리 효율적)"""
    with open(file_path, 'r') as file:
        for line in file:
            yield line.strip()

# 10GB 파일도 메모리 부담 없이 처리 가능
for line in read_large_file('huge_file.txt'):
    process_line(line)

# 2. 무한 시퀀스 생성
def infinite_counter(start=0):
    """무한히 숫자를 생성"""
    num = start
    while True:
        yield num
        num += 1

counter = infinite_counter(1)
print(next(counter))  # 1
print(next(counter))  # 2
print(next(counter))  # 3

# 3. 피보나치 수열
def fibonacci():
    """피보나치 수열을 무한히 생성"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
for i in range(10):
    print(next(fib))  # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

# 4. 데이터 파이프라인
def read_data(file_path):
    """데이터 읽기"""
    with open(file_path) as f:
        for line in f:
            yield line

def parse_data(lines):
    """데이터 파싱"""
    for line in lines:
        yield line.split(',')

def filter_data(rows):
    """데이터 필터링"""
    for row in rows:
        if len(row) > 2:
            yield row

# 제너레이터 체이닝 (메모리 효율적인 파이프라인)
pipeline = filter_data(parse_data(read_data('data.csv')))
for row in pipeline:
    print(row)
```

### 제너레이터 표현식 (Generator Expression)

리스트 컴프리헨션과 비슷하지만 `[]` 대신 `()`를 사용합니다.

```python
# 리스트 컴프리헨션 (메모리 많이 사용)
squares_list = [i ** 2 for i in range(1_000_000)]
print(type(squares_list))  # <class 'list'>
print(squares_list[0])     # 0

# 제너레이터 표현식 (메모리 적게 사용)
squares_gen = (i ** 2 for i in range(1_000_000))
print(type(squares_gen))   # <class 'generator'>
print(next(squares_gen))   # 0
print(next(squares_gen))   # 1

# 합계 계산 (제너레이터가 더 효율적)
total = sum(i ** 2 for i in range(1_000_000))
```

```javascript
// JavaScript는 제너레이터 표현식이 없음
// 제너레이터 함수를 직접 작성해야 함
function* squaresGenerator() {
    for (let i = 0; i < 1000000; i++) {
        yield i ** 2;
    }
}

const squares = squaresGenerator();
console.log(squares.next().value);  // 0
console.log(squares.next().value);  // 1
```

### next()와 send()

```python
# next()로 값 가져오기
def simple_gen():
    yield 1
    yield 2
    yield 3

gen = simple_gen()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
# print(next(gen))  # StopIteration 에러!

# send()로 값 전달하기
def echo_gen():
    """제너레이터에 값을 전달받을 수 있음"""
    while True:
        received = yield  # 값을 받음
        print(f"Received: {received}")

gen = echo_gen()
next(gen)  # 제너레이터 시작 (필수!)
gen.send("Hello")  # Received: Hello
gen.send("World")  # Received: World

# 양방향 통신
def counter_gen():
    count = 0
    while True:
        increment = yield count
        if increment is not None:
            count += increment
        else:
            count += 1

counter = counter_gen()
print(next(counter))       # 0
print(counter.send(5))     # 5 (0 + 5)
print(next(counter))       # 6 (5 + 1)
print(counter.send(10))    # 16 (6 + 10)
```

```javascript
// JavaScript도 유사하게 동작
function* counterGen() {
    let count = 0;
    while (true) {
        const increment = yield count;
        if (increment !== undefined) {
            count += increment;
        } else {
            count += 1;
        }
    }
}

const counter = counterGen();
console.log(counter.next().value);      // 0
console.log(counter.next(5).value);     // 5
console.log(counter.next().value);      // 6
console.log(counter.next(10).value);    // 16
```

### 제너레이터 vs 리스트 선택 가이드

```python
# 리스트를 사용해야 할 때
numbers = [1, 2, 3, 4, 5]

# ✓ 여러 번 순회해야 할 때
for num in numbers:
    print(num)
for num in numbers:  # 다시 순회 가능
    print(num)

# ✓ 인덱싱이 필요할 때
print(numbers[2])  # 3

# ✓ 길이를 알아야 할 때
print(len(numbers))  # 5

# 제너레이터를 사용해야 할 때
def gen_numbers():
    for i in range(1, 6):
        yield i

numbers_gen = gen_numbers()

# ✓ 한 번만 순회할 때
for num in numbers_gen:
    print(num)
# for num in numbers_gen:  # 두 번째 순회 불가! (제너레이터 소진됨)

# ✓ 메모리가 중요할 때 (대용량 데이터)
# ✓ 무한 시퀀스를 다룰 때
# ✓ 느리게 계산되는 값들을 다룰 때 (lazy evaluation)

# ✗ 인덱싱 불가
# print(numbers_gen[2])  # TypeError!

# ✗ 길이 확인 불가
# print(len(numbers_gen))  # TypeError!
```

### 실전 예시: API 페이지네이션

```python
# API에서 페이지별로 데이터 가져오기
def fetch_all_users(api_url):
    """모든 사용자를 페이지별로 가져오기"""
    page = 1
    while True:
        response = requests.get(f"{api_url}?page={page}")
        data = response.json()

        if not data['users']:
            break  # 더 이상 데이터 없음

        for user in data['users']:
            yield user  # 사용자 하나씩 반환

        page += 1

# 메모리 효율적으로 처리
for user in fetch_all_users('https://api.example.com/users'):
    process_user(user)
    # 100만 명의 사용자가 있어도 메모리는 일정하게 유지
```

```javascript
// JavaScript 비동기 제너레이터 (ES2018+)
async function* fetchAllUsers(apiUrl) {
    let page = 1;
    while (true) {
        const response = await fetch(`${apiUrl}?page=${page}`);
        const data = await response.json();

        if (!data.users || data.users.length === 0) {
            break;
        }

        for (const user of data.users) {
            yield user;
        }

        page++;
    }
}

// 사용
for await (const user of fetchAllUsers('https://api.example.com/users')) {
    processUser(user);
}
```

## 요약: 핵심 차이점

### 문법
- **Python**: 들여쓰기가 문법, 콜론(`:`) 필수, 중괄호 없음
- **JavaScript**: 중괄호와 세미콜론, 들여쓰기는 가독성용

### 조건문
- **Python**: `elif`, `and/or/not`, `if...else` 표현식
- **JavaScript**: `else if`, `&&/||/!`, 삼항 연산자

### 반복문
- **Python**: `for...in`으로 모든 iterable 순회, `range()`, `for...else`
- **JavaScript**: `for...of`와 `for...in`, 전통적 for 문

### 제너레이터
- **Python**: `yield` 키워드, 제너레이터 표현식 `()`
- **JavaScript**: `function*` 문법, `yield` 키워드

### 권장 스타일
- **Python**: 컴프리헨션 선호, `enumerate()`, `zip()` 활용, 대용량 데이터는 제너레이터
- **JavaScript**: `map/filter/reduce`, `forEach()` 활용

Python은 "코드는 읽히기 위해 쓰여진다"는 철학을 가지고 있어, 더 명시적이고 읽기 쉬운 코드를 지향합니다!
