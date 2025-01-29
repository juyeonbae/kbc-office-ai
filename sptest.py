import asyncio
import time
from openai_api import generate_text, generate_image_from_text, init_mongodb  # init_mongodb 추가

USERNAME = "test_user"
PROMPT_TEXT = "Explain the theory of relativity."
PROMPT_IMAGE = "그려줘 우주 속의 블랙홀"

async def sequential_execution():
    """ 기존 순차 실행 방식 (텍스트 → 이미지 순서대로 실행) """
    start_time = time.perf_counter()
    text_response = await generate_text(USERNAME, PROMPT_TEXT)
    image_response = await generate_image_from_text(USERNAME, PROMPT_IMAGE)
    elapsed_time = time.perf_counter() - start_time
    return elapsed_time

async def parallel_execution():
    """ 개선된 병렬 실행 방식 (텍스트와 이미지를 동시에 실행) """
    start_time = time.perf_counter()
    text_task = asyncio.create_task(generate_text(USERNAME, PROMPT_TEXT))
    image_task = asyncio.create_task(generate_image_from_text(USERNAME, PROMPT_IMAGE))
    
    text_response, image_response = await asyncio.gather(text_task, image_task)
    
    elapsed_time = time.perf_counter() - start_time
    return elapsed_time

async def benchmark():
    global history_service  # 전역 변수 사용
    
    print("🔵 MongoDB 초기화 시작")
    await init_mongodb()  # ✅ MongoDB 초기화
    print("✅ MongoDB 초기화 완료")

    num_trials = 10
    seq_times = []
    par_times = []

    for _ in range(num_trials):
        print(f"🔄 실행 {_+1}/{num_trials} (순차 실행)")
        seq_time = await sequential_execution()
        seq_times.append(seq_time)

        print(f"🔄 실행 {_+1}/{num_trials} (병렬 실행)")
        par_time = await parallel_execution()
        par_times.append(par_time)

    avg_seq_time = sum(seq_times) / num_trials
    avg_par_time = sum(par_times) / num_trials

    print(f"기존 순차 실행 평균 시간: {avg_seq_time:.2f}초")
    print(f"개선된 병렬 실행 평균 시간: {avg_par_time:.2f}초")
    print(f"속도 향상 비율: {avg_seq_time / avg_par_time:.2f}배")
    """ 10회 실행 후 평균 실행 시간 비교 """
    global history_service  # 전역 변수 사용
    
    await init_mongodb()  # ✅ MongoDB 초기화 (해결책)

    num_trials = 10
    seq_times = []
    par_times = []

    for _ in range(num_trials):
        seq_time = await sequential_execution()
        seq_times.append(seq_time)
        
        par_time = await parallel_execution()
        par_times.append(par_time)

    avg_seq_time = sum(seq_times) / num_trials
    avg_par_time = sum(par_times) / num_trials

    print(f"기존 순차 실행 평균 시간: {avg_seq_time:.2f}초")
    print(f"개선된 병렬 실행 평균 시간: {avg_par_time:.2f}초")
    print(f"속도 향상 비율: {avg_seq_time / avg_par_time:.2f}배")

# 실행
asyncio.run(benchmark())

'''
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(benchmark())
    except RuntimeError as e:
        print(f"❌ RuntimeError 발생: {e}")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(benchmark())

'''