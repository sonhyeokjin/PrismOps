import os
import time
import json
import hashlib
import redis
from fastapi import FastAPI, BackgroundTasks
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from kafka import KafkaProducer
from pymongo import MongoClient

app = FastAPI(title="PrismOps Gateway")

# Prometheus Scraping (앱 실행 시 자동 시작)
Instrumentator().instrument(app).expose(app)

# 인프라 연결 설정 (Redis 포함)
# Kafka
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'prism-kafka:9092')
producer = None
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=5000,
        acks=0
    )
    print(f"✅ [Kafka] Connected")
except Exception:
    print(f"⚠️ [Kafka] Connection Failed (Shadow Mode Disabled)")

# MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://prism-mongo:27017')
mongo_client = None
collection = None
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client['prism_db']
    collection = db['shadow_results']
    print("✅ [MongoDB] Connected")
except Exception:
    print("⚠️ [MongoDB] Connection Failed")

# Redis 연결
REDIS_HOST = os.getenv('REDIS_HOST', 'prism-redis')
redis_client = None
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    # 연결 테스트
    redis_client.ping()
    print(f"✅ [Redis] Connected to {REDIS_HOST}")
except Exception as e:
    print(f"⚠️ [Redis] Connection Failed: {e}")


# 데이터 모델 & 유틸리티
class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4o-mini"


def generate_cache_key(message: str, model: str):
    """질문 내용을 기반으로 고유한 해시 키 생성"""
    raw_key = f"{model}:{message.strip().lower()}"
    return hashlib.md5(raw_key.encode()).hexdigest()


def send_to_shadow_mode(user_message: str, main_response: str, main_latency: float, model_name: str):
    if producer:
        try:
            log_data = {
                "timestamp": time.time(),
                "prompt": user_message,
                "main_model": model_name,
                "main_response": main_response,
                "main_latency": main_latency,
                "shadow_model": "gemma:7b"
            }
            producer.send('prism-logs', log_data)
        except Exception as e:
            print(f"❌ Kafka Error: {e}")


# API 엔드포인트
@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/logs")
def get_shadow_logs():
    if collection is not None:
        return {"status": "ok", "logs": list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))}
    return {"status": "error", "message": "DB Not Connected"}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    start_time = time.time()
    cache_hit = False

    # [Step 1] Redis 캐시 확인
    cache_key = generate_cache_key(request.message, request.model)
    cached_response = None

    if redis_client:
        try:
            cached_response = redis_client.get(cache_key)
        except Exception:
            pass  # Redis 에러나도 메인 로직은 돌아가야 함

    if cached_response:
        # ✅ Cache Hit! (저장된 답변 반환)
        main_response = cached_response
        cache_hit = True
        print(f"⚡ [Cache Hit] Key: {cache_key}")
    else:
        # Cache Miss (AI 호출)
        # [Simulate OpenAI Call] - 실제 연동 시엔 litellm 사용
        # time.sleep(1) # 모의 지연 시간 (테스트용)
        main_response = f"[{request.model}] (Generated) 답변입니다: {request.message}"

        # Redis에 저장 (TTL: 3600초 = 1시간)
        if redis_client:
            redis_client.setex(cache_key, 3600, main_response)

    latency = time.time() - start_time

    # [Step 2] Shadow Mode (캐시에서 나왔더라도 성능 비교를 위해 Shadow는 돌릴 수 있음)
    # *선택사항: 캐시된 응답은 Shadow를 안 돌리고 싶다면 if not cache_hit: 조건을 걸면 됩니다.
    # 여기서는 데이터 수집을 위해 무조건 돌리는 것으로 둡니다.
    if producer:
        background_tasks.add_task(
            send_to_shadow_mode,
            request.message,
            main_response,
            latency,
            request.model
        )

    return {
        "response": main_response,
        "latency": latency,
        "model": request.model,
        "cached": cache_hit  # 프론트엔드에서 표시
    }