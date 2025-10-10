# 쿠버네티스 Minikube 실습 가이드

이 문서는 [kubernetes-basic-concepts.md](./kubernetes-basic-concepts.md)의 이론을 직접 실습해보는 가이드입니다.

## 목차
1. [실습 환경 준비](#실습-환경-준비)
2. [실습 1: Pod 비정상 감지 및 복구](#실습-1-pod-비정상-감지-및-복구)
3. [실습 2: Service와 DNS 동작](#실습-2-service와-dns-동작)
4. [실습 3: 종합 실습](#실습-3-종합-실습)

---

## 실습 환경 준비

### Minikube 설치

**macOS:**
```bash
brew install minikube
```

**Linux:**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Windows:**
```powershell
choco install minikube
```

### Minikube 시작

```bash
# Docker 드라이버로 시작
minikube start --driver=docker

# 클러스터 상태 확인
kubectl cluster-info
kubectl get nodes
```

**예상 출력:**
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3
```

### 유용한 명령어

```bash
# Minikube 상태 확인
minikube status

# Minikube 대시보드 열기
minikube dashboard

# Minikube 중지
minikube stop

# Minikube 삭제
minikube delete
```

---

## 실습 1: Pod 비정상 감지 및 복구

### 목표
- livenessProbe가 실패했을 때 kubelet이 컨테이너를 재시작하는지 확인
- readinessProbe가 실패했을 때 트래픽이 차단되는지 확인
- Pod 삭제 시 Deployment가 자동으로 새 Pod를 생성하는지 확인

---

### 1-1. livenessProbe 실습

#### YAML 파일 생성

`liveness-probe-test.yaml` 파일을 만듭니다:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-test
  labels:
    app: liveness
spec:
  containers:
  - name: app
    image: nginx:latest
    ports:
    - containerPort: 80
    livenessProbe:
      httpGet:
        path: /healthz
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 5
```

#### 실습 단계

```bash
# 1. Pod 생성
kubectl apply -f liveness-probe-test.yaml

# 2. Pod 상태 확인
kubectl get pods -w
# -w 옵션: 실시간으로 상태 변화 관찰

# 3. Pod 이벤트 확인
kubectl describe pod liveness-test

# 4. Pod 로그 확인
kubectl logs liveness-test
```

#### 예상 결과

```
NAME            READY   STATUS    RESTARTS   AGE
liveness-test   1/1     Running   0          10s
liveness-test   1/1     Running   1          45s  ← 재시작 발생!
liveness-test   1/1     Running   2          1m20s
```

**확인 포인트:**
- `/healthz` 경로가 없으므로 livenessProbe 실패
- kubelet이 자동으로 컨테이너 재시작
- `RESTARTS` 카운트가 증가

#### 동작 흐름

```
[kubelet] --5초마다--> GET /healthz --> [nginx]
                              ↓
                          404 Not Found
                              ↓
                    livenessProbe 실패
                              ↓
                    kubelet이 컨테이너 재시작
                              ↓
                      RESTARTS 증가
```

#### 정리

```bash
kubectl delete pod liveness-test
```

---

### 1-2. readinessProbe 실습

#### YAML 파일 생성

`readiness-probe-test.yaml` 파일을 만듭니다:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: readiness-test
spec:
  replicas: 2
  selector:
    matchLabels:
      app: readiness
  template:
    metadata:
      labels:
        app: readiness
    spec:
      containers:
      - name: app
        image: nginx:latest
        ports:
        - containerPort: 80
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 3
---
apiVersion: v1
kind: Service
metadata:
  name: readiness-service
spec:
  selector:
    app: readiness
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

#### 실습 단계

```bash
# 1. Deployment와 Service 생성
kubectl apply -f readiness-probe-test.yaml

# 2. Pod 상태 확인
kubectl get pods -l app=readiness

# 3. Endpoints 확인 (Service가 어떤 Pod를 가리키는지)
kubectl get endpoints readiness-service

# 4. Pod 하나의 nginx를 의도적으로 중단
POD_NAME=$(kubectl get pods -l app=readiness -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -- nginx -s stop

# 5. 다시 Endpoints 확인
kubectl get endpoints readiness-service

# 6. Pod 상태 확인
kubectl get pods -l app=readiness
```

#### 예상 결과

**nginx 중단 전:**
```
NAME                              READY   STATUS    RESTARTS   AGE
readiness-test-6d8f9c7b4d-abc12   1/1     Running   0          30s
readiness-test-6d8f9c7b4d-xyz89   1/1     Running   0          30s

NAME                 ENDPOINTS                     AGE
readiness-service    10.244.0.5:80,10.244.0.6:80   30s
```

**nginx 중단 후:**
```
NAME                              READY   STATUS    RESTARTS   AGE
readiness-test-6d8f9c7b4d-abc12   0/1     Running   0          1m
readiness-test-6d8f9c7b4d-xyz89   1/1     Running   0          1m

NAME                 ENDPOINTS          AGE
readiness-service    10.244.0.6:80      1m  ← 하나의 IP만 남음!
```

**확인 포인트:**
- nginx가 중단된 Pod는 `READY` 상태가 `0/1`로 변경
- Service의 Endpoints에서 해당 Pod IP가 자동으로 제거됨
- 트래픽이 정상 Pod로만 전달됨

#### 동작 흐름

```
[kubelet] --3초마다--> GET / --> [nginx]
                          ↓
                  nginx 중단됨 (응답 없음)
                          ↓
              readinessProbe 실패
                          ↓
      Pod를 Service Endpoints에서 제거
                          ↓
          해당 Pod로 트래픽 차단
```

#### 정리

```bash
kubectl delete deployment readiness-test
kubectl delete service readiness-service
```

---

### 1-3. Deployment 자동 복구 실습

#### YAML 파일 생성

`auto-recovery-test.yaml` 파일을 만듭니다:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auto-recovery
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auto-recovery
  template:
    metadata:
      labels:
        app: auto-recovery
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```

#### 실습 단계

```bash
# 1. Deployment 생성
kubectl apply -f auto-recovery-test.yaml

# 2. Pod 목록 확인
kubectl get pods -l app=auto-recovery

# 3. Pod 하나 강제 삭제
POD_NAME=$(kubectl get pods -l app=auto-recovery -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD_NAME

# 4. 실시간으로 Pod 상태 관찰
kubectl get pods -l app=auto-recovery -w

# 5. Deployment 이벤트 확인
kubectl describe deployment auto-recovery
```

#### 예상 결과

```
NAME                             READY   STATUS    RESTARTS   AGE
auto-recovery-7d9b8c5f6d-abc12   1/1     Running   0          30s
auto-recovery-7d9b8c5f6d-def34   1/1     Running   0          30s
auto-recovery-7d9b8c5f6d-ghi56   1/1     Running   0          30s

# Pod 삭제 후
auto-recovery-7d9b8c5f6d-abc12   1/1     Terminating   0          1m
auto-recovery-7d9b8c5f6d-jkl78   0/1     Pending       0          0s  ← 새 Pod 생성!
auto-recovery-7d9b8c5f6d-jkl78   0/1     ContainerCreating   0   1s
auto-recovery-7d9b8c5f6d-jkl78   1/1     Running             0   3s
```

**확인 포인트:**
- Pod 삭제 즉시 Deployment가 새 Pod 생성
- 항상 replicas: 3 유지
- Self-healing 동작 확인

#### 동작 흐름

```
[kubectl delete pod] → Pod Terminating
                            ↓
              [ReplicaSet Controller 감지]
                "현재 Pod: 2개, 원하는 상태: 3개"
                            ↓
                  새 Pod 스케줄링 요청
                            ↓
                    [Scheduler]
                어느 노드에 배치할지 결정
                            ↓
                    [kubelet]
                   새 Pod 실행
```

#### 정리

```bash
kubectl delete deployment auto-recovery
```

---

## 실습 2: Service와 DNS 동작

### 목표
- Service 이름으로 DNS 질의가 어떻게 되는지 확인
- CoreDNS가 Service 이름을 ClusterIP로 변환하는지 확인
- kube-proxy가 ClusterIP를 실제 Pod IP로 라우팅하는지 확인

---

### 2-1. Service 생성 및 DNS 질의

#### YAML 파일 생성

`service-dns-test.yaml` 파일을 만듭니다:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

#### 실습 단계

```bash
# 1. Deployment와 Service 생성
kubectl apply -f service-dns-test.yaml

# 2. Service 확인
kubectl get service backend-service

# 3. Endpoints 확인 (Service가 가리키는 실제 Pod IP)
kubectl get endpoints backend-service

# 4. Pod IP 확인
kubectl get pods -l app=backend -o wide

# 5. 임시 Pod 생성하여 DNS 질의 테스트
kubectl run test-pod --image=busybox --rm -it --restart=Never -- sh

# test-pod 안에서 실행:
# nslookup backend-service
# nslookup backend-service.default.svc.cluster.local
# wget -O- http://backend-service
# exit
```

#### 예상 결과

**Service 정보:**
```
NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
backend-service   ClusterIP   10.96.100.123   <none>        80/TCP    1m
```

**Endpoints:**
```
NAME              ENDPOINTS                     AGE
backend-service   10.244.0.10:80,10.244.0.11:80 1m
```

**Pod IP:**
```
NAME                      READY   STATUS    RESTARTS   AGE   IP            NODE
backend-7d8f9c5b4d-abc    1/1     Running   0          1m    10.244.0.10   minikube
backend-7d8f9c5b4d-xyz    1/1     Running   0          1m    10.244.0.11   minikube
```

**DNS 질의 결과 (test-pod 안에서):**
```bash
/ # nslookup backend-service
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local

Name:      backend-service
Address 1: 10.96.100.123 backend-service.default.svc.cluster.local
```

**HTTP 요청 결과:**
```bash
/ # wget -O- http://backend-service
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
...
```

**확인 포인트:**
- Service 이름 → CoreDNS → ClusterIP 반환
- ClusterIP로 요청 → kube-proxy → 실제 Pod IP로 라우팅
- Pod IP가 바뀌어도 Service 이름은 동일하게 사용 가능

#### 동작 흐름

```
[test-pod]
    │
    │ 1. DNS 질의: backend-service
    ↓
[CoreDNS Pod]
    │ (kube-system 네임스페이스)
    │
    │ 2. Service 이름 → ClusterIP 매핑
    │    backend-service → 10.96.100.123
    ↓
[test-pod]
    │
    │ 3. HTTP 요청: http://10.96.100.123
    ↓
[kube-proxy]
    │ (iptables/IPVS 규칙)
    │
    │ 4. ClusterIP → 실제 Pod IP 라우팅
    │    10.96.100.123 → 10.244.0.10 또는 10.244.0.11
    ↓
[backend Pod]
```

---

### 2-2. CoreDNS 동작 확인

```bash
# 1. CoreDNS Pod 확인
kubectl get pods -n kube-system -l k8s-app=kube-dns

# 2. CoreDNS 로그 확인
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50

# 3. CoreDNS ConfigMap 확인
kubectl get configmap coredns -n kube-system -o yaml
```

**CoreDNS ConfigMap 예시:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
        }
        prometheus :9153
        forward . /etc/resolv.conf
        cache 30
        loop
        reload
        loadbalance
    }
```

---

### 2-3. Pod IP 변경 시 Service 동작 확인

```bash
# 1. 현재 Endpoints 확인
kubectl get endpoints backend-service

# 2. Pod 하나 삭제 (새 Pod가 생성되어 IP 변경)
POD_NAME=$(kubectl get pods -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD_NAME

# 3. 새로운 Pod 생성 확인
kubectl get pods -l app=backend -o wide

# 4. Endpoints 변경 확인
kubectl get endpoints backend-service

# 5. test-pod에서 여전히 Service 이름으로 접근 가능한지 확인
kubectl run test-pod --image=busybox --rm -it --restart=Never -- wget -O- http://backend-service
```

#### 예상 결과

**Pod 삭제 전:**
```
ENDPOINTS: 10.244.0.10:80,10.244.0.11:80
```

**Pod 삭제 후:**
```
ENDPOINTS: 10.244.0.11:80,10.244.0.15:80  ← IP 변경!
```

**확인 포인트:**
- Pod IP가 변경되어도 Service 이름(backend-service)은 동일
- Endpoints가 자동으로 업데이트됨
- 클라이언트는 Service 이름만 알면 되고, Pod IP는 몰라도 됨

#### 동작 흐름

```
Pod 삭제
    ↓
Deployment가 새 Pod 생성
    ↓
새 Pod가 새로운 IP (10.244.0.15) 할당받음
    ↓
Endpoints Controller가 변경 감지
    ↓
Endpoints 자동 업데이트
    ↓
kube-proxy가 새로운 라우팅 규칙 생성
    ↓
Service 이름으로 접근 시 새 Pod로 트래픽 전달
```

#### 정리

```bash
kubectl delete deployment backend
kubectl delete service backend-service
```

---

## 실습 3: 종합 실습

### 목표
전체 흐름을 하나의 시나리오로 확인:
1. Deployment로 여러 Pod 배포
2. Service로 외부에 노출
3. livenessProbe/readinessProbe 설정
4. Pod 장애 발생 시 자동 복구 확인
5. Service를 통한 트래픽 라우팅 확인

---

### YAML 파일 생성

`comprehensive-test.yaml` 파일을 만듭니다:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 3
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

---

### 실습 시나리오

#### 1단계: 배포 및 확인

```bash
# 1. 배포
kubectl apply -f comprehensive-test.yaml

# 2. 전체 리소스 확인
kubectl get all -l app=web

# 3. Endpoints 확인
kubectl get endpoints web-service

# 4. Pod 상세 정보 확인
kubectl get pods -l app=web -o wide
```

**예상 출력:**
```
NAME                           READY   STATUS    RESTARTS   AGE   IP
pod/web-app-7d8f9c5b4d-abc12   1/1     Running   0          30s   10.244.0.10
pod/web-app-7d8f9c5b4d-def34   1/1     Running   0          30s   10.244.0.11
pod/web-app-7d8f9c5b4d-ghi56   1/1     Running   0          30s   10.244.0.12

NAME                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
service/web-service   ClusterIP   10.96.200.100   <none>        80/TCP    30s

NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/web-app   3/3     3            3           30s

NAME                                ENDPOINTS                                      AGE
endpoints/web-service               10.244.0.10:80,10.244.0.11:80,10.244.0.12:80   30s
```

---

#### 2단계: Service를 통한 접근 테스트

```bash
# 1. 임시 Pod 생성하여 반복 요청
kubectl run test-client --image=busybox --rm -it --restart=Never -- sh

# test-client 안에서 실행:
while true; do
  echo "=== Request at $(date) ==="
  wget -O- -q http://web-service | grep '<title>'
  sleep 2
done
```

**다른 터미널에서 동시에 관찰:**
```bash
kubectl get pods -l app=web -w
```

---

#### 3단계: Pod 장애 시뮬레이션

**새 터미널에서:**
```bash
# Pod 하나의 nginx 중단 (readinessProbe 실패 유도)
POD_NAME=$(kubectl get pods -l app=web -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -- nginx -s stop

# Endpoints 변화 확인
kubectl get endpoints web-service -w
```

**예상 결과:**
```
# nginx 중단 전
NAME          ENDPOINTS                                      AGE
web-service   10.244.0.10:80,10.244.0.11:80,10.244.0.12:80   2m

# nginx 중단 후 (약 5초 후)
web-service   10.244.0.11:80,10.244.0.12:80                  2m
```

**확인 포인트:**
- readinessProbe 실패 → 해당 Pod가 Endpoints에서 제거됨
- test-client의 요청은 계속 정상 처리 (정상 Pod로만 전달)
- 장애 Pod는 트래픽을 받지 않음

---

#### 4단계: 자동 복구 확인

```bash
# 1. Pod 하나 강제 삭제
POD_NAME=$(kubectl get pods -l app=web -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD_NAME

# 2. 실시간 관찰
kubectl get pods -l app=web -w

# 3. Deployment가 새 Pod 자동 생성 확인
kubectl get pods -l app=web
```

**예상 결과:**
```
web-app-7d8f9c5b4d-abc12   1/1     Terminating         0          5m
web-app-7d8f9c5b4d-jkl78   0/1     Pending             0          0s  ← 새 Pod
web-app-7d8f9c5b4d-jkl78   0/1     ContainerCreating   0          1s
web-app-7d8f9c5b4d-jkl78   1/1     Running             0          3s
```

**확인 포인트:**
- Deployment가 즉시 새 Pod 생성
- replicas: 3 유지
- Self-healing 동작 확인

---

#### 5단계: 전체 흐름 시각화

```bash
# 1. 모든 구성 요소 확인
kubectl get all,endpoints -l app=web

# 2. Pod 이벤트 확인
kubectl get events --sort-by='.lastTimestamp' | grep web-app

# 3. Service 상세 정보
kubectl describe service web-service
```

---

### 전체 동작 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────┐
│                    Control Plane                         │
│                                                          │
│  [kube-apiserver] ← [controller-manager] ← [scheduler]  │
│         │                                                │
│         └─── 상태 저장 → [etcd]                         │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Pod 상태 보고
                        │
┌─────────────────────────────────────────────────────────┐
│                    Worker Node                           │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ [kubelet]                                       │    │
│  │   ├─ livenessProbe 실행 (10초마다)             │    │
│  │   ├─ readinessProbe 실행 (5초마다)             │    │
│  │   └─ 이상 발견 시 → 재시작 / 상태 보고        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ [kube-proxy]                                    │    │
│  │   └─ ClusterIP → Pod IP 라우팅 규칙 관리       │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ [CoreDNS Pod]                                   │    │
│  │   └─ Service 이름 → ClusterIP 매핑 제공        │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Pod 1       │  │ Pod 2       │  │ Pod 3       │    │
│  │ web-app     │  │ web-app     │  │ web-app     │    │
│  │ 10.244.0.10 │  │ 10.244.0.11 │  │ 10.244.0.12 │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│         ▲                ▲                ▲             │
│         └────────────────┴────────────────┘             │
│                          │                              │
│                  [Service: web-service]                 │
│                  ClusterIP: 10.96.200.100               │
│                  Endpoints: 3개 Pod IP                  │
└─────────────────────────────────────────────────────────┘
```

---

### 실습 결과 요약

| 항목 | 동작 확인 |
|-----|----------|
| **livenessProbe** | ✅ 실패 시 kubelet이 컨테이너 재시작 |
| **readinessProbe** | ✅ 실패 시 Endpoints에서 제거, 트래픽 차단 |
| **Self-healing** | ✅ Pod 삭제 시 Deployment가 자동 복구 |
| **Service 이름 접근** | ✅ CoreDNS가 Service 이름 → ClusterIP 변환 |
| **트래픽 라우팅** | ✅ kube-proxy가 ClusterIP → Pod IP 라우팅 |
| **동적 IP 대응** | ✅ Pod IP 변경 시 Endpoints 자동 업데이트 |

---

### 정리

```bash
kubectl delete deployment web-app
kubectl delete service web-service
```

---

## 추가 학습 자료

### 유용한 kubectl 명령어

```bash
# Pod 로그 실시간 확인
kubectl logs -f <pod-name>

# Pod 안에서 명령 실행
kubectl exec -it <pod-name> -- /bin/bash

# 리소스 사용량 확인
kubectl top nodes
kubectl top pods

# YAML 출력
kubectl get <resource> <name> -o yaml

# 특정 레이블의 리소스만 확인
kubectl get pods -l app=web

# 네임스페이스별 리소스 확인
kubectl get all -n kube-system

# 이벤트 확인
kubectl get events --sort-by='.lastTimestamp'

# 리소스 감시
kubectl get pods -w
```

### 디버깅 팁

```bash
# Pod가 Pending 상태일 때
kubectl describe pod <pod-name>
# → Events 섹션에서 원인 확인

# Pod가 CrashLoopBackOff일 때
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # 이전 컨테이너 로그

# Service가 동작하지 않을 때
kubectl get endpoints <service-name>
# → Endpoints가 비어있으면 selector 확인

# DNS 문제 디버깅
kubectl run dnsutils --image=tutum/dnsutils --rm -it --restart=Never -- nslookup kubernetes.default
```

---

## 다음 단계

이 실습을 완료했다면:

1. **[kubernetes-basic-concepts.md](./kubernetes-basic-concepts.md)** 문서를 다시 읽어보세요
   - 실습 후 이론을 다시 보면 이해도가 크게 향상됩니다

2. **추가 개념 학습**
   - ConfigMap, Secret (설정 관리)
   - Ingress (외부 트래픽 라우팅)
   - Persistent Volume (데이터 저장)
   - Namespace (리소스 격리)

3. **실전 시나리오 연습**
   - 멀티 서비스 통신
   - 롤링 업데이트
   - Auto-scaling

---

## 참고 자료

- 쿠버네티스 공식 문서: https://kubernetes.io/docs/
- kubectl cheat sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Minikube 튜토리얼: https://minikube.sigs.k8s.io/docs/start/
