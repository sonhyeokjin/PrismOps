# config.py
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# === 모델 설정 ===
# Local Model (비용 0원)
MODEL_A = "ollama/gemma:7b"

# Cloud Model (유료/고성능)
# OpenAI가 있으면 아래 주석을 풀고 사용하세요.
MODEL_B = "gpt-4o-mini"
# MODEL_B = "gemini/gemini-1.5-flash"

# === 라우팅 설정 ===
# Model B로 보낼 확률 (0.5 = 50%)
ROUTING_RATIO = 0.5

# === 로그 파일 경로 ===
LOG_FILE_PATH = "traffic_log.jsonl"