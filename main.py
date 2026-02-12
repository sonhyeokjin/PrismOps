import time
import random
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from litellm import completion
from dotenv import load_dotenv

# Prometheus 모니터링 도구
from prometheus_fastapi_instrumentator import Instrumentator

# 모듈
import config
import logger

# 환경변수 로드
load_dotenv()

# 앱 초기화
app = FastAPI(
    title="PrismOps Gateway",
    description="A/B Testing Router for LLMs",
    version="0.3.1"  # 버그 수정 버전 업
)

# Prometheus 계측기 실행 (/metrics 엔드포인트 노출)
Instrumentator().instrument(app).expose(app)


# 데이터 모델 정의
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    model: str
    latency: float


@app.get("/")
async def health_check():
    return {"status": "ok", "mode": "A/B Routing"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    start_time = time.time()

    # 1. 라우팅 결정 (50:50 확률)
    if random.random() < config.ROUTING_RATIO:
        selected_model = config.MODEL_B  # Cloud (OpenAI)
        tag = "Cloud(B)"
    else:
        selected_model = config.MODEL_A  # Local (Ollama)
        tag = "Local(A)"

    print(f"🔀 [Router] {tag} 선택됨 -> {selected_model}")

    # 모델 타입에 따른 API 주소 분기 처리
    # 기본값은 None으로 설정 (OpenAI는 주소를 따로 설정할 필요 없음)
    custom_api_base = None

    # 만약 로컬 모델(Ollama)이 선택되었다면, 도커 호스트 주소(host.docker.internal)를 사용
    if selected_model == config.MODEL_A:
        custom_api_base = config.OLLAMA_API_BASE

    try:
        # 2. 모델 호출
        response = completion(
            model=selected_model,
            messages=[{"role": "user", "content": request.message}],
            api_base=custom_api_base
        )

        reply_text = response.choices[0].message.content

        # 3. 시간 측정
        end_time = time.time()
        latency = round(end_time - start_time, 2)

        # 4. 비동기 로그 저장
        log_data = {
            "user_message": request.message,
            "reply_snippet": reply_text[:30] + "...",
            "model": selected_model,
            "latency": latency,
            "status": "success"
        }
        background_tasks.add_task(logger.log_transaction, log_data)

        return ChatResponse(
            reply=reply_text,
            model=selected_model,
            latency=latency
        )

    except Exception as e:
        # 에러 발생 시 로그
        error_data = {
            "user_message": request.message,
            "model": selected_model,
            "error": str(e),
            "status": "failed"
        }
        background_tasks.add_task(logger.log_transaction, error_data)

        print(f"[Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))