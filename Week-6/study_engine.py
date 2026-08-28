"""
Neurofive Study Planner Engine
Combines: Prompt Engineering + Structured Output + RAG
"""

import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.6-flash"


# ============ RAG: Load Study Tips ============
def load_knowledge_base():
    with open("study_tips.txt", "r", encoding="utf-8") as f:
        return f.read()


def get_relevant_tips(subject: str, kb: str) -> str:
    """Simple RAG: find relevant tips from knowledge base."""
    lines = kb.strip().split("\n")
    relevant = []
    current_topic = ""
    
    for line in lines:
        if line.startswith("Topic:"):
            current_topic = line.replace("Topic:", "").strip().lower()
        elif line.startswith("-") and any(word in current_topic for word in subject.lower().split()):
            relevant.append(line.replace("-", "").strip())
    
    return "\n".join(relevant) if relevant else "General study tips: Consistency, active recall, and spaced repetition work for all subjects."


# ============ Structured Output Schema ============
STUDY_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "plan_title": {"type": "string"},
        "daily_schedule": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "day": {"type": "string"},
                    "topics": {"type": "array", "items": {"type": "string"}},
                    "hours": {"type": "number"},
                    "method": {"type": "string"}
                },
                "required": ["day", "topics", "hours", "method"]
            }
        },
        "weekly_goals": {
            "type": "array",
            "items": {"type": "string"}
        },
        "resources": {
            "type": "array",
            "items": {"type": "string"}
        },
        "motivation_note": {"type": "string"}
    },
    "required": ["plan_title", "daily_schedule", "weekly_goals", "resources", "motivation_note"]
}


# ============ Main Engine ============
def generate_study_plan(subject: str, duration_days: int, hours_per_day: int, goal: str, weak_areas: str) -> dict:
    """
    Generate a structured study plan using:
    1. RAG for subject-specific tips
    2. Structured JSON output
    3. Multi-agent-like prompting (planner + motivator)
    """
    
    kb = load_knowledge_base()
    tips = get_relevant_tips(subject, kb)
    
    prompt = f"""You are an expert study coach and educational planner.
    
STUDENT PROFILE:
- Subject: {subject}
- Duration: {duration_days} days
- Available hours per day: {hours_per_day}
- Goal: {goal}
- Weak areas: {weak_areas}

RELEVANT STUDY TIPS FROM KNOWLEDGE BASE:
{tips}

Create a personalized study plan. Return ONLY valid JSON matching this exact schema:
{{
  "plan_title": "string",
  "daily_schedule": [
    {{"day": "Day 1", "topics": ["topic1", "topic2"], "hours": number, "method": "study method"}}
  ],
  "weekly_goals": ["goal1", "goal2"],
  "resources": ["resource1", "resource2"],
  "motivation_note": "encouraging message"
}}

RULES:
- Focus extra time on weak areas
- Use study methods from the knowledge base
- Make schedule realistic and sustainable
- Include breaks and revision time
- Return ONLY the JSON, no extra text"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=2048,
            response_mime_type="application/json",
            response_schema=STUDY_PLAN_SCHEMA
        )
    )
    
    return json.loads(response.text)


def generate_motivational_message(plan: dict, name: str) -> str:
    """Week 4 style: Second agent that personalizes motivation."""
    
    prompt = f"""You are a motivational coach. Write a short, personalized encouragement message for {name}.
    
Their plan: {plan['plan_title']}
Duration: {len(plan['daily_schedule'])} days
Goal: {plan['weekly_goals'][0] if plan['weekly_goals'] else 'Success'}

Keep it under 3 sentences. Be inspiring but realistic."""
    
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.7, max_output_tokens=256)
    )
    
    return response.text.strip()