# 쿠버네티스 기본 동작 원리

## 목차
1. [Pod 비정상 감지 및 복구 메커니즘](#1-pod-비정상-감지-및-복구-메커니즘)
2. [Service 간 통신과 DNS 동작 방식](#2-service-간-통신과-dns-동작-방식)
3. [쿠버네티스 아키텍처 계층 구조](#3-쿠버네티스-아키텍처-계층-구조)

---

## 1. Pod 비정상 감지 및 복구 메커니즘

### 핵심 질문
**"Pod가 비정상이 될 때 쿠버네티스는 어떻게 감지하고 대응하는가?"**

### 감지 단계 - 상태 모니터링

쿠버네티스는 여러 레벨에서 Pod 상태를 주기적으로 감시합니다.

| 감시 주체 | 감시 대상 | 역할 |
|---------|---------|------|
| kubelet (노드 에이전트) | Pod 내부 컨테이너 | 컨테이너가 정상인지, 죽었는지, 재시작 중인지 감지 |
| kube-controller-manager | ReplicaSet / Deployment | 지정된 개수만큼 Pod가 존재하는지 감시 |
| Probe | 애플리케이션 내부 상태 | 앱이 "살아있는지", "요청 받을 준비 됐는지" 확인 |

### Probe (탐침) 종류

| 종류 | 목적 | 동작 방식 |
|-----|------|----------|
| **livenessProbe** | 앱이 "죽었는지" 감지 | 실패하면 kubelet이 컨테이너 재시작 |
| **readinessProbe** | 요청 받을 "준비 됐는지" 감지 | 실패하면 Service 트래픽에서 제외 |
| **startupProbe** | 앱이 "초기화 중인지" 감지 | 초기 로딩이 오래 걸리는 앱 보호용 |

### Probe 설정 예시

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
```

### 대응 단계 - 복구 메커니즘

| 비정상 원인 | 감지 주체 | 대응 방식 |
|-----------|---------|----------|
| 컨테이너 crash (exit code ≠ 0) | kubelet | 컨테이너 재시작 (restartPolicy) |
| livenessProbe 실패 | kubelet | 컨테이너 강제 재시작 |
| 노드 다운 (kubelet heartbeat 끊김) | controller-manager | 해당 노드의 Pod들을 다른 노드로 재스케줄링 |
| Replica 부족 (Pod 사라짐) | ReplicaSet controller | 새 Pod 생성 |
| Deployment 롤아웃 실패 | Deployment controller | 자동 롤백 또는 중단 |

### 전체 흐름 요약

```
1️⃣ kubelet이 주기적으로 Pod/Container 상태를 보고
2️⃣ 비정상 탐지 → probe 실패 or 컨테이너 crash 감지
3️⃣ kubelet이 재시작 또는 상태 보고
4️⃣ controller-manager가 desired 상태와 불일치 확인
5️⃣ 새로운 Pod를 생성하거나 노드를 변경하여 self-healing (자가 복구) 수행
```

### 쿠버네티스 클러스터 전체 구조 (Pod 상태 감지 관점)

```
🟦 Kubernetes Cluster
│
├── 🧠 Master Node (Control Plane)
│   │
│   ├── 📦 kube-apiserver
│   │     └─ 클러스터 모든 상태(Pod, Node 등)를 관리하는 중앙 API
│   │
│   ├── ⚙️ controller-manager
│   │     ├─ ReplicaSet Controller → "Pod 개수 유지" 감시
│   │     └─ Node Controller → "노드 상태" 감시 (kubelet heartbeat 체크)
│   │
│   ├── 🧮 scheduler
│   │     └─ 새로 만들어질 Pod가 어느 노드에 갈지 결정
│   │
│   └── 🗄 etcd
│         └─ 클러스터 전체 상태 저장소 (DB 역할)
│
│
└── 🖥 Worker Node (일반 노드)
    │
    ├── 🧩 kubelet
    │     ├─ 현재 노드의 Pod 상태를 모니터링
    │     ├─ 컨테이너 실행/중단 관리
    │     ├─ livenessProbe / readinessProbe 실행
    │     └─ 이상 발생 시 → kube-apiserver로 상태 보고
    │
    ├── 📦 kube-proxy
    │     └─ Service의 ClusterIP 기반으로 트래픽 라우팅 담당
    │
    └── 🧱 Pod (하나 이상의 Container로 구성)
          │
          ├── 🐳 Container
          │     └─ 실제 애플리케이션 실행
          │
          ├── 🔍 livenessProbe
          │     └─ 앱이 "살아있는지" 확인 → 실패 시 kubelet이 컨테이너 재시작
          │
          ├── 🔍 readinessProbe
          │     └─ 앱이 "요청 받을 준비 됐는지" 확인 → 실패 시 트래픽 제외
          │
          └── 🔍 startupProbe (선택)
                └─ 앱 초기 구동 중일 때 false positives 방지
```

### 복구 흐름 다이어그램

```
🔁 흐름 정리 (Pod 비정상 → 복구까지)

1️⃣ kubelet이 Probe 실행 중 → livenessProbe 실패 감지

2️⃣ kubelet이 컨테이너 재시작
   └─ 만약 노드 자체가 죽었으면?
       → controller-manager(Node Controller)가 노드 다운 감지

3️⃣ scheduler가 새 Pod를 다른 노드에 스케줄링

4️⃣ kube-apiserver를 통해 etcd에 새로운 상태 반영
```

### 핵심 요약

> **쿠버네티스는 kubelet과 controller-manager가 지속적으로 Pod 상태를 모니터링하고,**
> **probe 실패나 노드 장애를 감지하면 컨테이너 재시작 또는 새 Pod 생성으로 자동 복구한다.**
> **즉, "자가 복구(Self-healing)" 시스템이다.**

---

## 2. Service 간 통신과 DNS 동작 방식

### 핵심 질문
**"Pod가 다른 Service의 IP를 어떻게 찾아가는가? 쿠버네티스 내부 DNS는 어떻게 동작하는가?"**

### 문제 상황
- Pod A가 Pod B가 제공하는 서비스(예: 웹 API)를 호출하고 싶음
- Pod B가 동적으로 생성/삭제될 수 있음 → IP가 계속 바뀜
- Pod A는 항상 같은 Service 이름으로 접근하고 싶음 → **쿠버네티스 DNS 등장**

### 핵심 개념

| 용어 | 설명 |
|-----|------|
| **Service** | 여러 Pod 묶음에 하나의 고정된 논리적 이름과 ClusterIP를 제공 |
| **ClusterIP** | 쿠버네티스 클러스터 내부에서 유일한 IP (Pod가 Service를 호출할 때 사용) |
| **CoreDNS** | 클러스터 내부 DNS 서버. Service 이름 → ClusterIP 매핑 담당 |
| **Endpoints** | Service가 연결할 실제 Pod IP 목록 |
| **kube-proxy** | ClusterIP → 실제 Pod IP로 트래픽 라우팅 |

### 내부 동작 단계

#### (1) Service 생성
```
사용자가 Deployment + Service를 만들면:

1. Deployment가 Pod 생성
2. Service가 Pod들을 묶고 ClusterIP 할당
3. 동시에 Endpoints 객체 생성 → Service가 연결할 Pod들의 실제 IP 저장

예시:
Service: my-web
  ClusterIP: 10.96.0.10
  Endpoints: 10.244.1.5, 10.244.2.7
```

#### (2) Pod에서 Service 접근
```
1. Pod A가 http://my-web 요청
2. Pod A의 OS는 클러스터 DNS 서버(CoreDNS)로 질의
   예: my-web.default.svc.cluster.local
3. DNS 서버가 ClusterIP(10.96.0.10) 반환
```

#### (3) kube-proxy가 트래픽 라우팅
```
1. Pod A가 받은 ClusterIP로 요청 전송
2. kube-proxy가 Node 레벨에서 패킷을 실제 Pod IP 중 하나로 라우팅
3. Round-robin 또는 다른 로드밸런싱 정책 적용
4. Pod B 중 한 개가 요청 처리
   → Pod A는 서비스 이름만 알고 실제 Pod IP는 몰라도 됨
```

### Service 통신 흐름 다이어그램

```
[Pod A] ---> (http://my-web) ---> [CoreDNS]
                                  │
                                  ▼
                           ClusterIP: 10.96.0.10
                                  │
                                  ▼
                            [kube-proxy]
                          ┌─────────────┐
                          │ Pod B1 (10.244.1.5)
                          │ Pod B2 (10.244.2.7)
                          └─────────────┘
```

### 전체 아키텍처 (Service 통신 관점)

```
🟦 Kubernetes Cluster
│
├── 🧠 Master Node (Control Plane)
│   │
│   ├── 📦 kube-apiserver
│   │     └─ Cluster 상태 관리 (Pod, Service, Endpoints)
│   │
│   ├── ⚙️ controller-manager
│   │     └─ Deployment/ReplicaSet 감시 → Pod 수 맞추기
│   │
│   └── 🗄 etcd
│         └─ 클러스터 상태 저장 (Service 이름, ClusterIP, Pod IP 등)
│
└── 🖥 Worker Node (일반 노드)
    │
    ├── 🧩 kubelet
    │     ├─ Pod 실행 및 상태 감시
    │     └─ livenessProbe / readinessProbe 수행
    │
    ├── 📦 kube-proxy
    │     └─ ClusterIP 기반 트래픽을 실제 Pod IP로 라우팅
    │
    ├── 🔹 Pod A (클라이언트)
    │     └─ 애플리케이션 컨테이너
    │          └─ 요청: http://my-service
    │
    └── 🔹 Pod B1, Pod B2 (서비스 대상)
          ├─ Pod B1: 실제 애플리케이션
          └─ Pod B2: 실제 애플리케이션
```

### Pod A 요청 흐름

```
────────────────────────────────────────────
[Pod A 요청 흐름]

1️⃣ Pod A에서 http://my-service 요청

2️⃣ CoreDNS 질의
   → my-service.default.svc.cluster.local
   → ClusterIP 반환

3️⃣ 요청이 ClusterIP(10.96.0.10)로 전송

4️⃣ kube-proxy가 ClusterIP → 실제 Pod B1/B2 IP로 라우팅

5️⃣ Pod B1 또는 B2가 요청 처리
────────────────────────────────────────────
```

### 핵심 포인트

- ✅ **Service 이름으로 항상 접근 가능** → Pod IP가 바뀌어도 안전
- ✅ **CoreDNS** → 이름 → ClusterIP 변환
- ✅ **kube-proxy** → ClusterIP → 실제 Pod IP 라우팅
- ✅ **Controller + Endpoints** → Pod IP 변화 감지 → Service와 자동 연동

### 핵심 요약

> **Pod는 Service 이름으로 접근하고, CoreDNS가 이름 → ClusterIP 매핑, kube-proxy가 ClusterIP → 실제 Pod IP 라우팅을 수행하므로,**
> **Pod IP가 바뀌어도 항상 안정적으로 접근 가능하다.**

---

## 3. 쿠버네티스 아키텍처 계층 구조

### 전체 계층 구조

| 계층 | 예시 | 설명 |
|-----|------|------|
| **Cluster** | 회사 전체 쿠버네티스 환경 | 여러 서버(Node)를 묶은 전체 단위 |
| **Node** | 서버 한 대 (리눅스, VM 등) | Pod들이 실행되는 실제 공간 |
| **Pod** | 프로그램 단위 | 컨테이너 1~2개를 감싸는 실행 단위 |
| **Container** | 실제 앱 (nginx, python 등) | Pod 안에서 실행되는 프로그램 |

### 비유로 이해하기

```
🏢 회사 건물 (Cluster)
 ┣ 🏠 각 층 (Node)
 ┣ 🚪 각 방 (Pod)
 ┗ 👩‍💻 방 안의 사람 (Container)
```

### Node 구조

```
Kubernetes Cluster
 ├─ Node A
 │   ├─ Pod 1
 │   ├─ Pod 2
 │   └─ Pod 3
 ├─ Node B
 │   ├─ Pod 4
 │   └─ Pod 5
 └─ Node C
     ├─ Pod 6
     └─ Pod 7
```

### kubelet 설치 위치

| 구분 | kubelet 설치 | 일반 Pod 배치 가능? | 실행되는 Pod 예시 |
|-----|-------------|------------------|------------------|
| **마스터 노드** | ✅ 필요 | ❌ (기본적으로 taint로 막힘) | kube-apiserver, etcd, scheduler 등 |
| **워커 노드** | ✅ 필요 | ✅ | 사용자 Pod, Deployment, DaemonSet 등 |

### Control Plane 주요 컴포넌트

| 구성요소 | 역할 |
|---------|------|
| **kube-apiserver** | 쿠버네티스의 중심. 모든 명령은 여기로 옴 |
| **etcd** | 쿠버네티스의 데이터베이스 (상태 저장) |
| **kube-scheduler** | 새 Pod를 어느 Node에 넣을지 결정 |
| **kube-controller-manager** | Pod 개수를 맞추고, 복구하는 역할 |
| **kubelet** | (있긴 있음) 마스터 자체의 상태 관리용 |

### 실제 구조 다이어그램

```
[ Control Plane Node ]
 ├─ kube-apiserver
 ├─ etcd
 ├─ scheduler
 ├─ controller-manager
 └─ kubelet  ← 관리용

[ Worker Node 1 ]
 ├─ kubelet
 ├─ kube-proxy
 ├─ Pod 1 (nginx)
 ├─ Pod 2 (backend)

[ Worker Node 2 ]
 ├─ kubelet
 ├─ kube-proxy
 ├─ Pod 3 (db)
```

---

## 학습 환경 구성 방법

### PC 한 대로 쿠버네티스 학습하기

| 방식 | 특징 | 학습 가능 범위 | 난이도 |
|-----|------|--------------|--------|
| **Minikube** | 한 대에서 간단히 실행 | Pod, Service, Deployment, Probe 등 대부분 | ⭐ (가장 쉬움) |
| **kind** | Docker 안에서 멀티노드 가능 | 멀티노드, 네트워크 연습 | ⭐⭐ |
| **kubeadm + VM** | 진짜 서버 구성처럼 | 완전한 실전 환경 | ⭐⭐⭐ (설정 많음) |

### Minikube 시작하기 (추천)

```bash
# Minikube 시작
minikube start --driver=docker

# 클러스터 확인
kubectl get nodes
```

---

## 핵심 요약

### Pod 비정상 감지 및 복구
```
Control Plane(마스터 노드) = "두뇌"
Worker Node(일반 노드) = "근육"
kubelet + probe = "감각기관"

이 셋이 합쳐져서 Pod 비정상 → 감지 → 보고 → 복구를 자동으로 수행한다.
```

### Service 통신 및 DNS
```
Pod는 Service 이름으로 접근하고,
CoreDNS가 이름 → ClusterIP 매핑,
kube-proxy가 ClusterIP → 실제 Pod IP 라우팅을 수행하므로,
Pod IP가 바뀌어도 항상 안정적으로 접근 가능하다.
```

---

## 참고 자료
- 쿠버네티스 공식 문서: https://kubernetes.io/docs/
- Minikube: https://minikube.sigs.k8s.io/
- kind (Kubernetes in Docker): https://kind.sigs.k8s.io/
