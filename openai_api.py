# openai_api.py
import openai
from dotenv import load_dotenv
import os, requests
from googletrans import Translator
from io import BytesIO
from PIL import Image

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

translator = Translator()

def generate_text(prompt, model_name='gpt-4o-mini'):
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    return response.choices[0].message['content']

def generate_image_from_text(kr_prompt):
    translated_prompt = translator.translate(kr_prompt, src='ko', dest='en').text
    try:
        response = openai.Image.create(
            prompt=translated_prompt,
            n=1, 
            size="256x256", 
            model = "dall-e-2"
        )

        image_url = response['data'][0]['url']

        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))

        return image
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None