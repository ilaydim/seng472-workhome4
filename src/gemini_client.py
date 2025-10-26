# src/gemini_client.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.schema import CHATBOT_RESPONSE_SCHEMA
from src.prompts import SYSTEM_PROMPT

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_model():
    # Text-only model (e.g., 'gemini-1.5-pro' veya okulunuzun erişimine uygun olan)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",   # veya "gemini-2.5-pro"
        system_instruction=SYSTEM_PROMPT,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": CHATBOT_RESPONSE_SCHEMA
        }
    )
    return model
