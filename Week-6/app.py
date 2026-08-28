"""
Neurofive AI Study Planner
Capstone Project — Weeks 1-5 Combined
"""

import streamlit as st
from study_engine import generate_study_plan, generate_motivational_message
import json

# ============ Page Config ============
st.set_page_config(
    page_title="Neurofive AI Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ Custom CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        text-align: center;
        color: #0f172a;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .plan-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .day-card {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .motivation-box {
        background: linear-gradient(135deg, #1e3a5f, #2563eb);
        color: white;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-top: 20px;
    }
    
    .stat-badge {
        display: inline-block;
        background: #eff6ff;
        color: #1e40af;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    .resource-tag {
        display: inline-block;
        background: #f0fdf4;
        color: #166534;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .stButton > button {
        background: #0f172a;
        color: white;
        border-radius: 10px;
        padding: 14px 32px;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #1e293b;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============ Header ============
st.markdown('<h1 class="main-title">📚 Neurofive AI Study Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Personalized study plans powered by AI — with smart tips from our knowledge base</p>', unsafe_allow_html=True)

# ============ Input Form ============
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Your Name", placeholder="e.g., Danyal")
        subject = st.selectbox(
            "Subject to Study",
            ["Python Programming", "Mathematics", "Data Structures", "Machine Learning", 
             "Web Development", "Language Learning", "Exam Preparation", "Other"]
        )
        if subject == "Other":
            subject = st.text_input("Specify Subject", placeholder="e.g., Blockchain")
    
    with col2:
        duration = st.number_input("Study Duration (days)", min_value=1, max_value=90, value=7)
        hours_per_day = st.number_input("Hours per Day", min_value=1, max_value=12, value=3)
    
    goal = st.text_input("Your Goal", placeholder="e.g., Pass final exam with A grade")
    weak_areas = st.text_area("Weak Areas (comma separated)", placeholder="e.g., recursion, dynamic programming, time complexity")

# ============ Generate Button ============
if st.button("🎯 Generate My Study Plan", type="primary"):
    if not name or not goal or not weak_areas:
        st.error("Please fill in all fields!")
    else:
        with st.spinner("🤖 AI is crafting your personalized study plan..."):
            try:
                # Generate plan
                plan = generate_study_plan(subject, duration, hours_per_day, goal, weak_areas)
                
                # Generate motivation (Week 4 multi-agent style)
                motivation = generate_motivational_message(plan, name)
                
                # ============ Display Results ============
                st.success("✅ Your study plan is ready!")
                
                # Stats
                st.markdown(f"""
                <div style="margin-bottom: 20px;">
                    <span class="stat-badge">📅 {duration} Days</span>
                    <span class="stat-badge">⏱️ {hours_per_day} hrs/day</span>
                    <span class="stat-badge">📖 {subject}</span>
                    <span class="stat-badge">🎯 {len(plan['daily_schedule'])} Sessions</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Plan Title
                st.markdown(f'<div class="plan-card"><h2 style="margin:0;color:#0f172a;">{plan["plan_title"]}</h2></div>', unsafe_allow_html=True)
                
                # Daily Schedule
                st.markdown("### 📅 Daily Schedule")
                for day in plan['daily_schedule']:
                    with st.container():
                        st.markdown(f"""
                        <div class="day-card">
                            <h4 style="margin:0 0 8px 0;color:#1e40af;">{day['day']} — {day['hours']} hours</h4>
                            <p style="margin:0 0 8px 0;color:#475569;"><strong>Topics:</strong> {', '.join(day['topics'])}</p>
                            <p style="margin:0;color:#059669;font-size:0.9rem;"><strong>Method:</strong> {day['method']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Two columns for goals and resources
                col_goals, col_resources = st.columns(2)
                
                with col_goals:
                    st.markdown("### 🎯 Weekly Goals")
                    for goal_item in plan['weekly_goals']:
                        st.markdown(f"- {goal_item}")
                
                with col_resources:
                    st.markdown("### 📚 Recommended Resources")
                    for resource in plan['resources']:
                        st.markdown(f'<span class="resource-tag">{resource}</span>', unsafe_allow_html=True)
                
                # Motivation
                st.markdown(f"""
                <div class="motivation-box">
                    <h3 style="margin:0 0 12px 0;">💪 You've Got This, {name}!</h3>
                    <p style="margin:0;font-size:1.1rem;line-height:1.6;">{motivation}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Download JSON
                plan_json = json.dumps(plan, indent=2)
                st.download_button(
                    label="📥 Download Plan as JSON",
                    data=plan_json,
                    file_name=f"study_plan_{name.lower().replace(' ', '_')}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"Error generating plan: {str(e)}")

# ============ Footer ============
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#94a3b8;font-size:0.85rem;">
    <p>Built with ❤️ by Neurofive Solutions Intern | Capstone Project</p>
    <p>Combines: Prompt Engineering + Structured JSON + RAG + Multi-Agent Motivation</p>
</div>
""", unsafe_allow_html=True)