# PrismOps
LLM Gateway &amp; A/B Testing Platform

## LLM 서비스의 안정성과 비용 효율을 극대화하는 A/B 테스팅 및 관제 게이트웨이

## 1. 기획 배경 및 의도 (Problem & Solution)

- **배경 (Problem):** 현재 많은 AI 서비스들이 LLM API(GPT-4 등)를 블랙박스처럼 사용하고 있습니다. 이로 인해 "정확한 비용 산정의 어려움", "신규 모델 도입 시 리스크", "응답 속도(Latency) 병목 현상"을 파악하기 어렵습니다.
- **해결책 (Solution):** **PrismOps**는 서비스와 LLM 사이에 위치한 지능형 미들웨어(Middleware)입니다. 프리즘이 빛을 나누듯 트래픽을 정교하게 분산하여, 운영자가 안심하고 모델을 실험하고 모니터링할 수 있는 환경을 제공합니다.
- **핵심 가치:**
    1. **Cost Efficiency:** 상황에 따라 저렴한 모델로 자동 전환.
    2. **Reliability:** 장애 발생 시 즉시 우회(Failover).
    3. **Observability:** 모든 입출력 토큰과 응답 시간을 시각화.

---

## 2. 핵심 기능 (Key Features)

### ① Smart Routing (지능형 라우팅)

- 사용자의 요청 복잡도나 길이를 분석하여 최적의 모델로 연결합니다.
- **Logic:** 단순 인사/요약 ➔ **Local Llama 3 (무료)** / 복잡한 추론 ➔ **GPT-4o (유료)**

### ② Shadow Mode (🌟 Killing Point)

- **개념:** 운영 환경(Production)의 안정성을 해치지 않으면서 신규 모델을 테스트하는 고급 기술.
- **동작:** 사용자의 요청을 메인 모델(A)로 보내 답변을 리턴하는 동시에, 백그라운드에서 몰래 테스트 모델(B)에도 똑같은 요청을 보냅니다.
- **효과:** 사용자는 모델 B의 존재를 모르지만, 운영자는 모델 B가 실제 트래픽에서 잘 작동하는지(에러율, 속도) 데이터를 쌓을 수 있습니다.

### ③ Traffic Splitting (A/B Testing)

- 설정된 비율(예: 80:20)에 따라 트래픽을 분산시킵니다.
- 신규 모델 도입 전, 일부 사용자에게만 노출하여 반응을 살피는 **Canary 배포**를 시뮬레이션합니다.

### ④ Real-time Observability (실시간 관제)

- **Dashboard:** 처리량(TPS), 평균 응답 속도(Latency), 토큰 사용량(Cost), 에러율을 실시간 그래프로 시각화합니다.

---

## 3. 시스템 아키텍처 및 기술 스택

**Apple Silicon 로컬 환경**에서 비용 없이 엔터프라이즈급 아키텍처를 모사하도록 설계했습니다.

| **구분** | **기술 스택** | **선정 이유** |
| --- | --- | --- |
| **Language** | **Python 3.10+** | AI 생태계 표준 및 빠른 프로토타이핑 |
| **Framework** | **FastAPI** | 고성능 비동기(Async) 처리 지원 (I/O 바운드 작업 최적화) |
| **LLM Gateway** | **LiteLLM** | OpenAI, Azure, Ollama 등 다양한 모델을 표준화된 API로 통합 관리 |
| **Local Serving** | **Ollama** | Mac 환경(Metal 가속)에서 Llama 3 모델을 무료로 구동 |
| **Broker/Cache** | **Redis** | 로그 비동기 처리를 위한 경량 메시지 큐 역할 (Kafka 대체) |
| **Monitoring** | **Prometheus** | 시계열 데이터(Latency, TPS) 수집 |
| **Visualization** | **Grafana** | 수집된 데이터를 대시보드로 시각화 |
| **Infra** | **Docker & Compose** | 모든 컴포넌트를 컨테이너로 묶어 원클릭 실행 구현 |

