from kafka import KafkaConsumer
from pymongo import MongoClient
import requests
import json
import os
import time

# 설정 로드
KAFKA_SERVER = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'prism-kafka:9092')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://prism-mongo:27017')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')

print("Shadow Worker Starting...")

# 1. MongoDB 연결
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client['prism_db']
    collection = db['shadow_results']
    print("MongoDB Connected")
except Exception as e:
    print(f"MongoDB Failed: {e}")

# 2. Kafka Consumer 연결 (무한 재시도 로직 필요 - Kafka가 늦게 뜰 수 있음)
consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer(
            'prism-logs',  # 구독할 토픽
            bootstrap_servers=KAFKA_SERVER,
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='shadow-worker-group'
        )
        print("✅ Kafka Consumer Connected")
    except Exception as e:
        print("Waiting for Kafka...")
        time.sleep(5)

# 3. 메시지 처리 루프 (Daemon)
print("Worker is listening for Shadow Tasks...")
for message in consumer:
    data = message.value
    print(f"Received Task: {data['prompt'][:20]}...")

    # Shadow Model (Local Ollama) 호출
    start = time.time()
    shadow_response = "Error"
    try:
        payload = {
            "model": "gemma:7b",
            "prompt": data['prompt'],
            "stream": False
        }
        res = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload)
        if res.status_code == 200:
            shadow_response = res.json().get('response', '')
    except Exception as e:
        print(f"Ollama Call Failed: {e}")
        shadow_response = str(e)

    shadow_latency = time.time() - start

    # 결과 병합 및 DB 저장
    result_log = {
        **data,  # 기존 데이터 (Main 결과 등)
        "shadow_response": shadow_response,
        "shadow_latency": shadow_latency,
        "processed_at": time.time()
    }

    collection.insert_one(result_log)
    print(f"Logged to MongoDB: Shadow({shadow_latency:.2f}s) vs Main({data['main_latency']:.2f}s)")