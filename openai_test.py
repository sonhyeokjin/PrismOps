# openai_test.py
from litellm import completion
import os
from dotenv import load_dotenv  # ✨ 1. 라이브러리 불러오기

# ✨ 2. .env 파일 로드 (이 함수가 실행되면 .env 안의 내용이 환경변수로 등록됨)
load_dotenv()

# 3. API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    print("❌ 오류: .env 파일을 찾을 수 없거나 OPENAI_API_KEY가 없습니다.")
    exit()

print(f"🔑 API Key 로드 성공! (앞 5자리: {os.getenv('OPENAI_API_KEY')[:5]}...)")
print("🚀 OpenAI (GPT-4o-mini)에게 질문을 보냅니다...")

try:
    response = completion(
        model="gpt-4o-mini",
        messages=[{ "content": "안녕? 너는 .env 파일에서 키를 잘 읽어왔니?", "role": "user"}]
    )

    print(f"✅ 답변: {response.choices[0].message.content}")

except Exception as e:
    print(f"❌ 호출 실패: {e}")