# logger.py
import json
from datetime import datetime
from backend import config


def log_transaction(data: dict):
    """
    트래픽 정보를 받아서 JSONL 파일에 한 줄씩 추가합니다.
    이 함수는 BackgroundTask로 실행되므로 메인 응답을 막지 않습니다.
    """
    try:
        # 1. 타임스탬프 추가
        data["timestamp"] = datetime.now().isoformat()

        # 2. JSON 문자열로 변환 (한글 깨짐 방지 ensure_ascii=False)
        json_line = json.dumps(data, ensure_ascii=False)

        # 3. 파일에 이어쓰기 모드('a')로 저장
        with open(config.LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json_line + "\n")

        print(f"📝 [LOG] {data['model']} used ({data['latency']}s)")

    except Exception as e:
        print(f"❌ [LOG ERROR] 로그 저장 실패: {e}")