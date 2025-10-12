# Python 자료구조 - JS 개발자를 위한 가이드

JavaScript를 사용해본 경험이 있다면, Python의 자료구조들이 익숙하게 느껴질 것입니다. 하지만 미묘한 차이점들이 있으니 주의깊게 살펴보세요.

## 1. 리스트 (List) - JS의 Array

Python의 리스트는 JavaScript의 배열과 거의 동일한 개념입니다.

### 기본 사용법

```python
# Python
fruits = ['apple', 'banana', 'cherry']
numbers = [1, 2, 3, 4, 5]
mixed = [1, 'hello', True, 3.14]  # 여러 타입 혼용 가능
```

```javascript
// JavaScript
const fruits = ['apple', 'banana', 'cherry'];
const numbers = [1, 2, 3, 4, 5];
const mixed = [1, 'hello', true, 3.14];
```

### 주요 메서드 비교

| 작업 | Python | JavaScript |
|------|--------|------------|
| 추가 | `fruits.append('orange')` | `fruits.push('orange')` |
| 특정 위치 삽입 | `fruits.insert(1, 'mango')` | `fruits.splice(1, 0, 'mango')` |
| 삭제 (값으로) | `fruits.remove('banana')` | `fruits.splice(fruits.indexOf('banana'), 1)` |
| 삭제 (인덱스로) | `fruits.pop(1)` | `fruits.splice(1, 1)` |
| 길이 | `len(fruits)` | `fruits.length` |
| 슬라이싱 | `fruits[1:3]` | `fruits.slice(1, 3)` |

### Python만의 강력한 기능: 슬라이싱

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 인덱스 2부터 5 이전까지
print(numbers[2:5])  # [2, 3, 4]

# 처음부터 4 이전까지
print(numbers[:4])  # [0, 1, 2, 3]

# 5부터 끝까지
print(numbers[5:])  # [5, 6, 7, 8, 9]

# 역순
print(numbers[::-1])  # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

# 2칸씩 건너뛰기
print(numbers[::2])  # [0, 2, 4, 6, 8]
```

JavaScript에서는 이런 작업을 위해 여러 메서드를 조합해야 합니다.

### 리스트 컴프리헨션 (List Comprehension)

Python만의 강력한 기능으로, JS의 map, filter를 더 간결하게 표현할 수 있습니다.

```python
# Python - 리스트 컴프리헨션
numbers = [1, 2, 3, 4, 5]
squared = [x ** 2 for x in numbers]
print(squared)  # [1, 4, 9, 16, 25]

# 조건 포함
evens = [x for x in numbers if x % 2 == 0]
print(evens)  # [2, 4]
```

```javascript
// JavaScript - map과 filter
const numbers = [1, 2, 3, 4, 5];
const squared = numbers.map(x => x ** 2);
console.log(squared);  // [1, 4, 9, 16, 25]

const evens = numbers.filter(x => x % 2 === 0);
console.log(evens);  // [2, 4]
```

## 2. 튜플 (Tuple) - JS에는 없는 개념

튜플은 **불변(immutable)** 리스트입니다. 한번 생성하면 수정할 수 없습니다.

### 왜 튜플을 사용할까?

- **데이터 보호**: 실수로 데이터를 변경하는 것을 방지
- **성능**: 리스트보다 메모리 효율적
- **딕셔너리 키로 사용 가능**: 불변 객체만 키가 될 수 있음
- **다중 반환값**: 함수에서 여러 값을 반환할 때 유용

### 기본 사용법

```python
# 튜플 생성
coordinates = (10, 20)
rgb = (255, 128, 0)
single = (42,)  # 요소가 하나일 때는 쉼표 필수!

# 접근은 리스트와 동일
print(coordinates[0])  # 10

# 하지만 수정은 불가능
# coordinates[0] = 30  # TypeError!

# 튜플 언패킹 (destructuring)
x, y = coordinates
print(x, y)  # 10 20
```

```javascript
// JavaScript - 유사한 패턴 (하지만 불변성은 없음)
const coordinates = [10, 20];  // Object.freeze()로 불변 가능
const [x, y] = coordinates;  // destructuring
console.log(x, y);  // 10 20

// 또는 const로 재할당 방지
const rgb = [255, 128, 0];
// rgb = [0, 0, 0];  // Error!
// rgb[0] = 0;  // 하지만 이건 가능 (Python 튜플과 다른 점)
```

### 튜플의 실제 사용 예시

```python
# 함수에서 여러 값 반환
def get_user_info():
    name = "Alice"
    age = 30
    city = "Seoul"
    return (name, age, city)  # 튜플 반환

# 언패킹으로 받기
name, age, city = get_user_info()

# 좌표 데이터
point = (100, 200)
positions = [(0, 0), (10, 20), (30, 40)]

# 딕셔너리의 키로 사용 (리스트는 불가능)
locations = {
    (0, 0): "origin",
    (10, 20): "point A",
    (30, 40): "point B"
}
```

## 3. 딕셔너리 (Dictionary) - JS의 Object

Python의 딕셔너리는 JavaScript의 객체 및 Map과 유사합니다.

### 기본 사용법

```python
# Python
user = {
    'name': 'Alice',
    'age': 30,
    'city': 'Seoul'
}

