from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
from openai_api import detect_response_type, generate_text, generate_image_from_text
from io import BytesIO

import time 
from loguru import logger

app = FastAPI()

logger.add("file_{time}.log", rotation="1 day")

# 응답 시간 체크 
'''
@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.time() 
    response = await call_next(request)
    process_time = time.time() - start_time  
    logger.info(f"Request: {request.method} {request.url} - Process time: {process_time:.4f} seconds")
    return response
'''

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_route(data: PromptRequest):
    prompt = data.prompt

    if not prompt:
        raise HTTPException(status_code=400, detail="프롬프트가 제공되지 않았습니다.")

    response_type = detect_response_type(prompt)

    try:
        if response_type == 'image':
            image_task = asyncio.create_task(generate_image_from_text(prompt))
            generated_text = await generate_text(prompt)

            image = await image_task
            if image:
                img_io = BytesIO()
                image.save(img_io, 'PNG')
                img_io.seek(0)
                return StreamingResponse(img_io, media_type="image/png")
            else:
                raise HTTPException(status_code=500, detail="이미지 생성에 실패했습니다.")
        else:
            generated_text = await generate_text(prompt)
            return JSONResponse(content={"generated_text": generated_text})
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("testapp:app", host='0.0.0.0', port=5001)
