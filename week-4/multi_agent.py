"""
Neurofive Solutions Week 4 — Multi-Agent Pipeline (CLI)
Agent 1: Writer → Agent 2: Editor
"""

import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.6-flash"

# Agent Prompts
WRITER_PROMPT = (
    "You are a skilled Content Writer at Neurofive Solutions. "
    "Draft clear, engaging content on any topic. "
    "Include intro, 2-3 key points, and conclusion. "
    "Output ONLY the draft, no meta-commentary."
)

EDITOR_PROMPT = (
    "You are a senior Editor at Neurofive Solutions. "
    "Review drafts for clarity, structure, tone, and completeness. "
    "Fix grammar, improve transitions, strengthen arguments. "
    "Output the FINAL polished version only."
)


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
        contents=f"TOPIC: {topic}\n\nDRAFT:\n\"\"\"{draft}\"\"\"\n\nImprove this draft. Output final version only.",
        config=types.GenerateContentConfig(
            system_instruction=EDITOR_PROMPT,
            temperature=0.3,
            max_output_tokens=2048
        )
    )
    return response.text.strip()


def main():
    print("=" * 70)
    print("  🤖🤖 Neurofive Multi-Agent Pipeline")
    print("  Week 4 — Writer + Editor Collaboration")
    print("=" * 70)
    
    topic = input("\n✍️ Enter topic: ").strip()
    if not topic:
        print("⚠️ Topic cannot be empty.")
        return
    
    print("\n" + "-" * 70)
    print("  🎭 AGENT 1: WRITER — Drafting...")
    print("-" * 70)
    
    draft = agent_writer(topic)
    print(f"\n{draft}\n")
    
    print("-" * 70)
    print("  🎭 AGENT 2: EDITOR — Reviewing & Polishing...")
    print("-" * 70)
    
    final = agent_editor(draft, topic)
    print(f"\n{final}\n")
    
    print("=" * 70)
    print("  📊 COMPARISON")
    print("=" * 70)
    print(f"   Draft Words: {len(draft.split())}")
    print(f"   Final Words: {len(final.split())}")
    print(f"   Improvement: Editor refined structure, tone, and clarity")
    print("=" * 70)


if __name__ == "__main__":
    main()