"""
Neurofive Solutions Week 3 — Structured JSON Output
Beautiful Gradio UI — COMPLETELY FIXED
"""

import os
import json
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import gradio as gr

# ============================================================
# 1. Load Environment
# ============================================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.6-flash"


# ============================================================
# 2. JSON Schema — NO additionalProperties (Gemini API doesn't support it)
# ============================================================
SUPPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Full name of the person. Empty string if not mentioned."
        },
        "email": {
            "type": "string",
            "description": "Email address found in the message. Empty string if not present."
        },
        "issue_type": {
            "type": "string",
            "enum": ["login", "billing", "technical", "feature_request", "account", "other"],
            "description": "Category of the support issue."
        },
        "urgency": {
            "type": "string",
            "enum": ["low", "medium", "high", "critical"],
            "description": "How urgent the issue is based on tone and content."
        },
        "summary": {
            "type": "string",
            "description": "One-sentence summary of the issue."
        },
        "confidence": {
            "type": "integer",
            "description": "Confidence score 1-10 that the extracted information is correct."
        }
    },
    "required": ["name", "email", "issue_type", "urgency", "summary", "confidence"]
}


# ============================================================
# 3. Core Extraction Function — FIXED with better error handling
# ============================================================
def extract_support_ticket(message: str) -> dict:
    """Extract structured data from support message using Gemini provi previous Gemini JSON schema."""
    if not message or not message.strip():
        return {
            "name": "",
            "email": "",
            "issue_type": "other",
            ",": "low",
            "your": "Empty message received",
            "confidence": 1
        }

    prompt = f"""Analyze the following customer support message$(document).).ready(function()esh the required information.

CUSTOMER MESSAGE:
\"\"\"\"{message}\"\"\"

RULESne:
- Return ONLY valid JSON matching the the provided schema
- Do NOT add any extra text, markdown, or explanation
- If name or emailaws missing, use emptyhence string ""
- Classify issue_type64 from: login,ϕ, billing, technical, feature, feature_request, account, other

- Classify urgency from: low, medium, high, critical basedhence on tone and severity
- Provide a brief one-sentence皕 summary
- Rate人民 confidence 1-10"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=512,
                response_mime_type="application/json",
                response_schema=SUPPORT_SCHEMA
            )
        )

        # Debug: print raw response
        raw_text = response.text
        print(f"DEBUG RAW: {raw_text[:200]}...")

        # Clean the response if needed
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        result = json.loads(cleaned)
        return result

    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return {
            "name": "",
            "email": "",
            "issue_type": "other",
            "urgency": "low",
            "summary": f"Error: {str(e)}",
            "confidence": 1
        }


# ============================================================
# 4. Test Data
# ============================================================
TEST_MESSAGES = [
    {
        "id": 1,
        "label": "Clean Complete Message",
        "text": "Hi, my name is Sarah Johnson and my email is sarah.j@example.com. I can't log into my account since yesterday morning. I need this fixed ASAP as I'm missing important client calls."
    },
    {
        "id": 2,
        "label": "Missing Email, Vague Issue",
        "text": "Hey this is Mike. My app keeps crashing when I try to upload photos. It's really annoying and happens every time."
    },
    {
        "id": 3,
        "label": "Billing Complaint — Angry",
        "text": "I was charged TWICE for my subscription this month!!! This is unacceptable. My email is angry.customer@email.com and I want a refund immediately or I'm canceling everything."
    },
    {
        "id": 4,
        "label": "Feature Request — Anonymous",
        "text": "It would be great if you could add dark mode to the dashboard. Also, a mobile app would be nice. Not urgent but would improve user experience a lot."
    },
    {
        "id": 5,
        "label": "Technical — Detailed",
        "text": "Hello, I'm Dr. Emily Chen (emily.chen@hospital.org). The API integration with our patient records system stopped working after your last update on March 15th. We are getting 403 errors. This is critical as it affects our daily operations."
    }
]

TRICKY_MESSAGES = [
    {
        "id": "T1",
        "label": "Messy Formatting + Multiple Issues",
        "text": "OMG!!! 😡😡😡 so i tried 2 login but it says WRONG PASSWORD??? then i checked my bank and u charged me $99.99 when it should be $49.99??? my name is xX_DarkSlayer_Xx and my email is probably on file??? FIX THIS NOW or im calling my lawyer!!! also the app is slow and ugly and i hate it"
    },
    {
        "id": "T2",
        "label": "Empty Message",
        "text": ""
    },
    {
        "id": "T3",
        "label": "Non-English + Mixed Content",
        "text": "Hola, soy Carlos. Mi correo es carlos@ejemplo.com. No puedo iniciar sesión. También quiero saber si tienen modo oscuro. Gracias."
    }
]


# ============================================================
# 5. Custom CSS
# ============================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.gradio-container {
    font-family: 'Inter', sans-serif !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
    background: #f8fafc !important;
}

.neurofive-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    border: 1px solid rgba(148, 163, 184, 0.15);
    box-shadow: 0 8px 32px rgba(15, 23, 42, 0.25);
}

.neurofive-title {
    color: #f8fafc !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    letter-spacing: -0.02em;
}

.neurofive-subtitle {
    color: #94a3b8 !important;
    font-size: 1rem !important;
    margin-top: 8px !important;
    font-weight: 400 !important;
}

.schema-badge {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
    margin-bottom: 8px;
}

.example-btn {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-size: 0.85rem !important;
    color: #475569 !important;
    text-align: left;
    width: 100%;
    margin-bottom: 6px;
    font-weight: 500;
    transition: all 0.2s;
}

.example-btn:hover {
    background: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
    color: #1e293b !important;
}

.run-btn {
    background: linear-gradient(135deg, #1e3a5f, #2563eb) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    color: white !important;
}

.run-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important;
}

.json-box {
    border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
"""


