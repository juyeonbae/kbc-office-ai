# openai_api.py

import openai, os, asyncio
from googletrans import Translator
from fastapi import HTTPException
from dotenv import load_dotenv
import logging
from dotenv import load_dotenv
from history_service import initialize_mongodb  # initialize_mongodb 함수 추가

# .env 파일 로드
load_dotenv()
print(f"MongoDB URL in openai_api.py: {os.getenv('MONGO_DB_URL')}")


# 환경 변수에서 OpenAI API 키 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")

# 로거 설정
logger = logging.getLogger(__name__)

translator = Translator()

# 전역 변수로 history_service 선언
history_service = None

# MongoDB 초기화 함수
async def init_mongodb():
    global history_service
    try:
        history_service = await initialize_mongodb()
    except Exception as e:
        logger.error(f"MongoDB 초기화 실패: {str(e)}")
        raise

# 비동기 번역 함수
async def translate_text(kr_prompt):
    loop = asyncio.get_event_loop()
    translated = await loop.run_in_executor(None, translator.translate, kr_prompt, 'en')
    return translated.text

# 이미지 생성 관련 함수
async def fetch_image(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        else:
            raise HTTPException(status_code=500, detail=f"Failed to download image, status code: {response.status}")


async def generate_image_from_text(username, kr_prompt):
    try:
        translation_task = asyncio.create_task(translate_text(kr_prompt))  # ✅ 프롬프트 번역을 비동기로 실행
        
        await translation_task  # ✅ 번역 완료 대기
        translated_prompt = translation_task.result()

        response = await openai.Image.acreate(
            prompt=translated_prompt,
            n=1,
            size='1024x1024',
            model='dall-e-3',
            quality='hd'
        )

        image_url = response['data'][0]['url']
        
        # 비동기로 히스토리 저장
        asyncio.create_task(history_service.save_history(username, kr_prompt, image_url))  # ✅ 히스토리 저장을 비동기 실행
        
        return image_url
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
# 텍스트 생성 관련 함수
async def generate_text(username, prompt, model_name='gpt-4o-mini'):
    # 사용자 히스토리 가져오기
    print(f"🔵 [generate_text] 시작: {prompt}")
    history_task = asyncio.create_task(history_service.get_history(username))  # 비동기 실행 (히스토리 가져오기)

    history = await history_task
    print(f"🟢 [generate_text] 히스토리 로드 완료")

    # 이전 대화 기록을 바탕으로 대화 문맥을 유지하는 프롬프트 생성
    context = ""
    for entry in history[-5:]:  # 최근 5개의 대화만 가져와 문맥 생성 -> 범위는 조정하면 됨 
        context += f"User: {entry['question']}\nAssistant: {entry['answer']}\n"

    # 새로운 질문과 결합
    full_prompt = f"{context}User: {prompt}\nAssistant:"

    response = await openai.ChatCompletion.acreate(  # GPT 호출 (비동기)
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=500 # 최대 답변 생성 길이 
    )
    print(f"🟢 [generate_text] 응답 완료")

    generated_text = response['choices'][0]['message']['content']

    # 히스토리 저장 (질문과 생성된 텍스트 저장)
    await history_task  # ✅ 히스토리 가져오기 완료 대기
    asyncio.create_task(history_service.save_history(username, prompt, generated_text))  # ✅ 히스토리 저장을 백그라운드에서 실행

    return generated_text

# 응답 타입 감지 함수
def detect_response_type(prompt):
    image_keywords = ['그림', '이미지', '사진', '그려줘', '그려', '그림으로', '사진으로', '이미지로']
    if any(keyword in prompt for keyword in image_keywords):
        return 'image'
    else:
        return 'text'
