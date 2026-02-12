# frontend/app.py
import streamlit as st
import requests
import time

# === 1. 페이지 설정 ===
st.set_page_config(
    page_title="PrismOps",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 2. CSS 스타일링 (Gemini-C 스타일 적용) ===
# 구글 Gemini 특유의 깔끔한 카드 디자인과 폰트 스타일을 적용합니다.
st.markdown("""
<style>
    /* 메인 배경색 */
    .stApp {
        background-color: #ffffff;
        color: #1f1f1f;
    }

    /* 입력창 스타일 */
    .stChatInput {
        border-radius: 20px;
    }

    /* 추천 질문 카드 스타일 */
    .suggestion-card {
        background-color: #f0f4f9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .suggestion-card:hover {
        background-color: #e1e5ea;
        transform: scale(1.02);
    }

    /* 그라데이션 텍스트 */
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #4285f4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 3em;
    }

    /* 채팅 메시지 버블 제거 (깔끔하게) */
    .stChatMessage {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# === 3. 사이드바 (기록 및 설정) ===
with st.sidebar:
    st.title("PrismOps")
    st.markdown("---")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 🕒 Recent History")
    st.caption("대화 기록이 이곳에 표시됩니다.")
    # (추후 DB 연동 시 여기에 목록 표시)

# === 4. 세션 초기화 ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# === 5. 메인 화면 로직 ===

# 대화 기록이 없으면 -> '초기 환영 화면' 표시 (Gemini 스타일)
if not st.session_state.messages:
    st.markdown("<div class='gradient-text'>안녕하세요!</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #444746;'>무엇을 도와드릴까요?</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # 추천 질문 카드 (클릭은 안되지만 디자인 요소로 배치)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='suggestion-card'>
            <b>💻 Code Refactoring</b><br>
            <span style='font-size:0.8em'>Optimize this Python script...</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='suggestion-card'>
            <b>🚀 System Architecture</b><br>
            <span style='font-size:0.8em'>Design a scalable system...</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='suggestion-card'>
            <b>📊 Data Analysis</b><br>
            <span style='font-size:0.8em'>Analyze this CSV file...</span>
        </div>
        """, unsafe_allow_html=True)

# 대화 기록이 있으면 -> 채팅창 표시
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "💎"):
            st.markdown(message["content"])
            if "metadata" in message:
                meta = message["metadata"]
                st.caption(f"🏷️ {meta['model']} | ⏱️ {meta['latency']}s")

# === 6. 로직 처리 (백엔드 통신) ===
if prompt := st.chat_input("Enter a prompt here"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # AI 응답
    with st.chat_message("assistant", avatar="💎"):
        message_placeholder = st.empty()

        # 로딩 표시 (Gemini 스타일 스피너)
        with st.spinner("Generating..."):
            try:
                # Docker 통신
                api_url = "http://prism-app:8000/chat"
                response = requests.post(api_url, json={"message": prompt})

                if response.status_code == 200:
                    data = response.json()
                    reply = data["reply"]

                    # 스트리밍 효과
                    full_response = ""
                    for chunk in reply.split(" "):
                        full_response += chunk + " "
                        time.sleep(0.05)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)

                    # 메타데이터 표시
                    st.caption(f"🏷️ {data['model']} | ⏱️ {data['latency']}s")

                    # 기록 저장
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "metadata": {"model": data["model"], "latency": data["latency"]}
                    })
                else:
                    message_placeholder.error(f"Error: {response.status_code}")
            except Exception as e:
                message_placeholder.error(f"Connection Failed: {e}")