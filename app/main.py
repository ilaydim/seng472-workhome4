import gradio as gr
import json
from src.sql_agent import pipeline

INTRO = "Northwind Chatbot hazır. Türkçe/English sorabilirsiniz. Sadece SELECT sorguları çalışır."

def chat_fn(history, message):
    try:
        result = pipeline(message)
        natural_response = format_response(result, message)
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": natural_response}
        ]
        return history, ""
    except Exception as e:
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": f"⚠️ Hata: {e}"}
        ]
        return history, ""

with gr.Blocks(title="Northwind Chatbot") as demo:
    gr.Markdown(f"### {INTRO}")

    # Yeni format: messages tipi
    chatbot = gr.Chatbot(height=480, type="messages")
    msg = gr.Textbox(placeholder="Örn: 1997 yılında en çok satış yapan 5 müşteri?")
    send = gr.Button("Gönder")

    # Gönderim fonksiyonu
    send.click(chat_fn, inputs=[chatbot, msg], outputs=[chatbot, msg])
    msg.submit(chat_fn, inputs=[chatbot, msg], outputs=[chatbot, msg])

def format_response(result: dict, user_message: str = "") -> str:
    """AI'nin JSON çıktısını kullanıcıya doğal (TR/EN) cümleyle gösterir."""
    try:
        rows = result["answer"]["rows"]
        if not rows:
            if user_message.strip().startswith(("ne", "kim", "kaç", "hangi")):
                return "Hiç sonuç bulunamadı."
            else:
                return "No results found."

        first = rows[0]
        # Kullanıcının dilini otomatik tespit et (çok basit heuristic)
        is_turkish = any(ch in "ığüşöçİĞÜŞÖÇ" for ch in user_message) or user_message.lower().startswith(
            ("ne", "hangi", "kaç", "en", "listele", "göster", "yıl")
        )

        if "CustomerName" in first and "TotalSales" in first:
            name = first["CustomerName"]
            sales = round(first["TotalSales"], 2)
            if is_turkish:
                return f"1997 yılının en çok satış yapan müşterisi **{name}**, toplam satış tutarı **{sales}**."
            else:
                return f"The top customer in 1997 was **{name}**, with total sales of **{sales}**."

        cols = result["answer"]["columns"]
        preview = ", ".join(cols[:3])
        if is_turkish:
            return f"{len(rows)} sonuç bulundu. Sütunlar: {preview}."
        else:
            return f"I found {len(rows)} results. Columns: {preview}."
    except Exception:
        return f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

