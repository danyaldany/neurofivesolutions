"""
Neurofive Solutions RAG Resume Chatbot
Professional Gradio UI version — FIXED
"""

import os
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types
import gradio as gr
import faiss

try:
    import PyPDF2
    PDF_READER = "PyPDF2"
except ImportError:
    from pypdf import PdfReader
    PDF_READER = "pypdf"

# Load env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-3.6-flash"

# Global store
store = None
store_ready = False


def extract_text(pdf_path):
    text = ""
    if PDF_READER == "PyPDF2":
        with open(pdf_path, 'rb') as f:
            for page in PyPDF2.PdfReader(f).pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    else:
        for page in PdfReader(pdf_path).pages:
            text += page.extract_text() + "\n"
    return text.strip()


def chunk_text(text, size=800, overlap=100):
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end - overlap > start else end
    return chunks


def get_embeddings(texts):
    if isinstance(texts, str):
        texts = [texts]
    all_emb = []
    for i in range(0, len(texts), 100):
        batch = texts[i:i + 100]
        resp = client.models.embed_content(model=EMBEDDING_MODEL, contents=batch)
        for e in resp.embeddings:
            all_emb.append(e.values)
    return np.array(all_emb, dtype='float32')


class VectorStore:
    def __init__(self):
        self.index, self.chunks, self.dim = None, [], None

    def build(self, chunks):
        self.chunks = chunks
        emb = get_embeddings(chunks)
        self.dim = emb.shape[1]
        self.index = faiss.IndexFlatL2(self.dim)
        self.index.add(emb)
        return self

    def search(self, query, k=3):
        qe = get_embeddings([query])
        _, idx = self.index.search(qe, k)
        return [self.chunks[i] for i in idx[0] if i < len(self.chunks)]


def process_resume(pdf_file):
    global store, store_ready
    if pdf_file is None:
        return "❌ Please upload a PDF file."

    text = extract_text(pdf_file)
    chunks = chunk_text(text)
    store = VectorStore()
    store.build(chunks)
    store_ready = True

    return f"✅ Resume processed!\n\n📄 Characters: {len(text)}\n📦 Chunks: {len(chunks)}\n\nReady to chat."


def chat(query, history):
    global store_ready
    if not store_ready:
        history.append({
            "role": "assistant",
            "content": "⚠️ Please upload your resume first!"
        })
        return history

    if not query.strip():
        return history

    history.append({"role": "user", "content": query})
    yield history

    try:
        relevant = store.search(query, k=3)
        context = "\n\n---\n\n".join(relevant)

        prompt = f"""You are a helpful assistant. Answer STRICTLY from the resume context below. 
If the answer is not in the context, say 'I don't see that information in your resume.'

RESUME CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

        response = client.models.generate_content(
            model=CHAT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=1024)
        )

        history.append({"role": "assistant", "content": response.text})

    except Exception as e:
        history.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})

    yield history


def clear_chat():
    return []


# ============================================================
# Gradio UI — msg_input DEFINED BEFORE buttons that reference it
# ============================================================
with gr.Blocks(title="Neurofive RAG Resume") as demo:
    gr.HTML("""
    <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);padding:24px 32px;border-radius:16px;margin-bottom:20px;">
        <h1 style="color:#f8fafc;margin:0;font-size:1.7rem;">📄 Neurofive RAG Resume Chatbot</h1>
        <p style="color:#94a3b8;margin:8px 0 0 0;">Upload your resume and ask questions. Answers grounded in YOUR data.</p>
    </div>
    """)

    with gr.Row():
        # ============ LEFT SIDEBAR ============
        with gr.Column(scale=1):
            pdf_input = gr.File(label="Upload Resume (PDF)", file_types=[".pdf"])
            process_btn = gr.Button("📤 Process Resume", variant="primary")
            status = gr.Textbox(label="Status", interactive=False, lines=3)

            gr.Markdown("### 📝 Example Questions")

            # Example questions list
            examples = [
                "What is my highest education?",
                "What programming languages do I know?",
                "What was my last job role?",
                "Do I have any certifications?",
                "What projects have I worked on?",
            ]

        # ============ RIGHT CHAT AREA ============
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=500, value=[])
            # msg_input DEFINED HERE — before any button references it
            msg_input = gr.Textbox(
                placeholder="Ask about your resume...",
                show_label=False
            )
            with gr.Row():
                send_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear")

    # ============ EVENT BINDINGS ============
    process_btn.click(process_resume, inputs=pdf_input, outputs=status)

    # Send on Enter
    msg_input.submit(
        chat, inputs=[msg_input, chatbot], outputs=chatbot
    ).then(lambda: "", outputs=msg_input)

    # Send on button click
    send_btn.click(
        chat, inputs=[msg_input, chatbot], outputs=chatbot
    ).then(lambda: "", outputs=msg_input)

    # Clear chat
    clear_btn.click(clear_chat, outputs=chatbot)

    # ============ EXAMPLE BUTTONS (after msg_input is defined) ============
    for ex in examples:
        ex_btn = gr.Button(ex, size="sm")
        ex_btn.click(lambda x=ex: x, outputs=msg_input)


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        inbrowser=True
    )