import json
import time
from src.gemini_client import get_model, get_text_model
from src.db import run_sql # run_sql'in columns ve rows döndürdüğünü varsayıyoruz.

MODEL = get_model()           # Structured model (SQL üretimi)
TEXT_MODEL = get_text_model() # Plain text model (açıklama için)

def pipeline(user_message: str) -> dict:
    # --- Aşama 1: SQL Üretimi (Structured Output) ---
    try:
        resp = MODEL.generate_content(user_message)
        # JSONDecodeError'ı yakalamak için try-except bloğu.
        draft = json.loads(resp.text)
    except json.JSONDecodeError:
        return {"natural_summary": "⚠️ LLM'den geçersiz JSON formatı geldi. Sistem komutunu kontrol edin."}
    except Exception as e:
        return {"natural_summary": f"⚠️ LLM SQL üretirken beklenmeyen hata oluştu: {e}"}

    sql = draft.get("sql_query", "").strip()
    if not sql.lower().startswith("select"):
        return {"natural_summary": "❌ Sadece SELECT sorguları desteklenmektedir."}

    # --- SQL Çalıştırma ---
    try:
        result = run_sql(sql)
        draft["answer"] = result
    except Exception as e:
        return {"natural_summary": f"⚠️ SQL çalıştırılırken veritabanı hatası oluştu: {e}"}

    # Eğer sonuç yoksa, LLM'i yormadan direk yanıt ver.
    if not result.get('rows'):
         return {"natural_summary": "Veritabanında sorgunuza uygun sonuç bulunamadı."}

    # --- Aşama 2: Doğal Dil Yorumlama (Prompt İyileştirme) ---
    
    # ❗️ KRİTİK GÜNCELLEME ❗️
    # Modelin doğru dilde, kısa ve özetleyici olmayan bir cevap vermesi için prompt güncellendi.
    summary_prompt = f"""
    You are an expert data analyst and chatbot. 
    
    The user asked the question: "{user_message}"
    
    The following SQL was executed:
    {sql}

    The raw database results (columns: {result['columns']}, rows: {json.dumps(result['rows'], ensure_ascii=False)}) are provided below.
    
    YOUR TASK:
    1. Determine the language of the original question ("{user_message}").
    2. Based on the results, provide a single, concise, and direct answer.
    3. The answer MUST be in the SAME LANGUAGE as the question.
    4. Include specific data points (e.g., names, numbers) from the results in your answer.
    5. DO NOT start with phrases like "Bu sonuçlar göstermektedir ki..." or "Based on the results...".
    """

    try:
        summary_resp = TEXT_MODEL.generate_content(summary_prompt)
        text = summary_resp.text.strip()
        
        # İlk yanıt boşsa 0.5 saniye bekleyip tekrar dene (timeout fix)
        if not text:
            time.sleep(0.5)
            summary_resp = TEXT_MODEL.generate_content(summary_prompt)
            text = summary_resp.text.strip() or "Sonuç açıklaması bulunamadı."
    except Exception as e:
        text = f"⚠️ LLM açıklama üretirken hata oluştu: {e}"

    draft["natural_summary"] = text
    return draft
