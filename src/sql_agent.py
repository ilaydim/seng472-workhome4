import json
import time
from src.gemini_client import get_model, get_text_model
from src.db import run_sql

MODEL = get_model()          # Structured model (SQL üretimi)
TEXT_MODEL = get_text_model() # Plain text model (açıklama için)

def pipeline(user_message: str) -> dict:
    try:
        resp = MODEL.generate_content(user_message)
        draft = json.loads(resp.text)
    except Exception as e:
        return {"natural_summary": f"⚠️ LLM SQL üretirken hata oluştu: {e}"}

    sql = draft.get("sql_query", "").strip()
    if not sql.lower().startswith("select"):
        return {"natural_summary": "❌ Sadece SELECT sorguları desteklenmektedir."}

    # SQL çalıştır
    try:
        result = run_sql(sql)
        draft["answer"] = result
    except Exception as e:
        return {"natural_summary": f"⚠️ SQL çalıştırılırken hata oluştu: {e}"}

    # Natural explanation prompt
    summary_prompt = f"""
    You are a helpful data analyst.
    SQL Query executed successfully:
    {sql}

    Query result:
    {json.dumps(result['rows'], ensure_ascii=False, indent=2)}

    The user asked:
    "{user_message}"

    Explain the meaning of these results in the SAME LANGUAGE as the question.
    Respond as a short, natural sentence.
    """

    try:
        summary_resp = TEXT_MODEL.generate_content(summary_prompt)
        text = summary_resp.text.strip()
        if not text:
            time.sleep(0.5)
            summary_resp = TEXT_MODEL.generate_content(summary_prompt)
            text = summary_resp.text.strip() or "Sonuç açıklaması bulunamadı."
    except Exception as e:
        text = f"⚠️ LLM açıklama üretirken hata oluştu: {e}"

    draft["natural_summary"] = text
    return draft
