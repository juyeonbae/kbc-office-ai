import logging
import traceback
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime


# 로거 설정
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# 환경 변수에서 MongoDB URL 가져오기
db_url = os.getenv("MONGO_DB_URL", "mongodb://localhost:27017")

# 확인용 로그
print(f"MongoDB 연결 URL: {db_url}")
logger.info(f"MongoDB 연결 URL: {db_url}")

class HistoryService:
    def __init__(self, db_url: str):
        try:
            logger.info("MongoDB 연결 시도")
            self.client = AsyncIOMotorClient(db_url)
            self.db = self.client.chatbot
            self.collection = self.db.history  # history 컬렉션 지정
            logger.info("MongoDB 클라이언트 초기화 완료")

        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}\n{traceback.format_exc()}")
            raise

    async def check_connection(self) -> bool:
        """MongoDB 연결 테스트"""
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}\n{traceback.format_exc()}")
            return False

    async def get_history(self, username: str):
        """사용자의 최근 5개 대화 히스토리 가져오기"""
        history_cursor = self.collection.find({"username": username}).sort("timestamp", -1).limit(5)
        history = await history_cursor.to_list(length=5)
        return history

    async def save_history(self, username: str, question: str, answer: str):
        """대화 기록 저장"""
        await self.collection.insert_one({
            "username": username,
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow()
        })

async def initialize_mongodb():
    """MongoDB 초기화"""
    if not db_url:
        logger.error("MONGO_DB_URL 환경 변수가 없음")
        raise ValueError("MONGO_DB_URL 환경 변수가 없음")

    service = HistoryService(db_url)
    if await service.check_connection():
        return service
    raise ConnectionError("MongoDB 연결 실패")
