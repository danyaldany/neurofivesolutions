# 🤖 N8N RAG Agent — AI-Powered Workflow Automation
---
This project contains an advanced **Retrieval-Augmented Generation (RAG)** agent built with **n8n**, **LangChain**, and **OpenAI GPT models**.  
It’s designed for real-world AI automation use cases such as **customer support**, **lead capture**, and **knowledge-based responses** with integrated tools like Google Sheets and Gmail.
![Image](./image.png)
---

## 🧩 Features

- **End-to-End Conversational AI Workflow**
  - Integrates with `OpenAI GPT-4 / GPT-4o` via LangChain nodes
  - Context-aware memory (buffer window)
  - Structured AI prompt for consistent persona and logic
- **RAG (Retrieval-Augmented Generation)**
  - Connects to a Supabase Vector Store for document-based knowledge retrieval
  - Queries stored data before responding to user questions
- **Automated Lead Capture**
  - Collects Name + Email during the chat
  - Saves leads directly to Google Sheets
  - Sends notification emails using Gmail API
- **Clean JSON API Integration**
  - Communicates via Webhook endpoints for front-end chat integrations
- **Friendly, Controlled Chat Flow**
  - Lead-first approach
  - Controlled message pacing and scheduling logic
  - Warm, professional tone

---

## 🏗️ Workflow Overview

```text
Webhook → Memory → AI Agent (LangChain) → Output Parser → Code Cleanup → Response
          ↘ Google Sheets + Gmail tools for lead capture
````

### Nodes Included:

* 🧠 **AI Agent** — Main logic and persona with custom system prompt
* 🗂️ **Memory Buffer** — Keeps short-term context per user
* 🪶 **Formatter + Code Nodes** — Cleans and escapes OpenAI output
* 📊 **Google Sheets Tool** — Stores Name, Email, and History
* 📧 **Gmail Tool** — Sends notification on new lead
* 🌐 **Webhook / Respond to Webhook** — REST endpoints for chat connection

---

## ⚙️ Setup Instructions

### 1️⃣ Prerequisites

* n8n installed (Docker or local)
* Google Sheets and Gmail OAuth2 credentials connected
* OpenAI API key configured inside n8n

### 2️⃣ Import Workflow

1. Open n8n
2. Click **“Import Workflow”**
3. Upload the provided JSON file (from this repo)

### 3️⃣ Environment Setup

Add environment variables or credentials in n8n:

```env
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
```

### 4️⃣ Connect Google & Gmail

Authenticate both **Google Sheets** and **Gmail** nodes with your Google account.

### 5️⃣ Test Webhook

Once active, you can test the workflow:

```bash
curl -X POST https://your-n8n-domain/webhook/e4253cc4-28b8-450a-b600-91dfc15dd5bf \
  -H "Content-Type: application/json" \
  -d '{
        "body": {
          "message": "Hi, what programs do you offer?",
          "user_id": "test123"
        }
      }'
```

---

## 🧠 Vector Store Integration

This agent supports **Supabase Vector Store** for RAG-based document retrieval.
Add your knowledge base or company docs and connect via n8n’s Supabase vector node before the AI Agent node.

**Workflow Logic:**

1. Extract user question
2. Query Supabase Vector Store
3. Pass retrieved content to the AI Agent as context
4. Generate concise, fact-based response

---

## 📋 Example Use Case — ThriveRx Virtual Assistant

This workflow powers **ThriveRx**, a virtual wellness and hormone optimization platform.
It:

* Welcomes users and collects contact info
* Answers questions from company docs via RAG
* Saves leads to Google Sheets
* Notifies the team by Gmail
* Keeps chat professional and friendly

---

## 🧰 Tech Stack

| Component                 | Description                    |
| ------------------------- | ------------------------------ |
| **n8n**                   | Visual workflow automation     |
| **LangChain**             | AI orchestration and reasoning |
| **OpenAI GPT-4 / GPT-4o** | LLM backbone                   |
| **Supabase**              | Vector storage for RAG         |
| **Google Sheets**         | Lead storage                   |
| **Gmail**                 | Email notification system      |

---

## 🧑‍💻 Author

**Ali Hassan**
📚 BS Computer Science (2022–2026)
💻 Data Science Enthusiast & AI Workflow Developer
🌐 GitHub: [alihassanml](https://github.com/alihassanml)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🌟 Contributions

Pull requests are welcome!
If you find bugs, create an issue or PR — let’s make RAG automation smarter together.

---

### 🚀 Example Command to Run via Docker

```bash
docker run -d \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Then import this workflow and start building your own RAG-powered automations!

---

### 💬 Need Help?

Open an issue or reach out for guidance on:

* Custom AI Agent Prompts
* RAG integration with Supabase
* Lead management automations

