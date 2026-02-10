from litellm import completion
import time
import sys

# 1. 모델 변경: llama3 -> gemma:7b
# (주의: 터미널에서 'ollama pull gemma:7b'를 먼저 실행했어야 합니다)
model_name = "ollama/gemma:7b"

print(f"==========================================")
print(f"💎 PrismOps CLI Chatbot (Model: {model_name})")
print(f"   * System Prompt 없이 순수 모델과 대화합니다.")
print(f"   * 종료하려면 'exit' 또는 'quit'를 입력하세요.")
print(f"==========================================\n")

# 2. 시스템 메시지 없이 빈 리스트로 시작
# (대화의 문맥(Context)은 유지하기 위해 리스트는 사용합니다)
messages = []

while True:
    try:
        user_input = input("USER > ")

        # 종료 명령어 처리
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot을 종료합니다. 👋")
            break

        # 빈 입력 방지
        if not user_input.strip():
            continue

        # 사용자 질문을 대화 기록에 추가
        messages.append({"role": "user", "content": user_input})

        print("AI   > 생각 중...", end="\r")
        start_time = time.time()

        # AI에게 질문 보내기 (전체 대화 기록 포함)
        response = completion(
            model=model_name,
            messages=messages,
            api_base="http://localhost:11434"
        )

        end_time = time.time()

        answer = response.choices[0].message.content

        # 답변 출력
        print(f"\033[KAI   > {answer}")
        print(f"      (⏱️ {end_time - start_time:.2f}s)\n")

        # AI 답변을 대화 기록에 추가 (문맥 유지)
        messages.append({"role": "assistant", "content": answer})

    except KeyboardInterrupt:
        print("\n\n강제 종료합니다. 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}\n")