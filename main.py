# main.py
import time
import random
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from litellm import completion
from dotenv import load_dotenv

# ✨ 1. Prometheus 도구 불러오기
from prometheus_fastapi_instrumentator import Instrumentator

import config
import logger

load_dotenv()

app = FastAPI(
    title="PrismOps Gateway",
    description="A/B Testing Router for LLMs",
    version="0.3.0"  # 버전 업!
)

# ✨ 2. 서버가 켜질 때 계측기(Instrumentator)도 같이 켜기
# - instrument(app): 요청이 들어올 때마다 자동으로 숫자를 셉니다.
# - expose(app): '/metrics' 주소로 그 숫자를 보여줍니다.
Instrumentator().instrument(app).expose(app)


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

    # 🎲 라우팅 결정
    if random.random() < config.ROUTING_RATIO:
        selected_model = config.MODEL_B
    else:
        selected_model = config.MODEL_A

    print(f"🔀 [Router] 선택됨 -> {selected_model}")

    try:
        response = completion(
            model=selected_model,
            messages=[{"role": "user", "content": request.message}],
            api_base=config.OLLAMA_API_BASE
        )

        reply_text = response.choices[0].message.content
        end_time = time.time()
        latency = round(end_time - start_time, 2)

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
        error_data = {
            "user_message": request.message,
            "model": selected_model,
            "error": str(e),
            "status": "failed"
        }
        background_tasks.add_task(logger.log_transaction, error_data)
        raise HTTPException(status_code=500, detail=str(e))