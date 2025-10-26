import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.schema import CHATBOT_RESPONSE_SCHEMA
from src.prompts import SYSTEM_PROMPT

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_model():
    """Structured JSON output için (SQL üretimi)"""
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": CHATBOT_RESPONSE_SCHEMA
        }
    )

def get_text_model():
    """Natural language explanation için (plain text)"""
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={"response_mime_type": "text/plain"}
    )
