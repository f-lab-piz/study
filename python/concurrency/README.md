# Python 동시성과 병렬성 학습 가이드

> **대상**: JavaScript/프론트엔드 개발자 → Python/백엔드 전환

## 목차
1. [동시성 vs 병렬성](#동시성-vs-병렬성)
2. [JavaScript와 Python 비교](#javascript와-python-비교)
3. [Python의 동시성 모델](#python의-동시성-모델)
4. [Threading (스레드)](#threading-스레드)
5. [Multiprocessing (멀티프로세싱)](#multiprocessing-멀티프로세싱)
6. [AsyncIO (비동기)](#asyncio-비동기)
7. [어떤 방식을 선택할까?](#어떤-방식을-선택할까)
8. [실습 파일](#실습-파일)

---

## 동시성 vs 병렬성

### 개념 이해

```
동시성 (Concurrency)
- 여러 작업을 번갈아가며 처리
- "동시에 처리하는 것처럼 보임"
- 싱글 코어에서도 가능

  Task A: ━━━  ━━━  ━━━
  Task B:    ━━━  ━━━  ━━━
           ────────────────→ 시간
           (하나의 CPU가 번갈아 처리)

병렬성 (Parallelism)
- 여러 작업을 실제로 동시에 처리
- "진짜 동시 처리"
- 멀티 코어 필요

  Task A: ━━━━━━━━━━━━━
  Task B: ━━━━━━━━━━━━━
           ────────────────→ 시간
           (여러 CPU가 동시 처리)
```

### 실생활 비유

```
🍕 피자 가게 예시

동시성 (1명의 주방장):
- 피자 A 도우 만들기
- 피자 A 오븐에 넣기
- (오븐 돌아가는 동안) 피자 B 도우 만들기
- 피자 A 오븐에서 꺼내기
- 피자 B 오븐에 넣기
→ 한 사람이 여러 일을 번갈아 처리

병렬성 (3명의 주방장):
- 주방장1: 피자 A 만들기
- 주방장2: 피자 B 만들기
- 주방장3: 피자 C 만들기
→ 여러 사람이 동시에 각자 일 처리
```

---

## JavaScript와 Python 비교

### JavaScript (Node.js)

```javascript
// JavaScript는 기본적으로 단일 스레드 + 이벤트 루프

// ✅ 비동기 (Promise/async-await)
async function fetchData() {
    const response = await fetch('https://api.example.com');
    const data = await response.json();
    return data;
}

// Node.js의 동시성 모델:
// - 싱글 스레드 이벤트 루프
// - 논블로킹 I/O
// - 콜백/Promise 기반
```

**JavaScript 개발자에게 익숙한 점:**
- `async/await` 문법
- Promise 체이닝
- 이벤트 기반 프로그래밍

### Python

```python
# Python은 여러 방식 제공

# 1️⃣ AsyncIO (JavaScript와 가장 유사!)
async def fetch_data():
    response = await aiohttp.get('https://api.example.com')
    data = await response.json()
    return data

# 2️⃣ Threading (멀티 스레딩)
import threading
def fetch_data():
    # ...

thread = threading.Thread(target=fetch_data)
thread.start()

# 3️⃣ Multiprocessing (멀티 프로세싱)
import multiprocessing
def heavy_computation():
    # ...

process = multiprocessing.Process(target=heavy_computation)
process.start()
```

### 주요 차이점

| 특성 | JavaScript (Node.js) | Python |
|------|---------------------|---------|
| 기본 모델 | 싱글 스레드 | 멀티 스레드 지원 |
| 동시성 | 이벤트 루프 (기본) | Threading/AsyncIO |
| 병렬성 | Worker Threads | Multiprocessing |
| GIL | 없음 | **있음** (중요!) |
| I/O 처리 | 논블로킹 (기본) | 블로킹 (기본), AsyncIO로 논블로킹 |

---

## Python의 동시성 모델

### GIL (Global Interpreter Lock)

**JavaScript 개발자가 꼭 알아야 할 Python의 특징!**

```python
# Python의 GIL이란?
# - Python 인터프리터가 한 번에 하나의 스레드만 실행
# - 멀티 스레딩을 해도 CPU-bound 작업은 빨라지지 않음!

# ❌ Threading으로 CPU 작업 (GIL 때문에 느림)
import threading

def heavy_computation():
    result = 0
    for i in range(10_000_000):
        result += i
    return result

# 여러 스레드로 실행해도 느림 (GIL 때문)
threads = [threading.Thread(target=heavy_computation) for _ in range(4)]

# ✅ Multiprocessing으로 CPU 작업 (GIL 우회)
import multiprocessing

# 여러 프로세스로 실행하면 빠름 (각 프로세스가 독립적인 GIL)
processes = [multiprocessing.Process(target=heavy_computation) for _ in range(4)]
```

### 3가지 동시성 방식 비교

```
┌─────────────────────────────────────────────────┐
│                  Python 동시성                   │
├─────────────────┬──────────────┬────────────────┤
│   Threading     │  AsyncIO     │ Multiprocessing│
├─────────────────┼──────────────┼────────────────┤
│ 멀티 스레드     │ 싱글 스레드  │ 멀티 프로세스   │
│ GIL 영향 받음   │ GIL 영향 없음│ GIL 우회        │
│ I/O-bound 적합  │ I/O-bound 적합│CPU-bound 적합  │
│ 간단한 I/O 작업 │ 많은 I/O 작업│ 계산 작업       │
└─────────────────┴──────────────┴────────────────┘
```

---

## Threading (스레드)

### 언제 사용?

```
✅ I/O-bound 작업 (GIL의 영향 적음)
- 파일 읽기/쓰기
- 네트워크 요청
- 데이터베이스 쿼리

❌ CPU-bound 작업 (GIL 때문에 느림)
- 복잡한 계산
- 이미지 처리
- 데이터 분석
```

### 기본 사용법

```python
import threading
import time

def download_file(filename):
    """파일 다운로드 시뮬레이션 (I/O 작업)"""
    print(f"다운로드 시작: {filename}")
    time.sleep(2)  # 네트워크 I/O 대기
    print(f"다운로드 완료: {filename}")

# 순차 실행 (느림: 6초)
for i in range(3):
    download_file(f"file{i}.txt")

# 멀티 스레드 (빠름: 2초)
threads = []
for i in range(3):
    thread = threading.Thread(target=download_file, args=(f"file{i}.txt",))
    thread.start()
    threads.append(thread)

# 모든 스레드 완료 대기
for thread in threads:
    thread.join()
```

### JavaScript 개발자를 위한 비교

```javascript
// JavaScript (Promise.all)
const files = ['file1.txt', 'file2.txt', 'file3.txt'];
await Promise.all(files.map(file => downloadFile(file)));
```

```python
# Python (Threading)
import threading

threads = [
    threading.Thread(target=download_file, args=(file,))
    for file in ['file1.txt', 'file2.txt', 'file3.txt']
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
```

**실습 파일**: [1_threading_basics.py](1_threading_basics.py)

---

## Multiprocessing (멀티프로세싱)

### 언제 사용?

```
✅ CPU-bound 작업
- 복잡한 수학 계산
- 이미지/비디오 처리
- 머신러닝 학습
- 데이터 처리

❌ I/O-bound 작업 (오버헤드 때문에 비효율적)
- 파일 읽기/쓰기
- API 호출
```

### 기본 사용법

```python
import multiprocessing
import time

def heavy_computation(n):
    """CPU 집약적 작업"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result

# 순차 실행 (느림)
start = time.time()
results = [heavy_computation(10_000_000) for _ in range(4)]
print(f"순차 실행: {time.time() - start:.2f}초")

# 멀티프로세싱 (빠름)
start = time.time()
with multiprocessing.Pool(processes=4) as pool:
    results = pool.map(heavy_computation, [10_000_000] * 4)
print(f"병렬 실행: {time.time() - start:.2f}초")
```

### Threading vs Multiprocessing

```python
# Threading: GIL 때문에 CPU 작업은 느림
# 4개 스레드 → 싱글 코어에서 번갈아 실행
# 시간: ~4초 (거의 순차 실행과 동일)

# Multiprocessing: GIL 우회
# 4개 프로세스 → 4개 코어에서 동시 실행
# 시간: ~1초 (4배 빠름)
```

**실습 파일**: [2_multiprocessing_basics.py](2_multiprocessing_basics.py)

---

## AsyncIO (비동기)

### JavaScript 개발자에게 가장 익숙한 방식!

```javascript
// JavaScript
async function fetchData() {
    const response = await fetch('https://api.example.com');
    const data = await response.json();
    return data;
}

const results = await Promise.all([
    fetchData(),
    fetchData(),
    fetchData()
]);
```

```python
# Python (거의 동일!)
import asyncio
import aiohttp

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com') as response:
            data = await response.json()
            return data

# asyncio.gather = Promise.all
results = await asyncio.gather(
    fetch_data(),
    fetch_data(),
    fetch_data()
)
```

### 언제 사용?

```
✅ 많은 I/O 작업
- 수백 개의 API 호출
- 웹 스크래핑
- WebSocket 연결
- 데이터베이스 쿼리 (async 드라이버 사용 시)

❌ CPU-bound 작업
- 복잡한 계산 (Multiprocessing 사용)
```

### 기본 사용법

```python
import asyncio

async def say_hello(name, delay):
    """비동기 함수"""
    print(f"{name}: 시작")
    await asyncio.sleep(delay)  # I/O 대기 (논블로킹)
    print(f"{name}: 완료")
    return f"Hello, {name}!"

# 비동기 함수 실행
async def main():
    # 동시에 3개 실행
    results = await asyncio.gather(
        say_hello("Alice", 2),
        say_hello("Bob", 1),
        say_hello("Charlie", 3)
    )
    print(results)

# 실행
asyncio.run(main())
```

### AsyncIO vs Threading

| 특성 | AsyncIO | Threading |
|------|---------|-----------|
| 오버헤드 | 낮음 | 중간 |
| 동시 작업 수 | 수천~수만 개 | 수십~수백 개 |
| 복잡도 | 중간 | 낮음 |
| 라이브러리 | async 전용 필요 | 기존 라이브러리 사용 |

**실습 파일**: [3_asyncio_basics.py](3_asyncio_basics.py)

---

## 어떤 방식을 선택할까?

### 의사결정 플로우차트

```
작업이 I/O-bound인가? CPU-bound인가?
    │
    ├─ CPU-bound (계산 작업)
    │   └─→ Multiprocessing 사용
    │
    └─ I/O-bound (네트워크, 파일 등)
        │
        ├─ 작업이 100개 이상?
        │   └─→ AsyncIO 사용 (가장 효율적)
        │
        └─ 작업이 소수?
            │
            ├─ async 라이브러리 있음?
            │   └─→ AsyncIO 사용
            │
            └─ async 라이브러리 없음?
                └─→ Threading 사용 (간단함)
```

### 실전 예시

```python
# 1️⃣ 웹 스크래핑 (100개 URL)
# → AsyncIO
# 이유: 많은 네트워크 I/O, 동시 연결 수 많음

import asyncio
import aiohttp

async def scrape_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# 2️⃣ 이미지 리사이징 (10개 파일)
# → Multiprocessing
# 이유: CPU 집약적 작업

from multiprocessing import Pool
from PIL import Image

def resize_image(filename):
    img = Image.open(filename)
    img.thumbnail((800, 600))
    img.save(f"resized_{filename}")

with Pool(processes=4) as pool:
    pool.map(resize_image, image_files)

# 3️⃣ 파일 다운로드 (5개 파일)
# → Threading
# 이유: I/O 작업이지만 개수가 적어 Threading이 간단

import threading

def download_file(url):
    # ...

threads = [threading.Thread(target=download_file, args=(url,)) for url in urls]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

# 4️⃣ FastAPI 웹 서버
# → AsyncIO
# 이유: 많은 동시 요청 처리

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    # async/await 사용
    data = await fetch_from_db()
    return data
```

---

## 실습 파일

### 파일 목록

1. **[1_threading_basics.py](1_threading_basics.py)**
   - Threading 기초
   - I/O-bound 작업 예시
   - 스레드 풀 사용법

2. **[2_multiprocessing_basics.py](2_multiprocessing_basics.py)**
   - Multiprocessing 기초
   - CPU-bound 작업 예시
   - 프로세스 풀 사용법

3. **[3_asyncio_basics.py](3_asyncio_basics.py)**
   - AsyncIO 기초
   - async/await 문법
   - asyncio.gather 사용법

4. **[4_comparison.py](4_comparison.py)**
   - 3가지 방식 성능 비교
   - 실제 벤치마크 결과

5. **[5_real_world_examples.py](5_real_world_examples.py)**
   - 웹 스크래핑
   - API 호출
   - 파일 처리

### 실습 순서

1. **Threading 이해하기**
   ```bash
   python 1_threading_basics.py
   ```

2. **Multiprocessing 이해하기**
   ```bash
   python 2_multiprocessing_basics.py
   ```

3. **AsyncIO 이해하기** (JavaScript 개발자에게 가장 익숙!)
   ```bash
   python 3_asyncio_basics.py
   ```

4. **성능 비교해보기**
   ```bash
   python 4_comparison.py
   ```

5. **실전 예제 실행**
   ```bash
   python 5_real_world_examples.py
   ```

---

## JavaScript → Python 전환 팁

### 1. async/await는 거의 동일!

```javascript
// JavaScript
async function getData() {
    const result = await fetch('https://api.example.com');
    return await result.json();
}
```

```python
# Python
async def get_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com') as response:
            return await response.json()
```

### 2. Promise.all = asyncio.gather

```javascript
// JavaScript
const results = await Promise.all([task1(), task2(), task3()]);
```

```python
# Python
results = await asyncio.gather(task1(), task2(), task3())
```

### 3. 이벤트 루프

```javascript
// JavaScript (자동으로 실행)
async function main() {
    await doSomething();
}
main();
```

```python
# Python (명시적으로 실행)
async def main():
    await do_something()

asyncio.run(main())  # 이벤트 루프 시작
```

### 4. Worker Threads → Multiprocessing

```javascript
// JavaScript (Worker Threads)
const { Worker } = require('worker_threads');
const worker = new Worker('./worker.js');
```

```python
# Python (Multiprocessing)
from multiprocessing import Process
process = Process(target=worker_function)
process.start()
```

---

## 성능 비교 요약

### I/O-bound 작업 (네트워크 요청 100개)

| 방식 | 실행 시간 | 특징 |
|------|----------|------|
| 순차 실행 | ~100초 | 매우 느림 |
| Threading | ~5초 | 빠름, 간단 |
| **AsyncIO** | **~2초** | **가장 빠름** ⭐ |
| Multiprocessing | ~10초 | 오버헤드 큼, 비효율적 |

### CPU-bound 작업 (복잡한 계산 4개)

| 방식 | 실행 시간 | 특징 |
|------|----------|------|
| 순차 실행 | ~4초 | 느림 |
| Threading | ~4초 | GIL 때문에 빨라지지 않음 |
| AsyncIO | ~4초 | CPU 작업에는 효과 없음 |
| **Multiprocessing** | **~1초** | **가장 빠름** ⭐ |

---

## 참고 자료

### 공식 문서
- [Python Threading](https://docs.python.org/3/library/threading.html)
- [Python Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [Python AsyncIO](https://docs.python.org/3/library/asyncio.html)

### 추천 학습 자료
- [Real Python - Concurrency in Python](https://realpython.com/python-concurrency/)
- [Understanding GIL](https://realpython.com/python-gil/)
- [AsyncIO for JavaScript Developers](https://www.youtube.com/results?search_query=asyncio+for+javascript+developers)

---

## 요약

### JavaScript 개발자가 기억할 핵심

1. **AsyncIO = JavaScript의 async/await**
   - 문법이 거의 동일
   - I/O-bound 작업에 최적
   - 가장 먼저 배우기 추천!

2. **GIL 때문에 Threading은 CPU 작업에 효과 없음**
   - JavaScript에는 없는 개념
   - CPU 작업 = Multiprocessing

3. **3가지 방식 선택 기준**
   - 많은 I/O 작업 → AsyncIO
   - 소수 I/O 작업 → Threading
   - CPU 작업 → Multiprocessing

4. **FastAPI는 AsyncIO 기반**
   - JavaScript 개발자에게 친숙
   - async/await 문법 그대로 사용

이제 실습 파일을 실행해보세요! 🚀