# 접근
print(user['name'])  # 'Alice'
print(user.get('name'))  # 'Alice' (더 안전)
print(user.get('email', 'N/A'))  # 없으면 기본값 반환

# 추가/수정
user['email'] = 'alice@example.com'

# 삭제
del user['age']
```

```javascript
// JavaScript
const user = {
    name: 'Alice',
    age: 30,
    city: 'Seoul'
};

// 접근
console.log(user.name);  // 'Alice'
console.log(user['name']);  // 'Alice'

// 추가/수정
user.email = 'alice@example.com';

// 삭제
delete user.age;
```

### 주요 메서드 비교

```python
# Python
user = {'name': 'Alice', 'age': 30}

# 모든 키
user.keys()  # dict_keys(['name', 'age'])

# 모든 값
user.values()  # dict_values(['Alice', 30])

# 키-값 쌍
user.items()  # dict_items([('name', 'Alice'), ('age', 30)])

# 키 존재 확인
'name' in user  # True

# 병합 (Python 3.9+)
defaults = {'theme': 'dark', 'language': 'ko'}
combined = user | defaults
```

```javascript
// JavaScript
const user = {name: 'Alice', age: 30};

// 모든 키
Object.keys(user);  // ['name', 'age']

// 모든 값
Object.values(user);  // ['Alice', 30]

// 키-값 쌍
Object.entries(user);  // [['name', 'Alice'], ['age', 30]]

// 키 존재 확인
'name' in user;  // true

// 병합
const defaults = {theme: 'dark', language: 'ko'};
const combined = {...user, ...defaults};
```

### 딕셔너리 컴프리헨션

```python
# Python
numbers = [1, 2, 3, 4, 5]
squared_dict = {x: x**2 for x in numbers}
print(squared_dict)  # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# 조건 포함
even_squared = {x: x**2 for x in numbers if x % 2 == 0}
print(even_squared)  # {2: 4, 4: 16}
```

```javascript
// JavaScript
const numbers = [1, 2, 3, 4, 5];
const squaredDict = Object.fromEntries(
    numbers.map(x => [x, x**2])
);
console.log(squaredDict);  // {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

const evenSquared = Object.fromEntries(
    numbers.filter(x => x % 2 === 0).map(x => [x, x**2])
);
console.log(evenSquared);  // {2: 4, 4: 16}
```

## 중요한 차이점 정리

### 1. 인덱싱

```python
# Python: 대괄호만 사용
user['name']  # OK
# user.name  # AttributeError (일반 딕셔너리에서는 안됨)
```

```javascript
// JavaScript: 둘 다 가능
user['name']  // OK
user.name     // OK
```

### 2. 키 타입

```python
# Python: 불변 객체만 키로 사용 가능
data = {
    'string_key': 1,
    42: 'number key',
    (1, 2): 'tuple key',  # OK
    # [1, 2]: 'list key'  # TypeError! (리스트는 불가)
}
```

```javascript
// JavaScript: 문자열과 Symbol만 키로 사용 (숫자는 문자열로 변환)
const data = {
    'string_key': 1,
    42: 'number key',  // '42'로 변환됨
};
```

### 3. 순서 보장

```python
# Python 3.7+: 딕셔너리는 삽입 순서를 보장
user = {'name': 'Alice', 'age': 30, 'city': 'Seoul'}
# 항상 name -> age -> city 순서
```

```javascript
// JavaScript: 객체도 대부분 순서를 유지하지만 보장되지 않음
// Map을 사용하면 확실히 순서 보장
const user = new Map([
    ['name', 'Alice'],
    ['age', 30],
    ['city', 'Seoul']
]);
```

## 실전 예시: 데이터 처리

```python
# Python
students = [
    {'name': 'Alice', 'score': 85},
    {'name': 'Bob', 'score': 92},
    {'name': 'Charlie', 'score': 78}
]

# 80점 이상인 학생들의 이름
high_scorers = [s['name'] for s in students if s['score'] >= 80]
print(high_scorers)  # ['Alice', 'Bob']

# 점수로 정렬
sorted_students = sorted(students, key=lambda s: s['score'], reverse=True)
```

```javascript
// JavaScript
const students = [
    {name: 'Alice', score: 85},
    {name: 'Bob', score: 92},
    {name: 'Charlie', score: 78}
];

// 80점 이상인 학생들의 이름
const highScorers = students
    .filter(s => s.score >= 80)
    .map(s => s.name);
console.log(highScorers);  // ['Alice', 'Bob']

// 점수로 정렬
const sortedStudents = [...students].sort((a, b) => b.score - a.score);
```

## 요약

- **리스트**: JS의 Array와 거의 동일하지만, 슬라이싱과 컴프리헨션이 강력
- **튜플**: JS에 없는 불변 리스트, 데이터 보호와 성능에 유리
- **딕셔너리**: JS의 Object/Map과 유사하지만, 키 타입 제한이 있고 순서가 보장됨

Python은 간결하고 읽기 쉬운 문법을 지향하므로, JS보다 더 직관적으로 느껴질 것입니다!
