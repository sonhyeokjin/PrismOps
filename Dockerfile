# 1. 베이스 이미지 선택 (가볍고 안정적인 Python 3.9 Slim 버전)
FROM python:3.9-slim

# 2. 작업 디렉토리 설정 (컨테이너 내부의 폴더명)
WORKDIR /app

# 3. 필수 패키지 설치
# (캐시 효율을 위해 requirements.txt만 먼저 복사해서 설치합니다)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사 (내 컴퓨터 -> 컨테이너)
COPY . .

# 5. 포트 노출 (FastAPI 기본 포트)
EXPOSE 8000

# 6. 실행 명령어 (서버 켜기)
# --host 0.0.0.0: 외부에서 접속 가능하게 설정 (필수!)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]