### 🏗 Architecture Flow

1. **Client:** API 요청 (`POST /v1/chat/completions`)
2. **Prism Gateway (FastAPI):** 요청 수신 및 라우팅 로직 수행 (Shadow Mode 실행 여부 판단)
3. **Model Layer:**
    - Path A: **OpenAI API** (Main)
    - Path B: **Ollama Container** (Shadow/Local)
4. **Async Logger (Background Task):** 응답 완료 후 메타데이터(소요 시간, 모델명)를 **Redis**로 전송
5. **Metrics Exporter:** Redis에 쌓인 로그를 집계하여 **Prometheus**가 긁어갈 수 있는 포맷으로 노출
6. **Dashboard:** **Grafana**가 Prometheus 데이터를 시각화

---

## 4. 주차별 개발 일정 (2 Weeks Roadmap)

### [Week 1] 핵심 엔진(Core Engine) 구축

- **Day 1: 환경 설정 및 Hello World**
    - Docker Compose로 Redis, Prometheus, Grafana 띄우기.
    - Ollama 설치 및 Llama 3 모델 Pull (`ollama pull llama3`).
- **Day 2: Gateway 서버 구현 (Basic)**
    - FastAPI 프로젝트 생성.
    - LiteLLM을 연동하여 API 하나로 OpenAI와 Ollama를 번갈아 호출하는 기능 구현.
- **Day 3: 라우팅 로직 구현**
    - Config 파일(`config.yaml`)을 만들어 모델 비율(50:50) 설정 기능 추가.
    - 간단한 로드 밸런싱 구현.
- **Day 4: 로그 파이프라인 구축**
    - 요청이 끝나면 비동기(`BackgroundTasks`)로 Redis에 로그를 적재하는 로직 구현.
    - Main Thread가 멈추지 않도록 Non-blocking 처리 확인.

### [Week 2] 킬링 포인트 및 운영(Ops) 고도화

- **Day 5: Shadow Mode 구현 (🌟)**
    - 사용자에게는 Main 모델 결과만 반환.
    - 백그라운드 스레드에서 Shadow 모델 호출 및 결과 로깅.
    - Main vs Shadow 결과 비교(응답 속도 차이 등) 저장.
- **Day 6: 모니터링 대시보드 구성**
    - Prometheus 설정 파일(`prometheus.yml`) 작성.
    - Grafana에 접속하여 패널 생성 (RPS, Latency, Error Rate).
- **Day 7: 통합 테스트 및 문서화**
    - Docker Compose 하나로 전체 시스템(`Gateway + DB + Monitor`) 실행 확인.
    - README 작성: 아키텍처 다이어그램 포함, "Shadow Mode" 작동 방식 강조.

---

## 5. 기대 효과 및 어필 포인트 (Why Hire Me?)

이 프로젝트를 완성하면 이력서에 다음과 같이 기술할 수 있습니다.

> "LLM 운영 안정성을 위한 A/B 테스팅 및 Shadow Mode 게이트웨이 개발"
> 
> - **Ops 역량:** Kafka 대신 Redis를 활용해 경량화된 비동기 로그 파이프라인을 구축하고, Prometheus/Grafana로 실시간 관제 환경을 구성함.
> - **비용 최적화:** LiteLLM을 활용해 상용 모델(GPT-4)과 로컬 모델(Ollama)을 하이브리드로 구성, 트래픽 라우팅을 통해 비용 절감 구조 설계.
> - **문제 해결:** Mac Silicon 환경의 제약을 극복하기 위해 vLLM 대신 Ollama를 컨테이너화하여 Local MLOps 환경을 구현.
> - **고급 테크닉:** 운영 중인 서비스의 리스크 없이 신규 모델을 검증하는 **Shadow Mode**를 직접 구현하여 안정적인 배포 전략을 확보.

---