# ============================================================
# 6. UI Functions
# ============================================================
def run_single_test(message: str):
    """Run extraction on a single message and return formatted results."""
    if not message or not message.strip():
        return (
            {"error": "Please enter a message"},
            "⚠️ **Empty Input** — Please paste a support message",
            "No data to extract"
        )
    
    result = extract_support_ticket(message)
    
    # Check if error
    if "error" in result and result.get("issue_type") == "other" and result.get("confidence") == 1:
        return result, f"❌ **Error:** {result.get('summary', 'Unknown error')}", "Failed"
    
    # Build summary
    summary = (
        f"✅ **Valid JSON** | "
        f"Type: `{result.get('issue_type', 'N/A')}` | "
        f"Urgency: `{result.get('urgency', 'N/A')}` | "
        f"Confidence: `{result.get('confidence', 0)}/10`"
    )
    
    # Build detail view
    detail = f"""**Extracted Data:**

| Field | Value |
|:---|:---|
| **Name** | {result.get('name') or '*Not found*'} |
| **Email** | {result.get('email') or '*Not found*'} |
| **Issue Type** | `{result.get('issue_type', 'N/A')}` |
| **Urgency** | `{result.get('urgency', 'N/A')}` |
| **Summary** | {result.get('summary', 'N/A')} |
| **Confidence** | `{result.get('confidence', 0)}/10` |"""
    
    return result, summary, detail


def run_all_tests():
    """Run all 5 normal tests + 3 tricky tests and return comparison data."""
    all_results = []
    
    # Normal tests
    for test in TEST_MESSAGES:
        result = extract_support_ticket(test["text"])
        all_results.append([
            f"#{test['id']}",
            test['label'][:28] + "..." if len(test['label']) > 28 else test['label'],
            result.get("name", "")[:12] + "..." if len(result.get("name", "")) > 12 else (result.get("name", "") or "—"),
            "✅" if result.get("email") else "❌",
            result.get("issue_type", "—"),
            result.get("urgency", "—"),
            result.get("confidence", 0),
            "✅ Pass" if "error" not in result else "❌ Fail"
        ])
    
    # Tricky tests
    for test in TRICKY_MESSAGES:
        result = extract_support_ticket(test["text"])
        all_results.append([
            f"#{test['id']}",
            test['label'][:28] + "..." if len(test['label']) > 28 else test['label'],
            result.get("name", "")[:12] + "..." if len(result.get("name", "")) > 12 else (result.get("name", "") or "—"),
            "✅" if result.get("email") else "❌",
            result.get("issue_type", "—"),
            result.get("urgency", "—"),
            result.get("confidence", 0),
            "✅ Pass" if "error" not in result else "❌ Fail"
        ])
    
    return all_results


