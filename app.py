from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from openai_api import detect_response_type, generate_text, generate_image_from_text, init_mongodb
from datetime import datetime
from contextlib import asynccontextmanager
from middleware import error_handler

import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongodb()  # ✅ MongoDB 초기화
    yield
    # 종료 이벤트가 필요한 경우 추가 가능

app = FastAPI(lifespan=lifespan)
app.middleware("http")(error_handler)


# 요청으로 들어오는 데이터의 구조를 정의하는 Pydantic 모델
class PromptRequest(BaseModel):
    username: str  # 사용자의 고유 ID
    prompt: str   # 사용자가 입력한 질문 또는 명령어

# 텍스트 또는 이미지 생성을 위한 엔드포인트 정의
# app.py 수정
@app.post("/chat")
async def generate_route(data: PromptRequest):
    if not data.prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    response_type = detect_response_type(data.prompt)
    
    # 이미지와 텍스트 생성을 동시에 실행
    tasks = [asyncio.create_task(generate_text(data.username, data.prompt))]  # 텍스트 생성 비동기 실행
    
    if response_type == 'image':
        
        tasks.append(asyncio.create_task(generate_image_from_text(data.username, data.prompt)))  # 이미지 생성도 병렬 실행

    # 모든 태스크가 병렬로 실행되고, 완료될 때까지 기다림
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 결과 처리
    response = {
        'text': results[0] if not isinstance(results[0], Exception) else str(results[0])
    }
    
    if response_type == 'image':
        response['image_url'] = results[1] if not isinstance(results[1], Exception) else None

    return create_response(
        "GENERATED_SUCCESS", 
        "생성 완료", 
        201, 
        response,
        response_type
    )

def create_response(message, details, http_status, data, type):
    response = {
        "timeStamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "code": http_status,
        "message": message,
        "details": details,
        "data": data,
        "type": type
    }
    return JSONResponse(content=response, status_code=200)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host='0.0.0.0', port=5001)
