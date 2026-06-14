import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

client = OpenAI(base_url=API_URL, api_key=API_KEY)

def call_llm(messages, temperature=0.3):
    response = client.chat.completions.create(
        # model='Qwen/Qwen2.5-14B-Instruct-AWQ',
        model='gemini-2.5-pro',
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content