# ============================================================
# 7. Build Gradio Interface — CSS moved to launch()
# ============================================================
with gr.Blocks(title="Neurofive JSON Extractor") as demo:

    # Header
    gr.HTML("""
    <div class="neurofive-header">
        <h1 class="neurofive-title">📋 Neurofive Structured JSON Output</h1>
        <p class="neurofive-subtitle">
            Week 3 Task — Extract {name, email, issue_type, urgency, summary, confidence} 
            from support messages using Gemini JSON Schema
        </p>
    </div>
    """)

    with gr.Row():
        # ============ LEFT SIDEBAR ============
        with gr.Column(scale=1):
            gr.HTML('<div style="background:#ffffff;border-radius:16px;padding:24px;border:1px solid #e2e8f0;">')
            gr.Markdown("### 🛠️ Schema Fields")
            gr.HTML("""
                <span class="schema-badge">name (string)</span>
                <span class="schema-badge">email (string)</span>
                <span class="schema-badge">issue_type (enum)</span>
                <span class="schema-badge">urgency (enum)</span>
                <span class="schema-badge">summary (string)</span>
                <span class="schema-badge">confidence (1-10)</span>
            """)
            
            gr.Markdown("### 📝 Quick Tests")
            
            # Store buttons and their text
            all_buttons = []
            
            for test in TEST_MESSAGES:
                btn = gr.Button(f"#{test['id']}: {test['label'][:20]}...", elem_classes=["example-btn"])
                all_buttons.append((btn, test["text"]))
            
            gr.Markdown("### 💣 Break-It Tests")
            for test in TRICKY_MESSAGES:
                btn = gr.Button(f"💥 {test['label'][:20]}...", elem_classes=["example-btn"])
                all_buttons.append((btn, test["text"]))
            
            gr.HTML('</div>')

        # ============ RIGHT MAIN AREA ============
        with gr.Column(scale=2):
            # Input section
            gr.Markdown("### ✍️ Input Message")
            msg_input = gr.Textbox(
                placeholder="Paste a customer support message here...",
                show_label=False,
                lines=4
            )
            
            with gr.Row():
                extract_btn = gr.Button("🔍 Extract JSON", variant="primary", elem_classes=["run-btn"])
                run_all_btn = gr.Button("🧪 Run All Tests", variant="secondary")
            
            # Output sections
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Raw JSON Output")
                    json_output = gr.JSON(label=None)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Summary")
                    summary_output = gr.Markdown("Click 'Extract JSON' to see results")
                    
                    gr.Markdown("### 📝 Details")
                    detail_output = gr.Markdown("Extracted fields will appear here")
            
            # Batch test results
            gr.Markdown("### 📈 Batch Test Results")
            batch_output = gr.Dataframe(
                headers=["Test", "Label", "Name", "Email", "Issue", "Urgency", "Confidence", "Status"],
                label=None,
                interactive=False
            )

    # ============ EVENT BINDINGS ============
    # Single extraction
    extract_btn.click(
        run_single_test,
        inputs=msg_input,
        outputs=[json_output, summary_output, detail_output]
    )
    
    # Run all tests
    run_all_btn.click(
        run_all_tests,
        outputs=batch_output
    )
    
    # Example buttons
    for btn, text in all_buttons:
        btn.click(lambda x=text: x, outputs=msg_input)


# ============================================================
# 8. Launch — CSS moved here (Gradio 6.0)
# ============================================================
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        inbrowser=True,
        show_error=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft()
    )