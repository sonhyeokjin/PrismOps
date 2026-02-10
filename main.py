# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from litellm import completion
import time
from dotenv import load_dotenv

# 1. FastAPI 앱 생성
app = FastAPI(
    title="PrismOps Gateway",
    description="LLM A/B Testing & Routing Gateway",
    version="0.1.0"
)


# 2. 데이터 모델 정의 (요청/응답 형식을 미리 약속함)
class ChatRequest(BaseModel):
    model: str = "ollama/gemma:7b"  # 기본값 설정
    message: str


class ChatResponse(BaseModel):
    reply: str
    model_used: str
    latency: float


# 3. 헬스 체크용 엔드포인트 (서버 살아있니?)
@app.get("/")
async def health_check():
    return {"status": "ok", "service": "PrismOps Gateway"}


# 4. 채팅 엔드포인트 (핵심 기능!)
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()

    print(f"📥 요청 수신: {request.model} / 내용: {request.message}")

    try:
        # LiteLLM으로 AI에게 질문 던지기
        response = completion(
            model=request.model,
            messages=[{"role": "user", "content": request.message}],
            api_base="http://localhost:11434"
        )

        # 답변 추출
        reply_text = response.choices[0].message.content
        end_time = time.time()
        process_time = round(end_time - start_time, 2)

        return ChatResponse(
            reply=reply_text,
            model_used=request.model,
            latency=process_time
        )

    except Exception as e:
        # 에러 나면 500 에러 반환
        raise HTTPException(status_code=500, detail=str(e))