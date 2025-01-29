from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드
print(f"MongoDB 연결 URL: {os.getenv('MONGO_DB_URL')}")  # 올바르게 로드되었는지 확인
