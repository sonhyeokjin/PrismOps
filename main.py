# main.py
import time
import random
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from litellm import completion
from dotenv import load_dotenv

# 우리가 만든 모듈 가져오기
import config
import logger

load_dotenv()

app = FastAPI(
    title="PrismOps Gateway",
    description="A/B Testing Router for LLMs",
    version="0.2.0"  # 버전 업!
)


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
    """
    [A/B 라우팅 로직]
    1. 50% 확률로 Model A(Local) 또는 Model B(Cloud) 선택
    2. 선택된 모델로 추론 실행
    3. 결과 반환 및 비동기 로그 저장
    """
    start_time = time.time()

    # 🎲 1. 라우팅 결정 (0.0 ~ 1.0 사이의 랜덤 숫자 뽑기)
    if random.random() < config.ROUTING_RATIO:
        selected_model = config.MODEL_B  # Cloud
        tag = "Cloud(B)"
    else:
        selected_model = config.MODEL_A  # Local
        tag = "Local(A)"

    print(f"🔀 [Router] {tag} 선택됨 -> {selected_model}")

    try:
        # 🤖 2. 모델 호출
        response = completion(
            model=selected_model,
            messages=[{"role": "user", "content": request.message}]
        )

        reply_text = response.choices[0].message.content

        # ⏱️ 3. 시간 측정
        end_time = time.time()
        latency = round(end_time - start_time, 2)

        # 📝 4. 비동기 로그 저장 예약 (사용자는 기다리지 않음!)
        log_data = {
            "user_message": request.message,
            "reply_snippet": reply_text[:30] + "...",  # 답변 앞부분만 저장
            "model": selected_model,
            "latency": latency,
            "status": "success"
        }
        # 이 함수는 return이 끝난 뒤 백그라운드에서 실행됨
        background_tasks.add_task(logger.log_transaction, log_data)

        return ChatResponse(
            reply=reply_text,
            model=selected_model,
            latency=latency
        )

    except Exception as e:
        # 에러 발생 시에도 로그는 남겨야 함 (Error Log)
        error_data = {
            "user_message": request.message,
            "model": selected_model,
            "error": str(e),
            "status": "failed"
        }
        background_tasks.add_task(logger.log_transaction, error_data)
        raise HTTPException(status_code=500, detail=str(e))