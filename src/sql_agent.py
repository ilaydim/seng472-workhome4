# src/sql_agent.py
from src.gemini_client import get_model
from src.db import run_sql

MODEL = get_model()

def ask_llm_for_sql(user_message: str) -> dict:
    """
    LLM'den JSON (sql_query, intent, answer boş) taslağı alır.
    """
    resp = MODEL.generate_content(user_message)
    # resp.text JSON olacak şekilde gelir
    import json
    draft = json.loads(resp.text)
    return draft

def execute_and_fill(draft: dict) -> dict:
    """
    LLM'in ürettiği SQL'i çalıştırır, sonucu draft['answer'] içine doldurur.
    """
    sql = draft.get("sql_query","").strip()
    if not sql.lower().startswith("select"):
        # güvenlik: sadece SELECT
        draft["notes"] = (draft.get("notes","") + " Only SELECT queries are allowed.").strip()
        draft["answer"] = {"columns": [], "rows": []}
        return draft

    result = run_sql(sql)
    draft["answer"] = {
        "columns": result["columns"],
        "rows": result["rows"]
    }
    return draft

def pipeline(user_message: str) -> dict:
    draft = ask_llm_for_sql(user_message)
    final = execute_and_fill(draft)
    return final
