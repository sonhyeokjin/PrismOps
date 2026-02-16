import streamlit as st
import requests
import os
import time

# ----------------------------------------------------------------
# 1. 기본 설정 (심플하게)
# ----------------------------------------------------------------
st.set_page_config(
    page_title="PrismOps Chat",
    page_icon="💎",
    layout="centered"
)

st.title("💎 PrismOps Chat")
st.caption("Shadow Mode Enabled Architecture")

# [중요] 백엔드 연결 주소 설정 (이 부분은 유지해야 연결이 됩니다!)
BACKEND_URL = os.getenv("BACKEND_URL", "http://prism-gateway:8000")

# ----------------------------------------------------------------
# 2. 세션 상태 초기화 (대화 기록)
# ----------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 기록 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------------------------------------
# 3. 채팅 로직
# ----------------------------------------------------------------
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 표시 및 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # 백엔드 호출
            payload = {
                "message": prompt,
                "model": "gpt-4o-mini"  # 기본 모델
            }

            with st.spinner("답변 생성 중..."):
                response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "")
                latency = result.get("latency", 0.0)

                # 스트리밍 효과 (한 글자씩 출력)
                for chunk in answer.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                # 심플하게 메타데이터 표시
                st.info(f"⚡ Latency: {latency:.2f}s | 🤖 Model: {result.get('model')}")

            else:
                st.error(f"서버 오류: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error("🚨 서버 연결 실패")
            st.caption(f"연결 시도 주소: `{BACKEND_URL}`")
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")

    # 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})