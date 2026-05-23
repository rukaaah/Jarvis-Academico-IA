import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

client = OpenAI(base_url=API_URL, api_key=API_KEY)

def call_llm(messages, temperature=0.3):
    response = client.chat.completions.create(
        model='google/gemma-3-12b-it',
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content