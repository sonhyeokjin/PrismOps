# frontend/app.py
import streamlit as st
import requests
import time

# 페이지 설정
st.set_page_config(page_title="PrismOps Chat", page_icon="💎")

st.title("💎 PrismOps AI Chat")
st.caption("🚀 Powered by Ollama & OpenAI with A/B Routing")

# 세션 상태 초기화 (대화 기록 저장)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 1. 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. API 호출
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            # Docker 내부 통신용 URL (prism-app 컨테이너를 가리킴)
            # 주의: 브라우저가 아니라 '컨테이너'가 요청을 보내므로 localhost가 아님!
            api_url = "http://prism-app:8000/chat"

            payload = {"message": prompt}
            response = requests.post(api_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                reply = data["reply"]
                model = data["model"]
                latency = data["latency"]

                # 답변 표시 (모델 정보와 지연시간도 함께)
                full_response = f"{reply}\n\n---\n*🏷️ Model: `{model}` | ⏱️ Latency: `{latency}s`*"
                message_placeholder.markdown(full_response)

                # 대화 기록에 저장
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                message_placeholder.error(f"Error: {response.status_code}")

        except Exception as e:
            message_placeholder.error(f"Connection Failed: {str(e)}")