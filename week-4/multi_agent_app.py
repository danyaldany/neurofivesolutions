"""
Neurofive Solutions Week 4 — Multi-Agent Pipeline
Streamlit UI — Clean, Professional, Works Perfectly
"""

import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

# ============================================================
# 1. Load Environment
# ============================================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found in .env")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.6-flash"

# ============================================================
# 2. Agent Prompts
# ============================================================
WRITER_PROMPT = (
    "You are a skilled Content Writer. "
    "Draft clear, engaging content on any topic. "
    "Include intro, 2-3 key points, and conclusion. "
    "Output ONLY the draft content."
)

EDITOR_PROMPT = (
    "You are a senior Editor. "
    "Review drafts for clarity, structure, tone, and completeness. "
    "Fix grammar, improve transitions, strengthen arguments. "
    "Output the FINAL polished version only."
)

# ============================================================
# 3. Agent Functions
# ============================================================
def agent_writer(topic: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=f"Write about: {topic}",
        config=types.GenerateContentConfig(
            system_instruction=WRITER_PROMPT,
            temperature=0.7,
            max_output_tokens=2048
        )
    )
    return response.text.strip()


def agent_editor(draft: str, topic: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=f"TOPIC: {topic}\n\nDRAFT:\n\"\"\"{draft}\"\"\"\n\nImprove this draft. Output final polished version only.",
        config=types.GenerateContentConfig(
            system_instruction=EDITOR_PROMPT,
            temperature=0.3,
            max_output_tokens=2048
        )
    )
    return response.text.strip()


# ============================================================
# 4. Streamlit Page Config
# ============================================================
st.set_page_config(
    page_title="Neurofive Multi-Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Light sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #334155;
    }
    
    /* Main area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Cards */
    .writer-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border-left: 4px solid #3b82f6;
    }
    
    .editor-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        border-left: 4px solid #22c55e;
    }
    
    .card-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 12px;
        color: #0f172a;
    }
    
    .card-body {
        font-size: 0.95rem;
        line-height: 1.7;
        color: #334155;
        white-space: pre-wrap;
    }
    
    .stats-bar {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #f1f5f9;
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 14px 18px;
        font-size: 0.95rem;
    }
    
    .stButton > button {
        background: #0f172a;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 500;
        border: none;
    }
    
    .stButton > button:hover {
        background: #1e293b;
    }
    
    /* History items */
    .history-item {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #475569;
        cursor: pointer;
    }
    
    .history-item:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 5. Sidebar
# ============================================================
with st.sidebar:
    st.markdown("### 💬 Chat History")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if len(st.session_state.chat_history) == 0:
        st.markdown('<div style="color: #94a3b8; font-size: 0.85rem; padding: 10px;">No chats yet</div>', unsafe_allow_html=True)
    else:
        for i, topic in enumerate(st.session_state.chat_history):
            display = topic[:35] + "..." if len(topic) > 35 else topic
            st.markdown(f'<div class="history-item">{display}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎭 Agents")
    st.markdown("✍️ **Writer** — drafts content")
    st.markdown("🔍 **Editor** — polishes output")
    
    if st.button("🗑️ New Chat", use_container_width=True):
        st.session_state.chat_history = []
        if "current_topic" in st.session_state:
            del st.session_state.current_topic
        if "draft" in st.session_state:
            del st.session_state.draft
        if "final" in st.session_state:
            del st.session_state.final
        st.rerun()

# ============================================================
# 6. Main Area
# ============================================================

# Input at bottom using columns
col1, col2 = st.columns([6, 1])

with col1:
    topic = st.text_input(
        "Enter topic",
        placeholder="Enter a topic (e.g., The Future of AI in Healthcare)...",
        label_visibility="collapsed",
        key="topic_input"
    )

with col2:
    generate = st.button("Generate", use_container_width=True)

# Process
if generate and topic.strip():
    with st.spinner("✍️ Writer drafting... 🔍 Editor reviewing..."):
        draft = agent_writer(topic)
        final = agent_editor(draft, topic)
        
        st.session_state.current_topic = topic
        st.session_state.draft = draft
        st.session_state.final = final
        st.session_state.chat_history.append(topic)
        st.rerun()

# Display output
if "draft" in st.session_state and "final" in st.session_state:
    st.markdown(f"""
    <div class="writer-card">
        <div class="card-title">✍️ Writer Draft</div>
        <div class="card-body">{st.session_state.draft}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="editor-card">
        <div class="card-title">🔍 Editor Final</div>
        <div class="card-body">{st.session_state.final}</div>
        <div class="stats-bar">📊 {len(st.session_state.draft.split())} → {len(st.session_state.final.split())} words | ✅ Publication Ready</div>
    </div>
    """, unsafe_allow_html=True)
    
else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 80px 20px; color: #94a3b8;">
        <div style="font-size: 2.5rem; margin-bottom: 16px;">💬</div>
        <div style="font-size: 1.1rem; font-weight: 500; color: #64748b; margin-bottom: 8px;">Start a conversation</div>
        <div style="font-size: 0.9rem;">Enter a topic below and click Generate</div>
    </div>
    """, unsafe_allow_html=True)