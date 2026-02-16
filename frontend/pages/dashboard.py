import streamlit as st
import pandas as pd
import requests
import os
import time

# 페이지 설정
st.set_page_config(page_title="Shadow Dashboard", page_icon="📊", layout="wide")

st.title("📊 Shadow Mode Dashboard")
st.caption("Real-time comparison between Main Model & Shadow Model")

# 백엔드 URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://prism-gateway:8000")


def load_data():
    try:
        response = requests.get(f"{BACKEND_URL}/logs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "ok":
                return data["logs"]
        return []
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return []


# 새로고침 버튼
if st.button("🔄 데이터 새로고침"):
    st.rerun()

# 데이터 가져오기
logs = load_data()

if logs:
    # 데이터 전처리 (Pandas DataFrame 변환)
    df = pd.DataFrame(logs)

    # 시간 포맷 변환 (timestamp -> datetime)
    if 'timestamp' in df.columns:
        df['Time'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.sort_values('Time', ascending=False)

    # 1. KPI 지표 (Key Performance Indicators)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Requests", len(df))
    with col2:
        avg_main = df['main_latency'].mean() if 'main_latency' in df.columns else 0
        st.metric("Avg Main Latency", f"{avg_main:.4f}s")
    with col3:
        avg_shadow = df['shadow_latency'].mean() if 'shadow_latency' in df.columns else 0
        st.metric("Avg Shadow Latency", f"{avg_shadow:.4f}s")

    st.divider()

    # 2. 성능 비교 차트 (Latency Comparison)
    st.subheader("⚡ Latency Comparison (Main vs Shadow)")
    if 'main_latency' in df.columns and 'shadow_latency' in df.columns:
        chart_data = df[['Time', 'main_latency', 'shadow_latency']].set_index('Time')
        st.line_chart(chart_data)

    st.divider()

    # 3. 상세 로그 테이블
    st.subheader("📝 Request Logs")

    # 보여줄 컬럼 선택 및 정리
    display_cols = ['Time', 'prompt', 'main_model', 'shadow_model', 'main_latency', 'shadow_latency']
    # 실제 데이터에 있는 컬럼만 선택
    valid_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(
        df[valid_cols],
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("아직 데이터가 없습니다. 채팅을 먼저 시작해보세요!")