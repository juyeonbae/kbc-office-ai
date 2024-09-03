# app.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
from openai_api import detect_response_type, generate_text, generate_image_from_text
from io import BytesIO
from datetime import datetime

app = FastAPI()

# import time 
# from loguru import logger
# logger.add("file_{time}.log", rotation="1 day")

# 요청으로 들어오는 데이터의 구조를 정의하는 Pydantic 모델
'''
Pydantic 모델은 FastAPI와 같은 Python 웹 프레임워크에서 
요청(request)으로 들어오는 데이터의 유효성 검사를 간편하게 처리하기 위해 
사용하는 도구

1. 데이터 구조 정의
2. 유효성 검사 

'''
class PromptRequest(BaseModel):
    user_id: str  # 사용자의 고유 ID
    prompt: str   # 사용자가 입력한 질문 또는 명령어

<<<<<<< HEAD
# 텍스트 또는 이미지 생성을 위한 엔드포인트 정의
@app.post("/generate")
=======
@app.post("/chat")
>>>>>>> fa77001d8b376fd68c0f1303e772570dfa854a6c
async def generate_route(data: PromptRequest):
    user_id = data.user_id
    prompt = data.prompt

    if not prompt:
        raise HTTPException(status_code=400, detail="잘못된 입력 값 입니다.")

    # 프롬프트를 분석하여 이미지 생성인지 텍스트 생성인지 판별
    response_type = detect_response_type(prompt)

    try:
        if response_type == 'image':
<<<<<<< HEAD
            # 이미지 생성 작업 비동기 처리 시작
            image_task = asyncio.create_task(generate_image_from_text(user_id, prompt))
            
            # 텍스트 생성 (동시에 처리되지 않고, 차례로 처리됨)
            generated_text = await generate_text(user_id, prompt)
=======
            image_task = asyncio.create_task(generate_image_from_text(prompt))
            #generated_text = await generate_text(prompt)
>>>>>>> fa77001d8b376fd68c0f1303e772570dfa854a6c

            # 이미지 생성 완료 대기
            image = await image_task
            
            # 이미지 생성이 성공적으로 완료된 경우, 이미지를 반환
            if image:
                img_io = BytesIO()
                image.save(img_io, 'PNG')
                img_io.seek(0)
                return StreamingResponse(img_io, media_type="image/png")
            else:
                return create_response("GENERATED_FAILED", "이미지 생성에 실패했습니다.", 500, None)
        else:
<<<<<<< HEAD
            generated_text = await generate_text(user_id, prompt)
            return JSONResponse(content={"generated_text": generated_text})
    
=======
            generated_text = await generate_text(prompt)
            response_data = {"generated_text": generated_text}
            return create_response("GENERATED_SUCCESSFULLY", f"gpt4-o가 생성한 답변입니다.", 201, response_data)
>>>>>>> fa77001d8b376fd68c0f1303e772570dfa854a6c
    except Exception as e:
            print(f"An error occurred: {e}")
            return create_response("GENERATED_FAILED", str(e), 500, None)

def create_response(message, details, http_status, data):
    response = {
        "timeStamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "code": http_status,
        "message": message,
        "details": details,
        "data": data
    }
    return JSONResponse(content=response, status_code=200)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host='0.0.0.0', port=5001)
