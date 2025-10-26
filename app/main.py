import gradio as gr
from src.sql_agent import pipeline

INTRO = "Northwind Chatbot hazır. Türkçe/English sorabilirsiniz. Sadece SELECT sorguları çalışır."

def chat_fn(history, message):
    try:
        result = pipeline(message)
        response_text = result.get("natural_summary") or "No summary available."
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response_text}
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
    chatbot = gr.Chatbot(height=480, type="messages")
    msg = gr.Textbox(placeholder="Örn: 1997 yılında en çok satış yapan 5 müşteri?")
    send = gr.Button("Gönder")
    send.click(chat_fn, inputs=[chatbot, msg], outputs=[chatbot, msg])
    msg.submit(chat_fn, inputs=[chatbot, msg], outputs=[chatbot, msg])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
