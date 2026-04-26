import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import os
import json
import time
from dotenv import load_dotenv
from agent.extractor import extract_skills, get_skills_to_assess, get_resume_text_from_pdf
from agent.assessor import generate_questions, evaluate_answer, get_score_label, calculate_readiness_score
from agent.gap_analyzer import analyze_gaps, generate_learning_plan
from agent.youtube_search import search_youtube_videos
from agent.mcq_generator import generate_mcq, determine_skill_level, extract_focus_area, calculate_mcq_score
from utils.storage import save_candidate_result, calculate_selection_chance, calculate_willingness_score
from utils.anti_cheat import render_timer_and_anticheat
from utils.pdf_generator import generate_pdf_report
from utils.gamification import (
    award_xp, get_level, get_level_progress_pct, get_xp_to_next,
    get_xp, unlock_badge, check_and_award_badges, get_all_badges_status,
    update_streak, save_sprint_score, get_sprint_best,
    get_profile_summary, XP_VALUES
)
from groq import Groq
from prompts import FLASHCARD_PROMPT

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(
    page_title="Catalyst — Candidate Portal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {display:none;}

    @keyframes fadeInUp {
        from {opacity:0;transform:translateY(20px);}
        to {opacity:1;transform:translateY(0);}
    }
    @keyframes popIn {
        0% {transform:scale(0.5);opacity:0;}
        70% {transform:scale(1.1);}
        100% {transform:scale(1);opacity:1;}
    }
    @keyframes shimmer {
        0% {background-position:-200% center;}
        100% {background-position:200% center;}
    }
    @keyframes pulse {
        0%,100% {transform:scale(1);}
        50% {transform:scale(1.05);}
    }
    @keyframes xpFill {
        from {width:0%;}
    }

    .hero-card {
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:20px;
        padding:24px;
        border:1px solid #2d3748;
        animation:fadeInUp 0.5s ease;
    }
    .level-badge {
        display:inline-flex;
        align-items:center;
        gap:8px;
        background:linear-gradient(135deg,#667eea,#764ba2);
        border-radius:30px;
        padding:6px 16px;
        font-size:14px;
        font-weight:700;
        color:white;
        animation:popIn 0.4s ease;
    }
    .xp-bar-outer {
        background:#2d3748;
        border-radius:10px;
        height:12px;
        width:100%;
        overflow:hidden;
        margin:8px 0;
    }
    .xp-bar-inner {
        height:100%;
        border-radius:10px;
        background:linear-gradient(90deg,#667eea,#764ba2,#f093fb);
        background-size:200% auto;
        animation:shimmer 2s linear infinite, xpFill 1s ease;
        transition:width 1s ease;
    }
    .badge-card {
        background:#1a1a2e;
        border-radius:12px;
        padding:12px;
        text-align:center;
        border:2px solid #2d3748;
        transition:all 0.3s;
        animation:fadeInUp 0.3s ease;
    }
    .badge-card.unlocked {
        border-color:#667eea;
        box-shadow:0 0 15px rgba(102,126,234,0.3);
    }
    .badge-card.locked {
        opacity:0.4;
        filter:grayscale(1);
    }
    .badge-unlock-popup {
        background:linear-gradient(135deg,#667eea,#764ba2);
        border-radius:16px;
        padding:20px;
        text-align:center;
        color:white;
        animation:popIn 0.5s ease;
        margin:10px 0;
    }
    .skill-card {
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:12px;
        padding:16px;
        margin:8px 0;
        border-left:4px solid #667eea;
        animation:fadeInUp 0.4s ease;
    }
    .xp-gain-toast {
        background:linear-gradient(135deg,#68d391,#38a169);
        color:white;
        border-radius:10px;
        padding:10px 16px;
        font-weight:700;
        text-align:center;
        animation:popIn 0.4s ease;
        margin:6px 0;
    }
    .sprint-card {
        background:linear-gradient(135deg,#1a1a2e,#0f3460);
        border-radius:16px;
        padding:20px;
        border:2px solid #667eea;
        animation:fadeInUp 0.5s ease;
    }
    .progress-node {
        width:40px;height:40px;
        border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        font-weight:800;font-size:13px;
        border:3px solid;
    }
    .metric-card {
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:16px;
        padding:20px;
        text-align:center;
        border:1px solid #2d3748;
    }
    .chance-up {color:#68d391;font-weight:700;}
    .chance-down {color:#fc8181;font-weight:700;}
</style>
""", unsafe_allow_html=True)

DEMO_JD = """We are looking for a Python Developer with experience in:
- Python programming
- Django or Flask web framework
- SQL databases (PostgreSQL or MySQL)
- REST API development
- AWS EC2 and S3
- Git version control
- Problem solving and communication skills"""

DEMO_RESUME = """John Doe | johndoe@email.com
Software Developer

Skills: Python, Flask, MySQL, Git, HTML, CSS

Experience:
- Built 3 web applications using Flask and MySQL
- Worked on REST APIs for mobile applications

Education: B.Tech Computer Science, 2022"""

defaults = {
    'cp_step': 'login',
    'cp_name': '',
    'cp_email': '',
    'cp_demo_mode': False,
    'cp_extraction_done': False,
    'cp_extraction_result': None,
    'cp_skills_to_assess': [],
    'cp_jd': '',
    'cp_resume': '',
    'cp_assessment_started': False,
    'cp_current_skill_index': 0,
    'cp_current_questions': [],
    'cp_current_q_index': 0,
    'cp_current_q_text': '',
    'cp_chat_history': [],
    'cp_skill_scores': {},
    'cp_skill_reasoning': {},
    'cp_follow_up_asked': False,
    'cp_assessment_complete': False,
    'cp_mcq_questions': [],
    'cp_mcq_answers': [],
    'cp_mcq_submitted': False,
    'cp_tab_violations': 0,
    'cp_learning_plan_generated': False,
    'cp_gap_analysis': None,
    'cp_learning_plan': None,
    'cp_youtube_results': {},
    'cp_flashcards': {},
    'cp_flashcard_flip': {},
    'cp_selection_chance': 0,
    'cp_report_saved': False,
    'cp_xp_events': [],
    'cp_new_badges': [],
    'cp_leveled_up': False,
    'cp_old_level': None,
    'cp_new_level': None,
    'cp_sprint_active': False,
    'cp_sprint_questions': [],
    'cp_sprint_current': 0,
    'cp_sprint_score': 0,
    'cp_sprint_streak': 0,
    'cp_sprint_done': False,
    'cp_start_time': None,
    'cp_assessment_phase_done': False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ─────────────────────────────────────────
# HELPER: Show XP bar widget
# ─────────────────────────────────────────
def show_xp_bar(email: str):
    if not email:
        return
    summary = get_profile_summary(email)
    xp = summary['xp']
    level = summary['level']
    pct = summary['level_progress_pct']
    xp_next = summary['xp_to_next']
    streak = summary['streak']
    badges_count = summary['badges_count']

    st.markdown(f"""
    <div class="hero-card">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:32px;">{level['icon']}</span>
                <div>
                    <div class="level-badge">{level['name']}</div>
                    <div style="color:#a0aec0;font-size:12px;margin-top:4px;">{xp} XP total</div>
                </div>
            </div>
            <div style="display:flex;gap:20px;">
                <div style="text-align:center;">
                    <div style="font-size:22px;font-weight:800;color:#f6ad55;">🔥 {streak}</div>
                    <div style="color:#a0aec0;font-size:11px;">day streak</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:22px;font-weight:800;color:#b794f4;">🏅 {badges_count}</div>
                    <div style="color:#a0aec0;font-size:11px;">badges</div>
                </div>
            </div>
        </div>
        <div style="margin-top:12px;">
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#718096;margin-bottom:4px;">
                <span>Level progress</span>
                <span>{pct}% — {xp_next} XP to next level</span>
            </div>
            <div class="xp-bar-outer">
                <div class="xp-bar-inner" style="width:{pct}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPER: Show XP gain toast
# ─────────────────────────────────────────
def show_xp_toast(xp_gained: int, action_label: str):
    st.markdown(f"""
    <div class="xp-gain-toast">
        +{xp_gained} XP — {action_label}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPER: Show badge unlock
# ─────────────────────────────────────────
def show_badge_unlocks(new_badges: list):
    if not new_badges:
        return
    for badge in new_badges:
        st.markdown(f"""
        <div class="badge-unlock-popup">
            <div style="font-size:40px;">{badge['icon']}</div>
            <div style="font-size:18px;font-weight:800;margin:8px 0;">Badge Unlocked!</div>
            <div style="font-size:16px;font-weight:700;">{badge['name']}</div>
            <div style="font-size:13px;opacity:0.85;margin-top:4px;">{badge['desc']}</div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPER: Confetti animation
# ─────────────────────────────────────────
def show_confetti():
    components.html("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
    confetti({
        particleCount: 150,
        spread: 80,
        origin: {y: 0.4},
        colors: ['#667eea','#764ba2','#f093fb','#f5576c','#68d391','#f6ad55']
    });
    setTimeout(() => confetti({
        particleCount: 80,
        angle: 60,
        spread: 55,
        origin: {x: 0, y: 0.5}
    }), 400);
    setTimeout(() => confetti({
        particleCount: 80,
        angle: 120,
        spread: 55,
        origin: {x: 1, y: 0.5}
    }), 600);
    </script>
    """, height=0)


# ─────────────────────────────────────────
# HELPER: Progress Journey
# ─────────────────────────────────────────

def show_progress_journey(readiness: int):
    milestones = [
        {"pct": 0,   "label": "Start",     "color": "#63b3ed"},
        {"pct": 25,  "label": "Beginner",  "color": "#63b3ed"},
        {"pct": 50,  "label": "Learning",  "color": "#f6ad55"},
        {"pct": 75,  "label": "Skilled",   "color": "#68d391"},
        {"pct": 100, "label": "Job Ready", "color": "#b794f4"},
    ]

    node_htmls = []
    for i, m in enumerate(milestones):
        reached = readiness >= m["pct"]
        bg = m["color"] if reached else "#2d3748"
        glow = f"box-shadow:0 0 12px {m['color']}66;" if reached else ""
        check = "✓" if reached else f"{m['pct']}%"
        lc = "white" if reached else "#718096"
        lw = "700" if reached else "400"
        node_htmls.append(
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:4px;">'
            f'<div style="width:40px;height:40px;border-radius:50%;background:{bg};'
            f'border:3px solid {m["color"]};display:flex;align-items:center;'
            f'justify-content:center;color:white;font-weight:800;font-size:11px;{glow}">'
            f'{check}</div>'
            f'<div style="color:{lc};font-size:10px;font-weight:{lw};">{m["label"]}</div>'
            f'</div>'
        )
        if i < len(milestones) - 1:
            lc2 = m["color"] if readiness > m["pct"] else "#2d3748"
            node_htmls.append(
                f'<div style="flex:1;height:3px;background:{lc2};'
                f'margin-bottom:16px;border-radius:2px;min-width:20px;"></div>'
            )

    nodes_str = "".join(node_htmls)
    bar_width = min(100, readiness)

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);'
        f'border-radius:16px;padding:20px;border:1px solid #2d3748;margin:10px 0;">'
        f'<div style="color:#a0aec0;font-size:11px;margin-bottom:14px;font-weight:600;'
        f'letter-spacing:1px;">YOUR JOURNEY TO JOB READINESS</div>'
        f'<div style="display:flex;align-items:center;gap:6px;">{nodes_str}</div>'
        f'<div style="margin-top:14px;background:#2d3748;border-radius:10px;height:8px;overflow:hidden;">'
        f'<div style="width:{bar_width}%;height:100%;'
        f'background:linear-gradient(90deg,#667eea,#68d391);border-radius:10px;"></div>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;color:#718096;'
        f'font-size:11px;margin-top:5px;">'
        f'<span>0%</span>'
        f'<span style="color:white;font-weight:700;">{readiness}% readiness</span>'
        f'<span>100%</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────
# HELPER: All Badges Display
# ─────────────────────────────────────────
def show_all_badges(email: str):
    all_badges = get_all_badges_status(email)
    cols = st.columns(5)
    for i, badge in enumerate(all_badges):
        with cols[i % 5]:
            locked_class = "unlocked" if badge["unlocked"] else "locked"
            icon = badge["icon"] if badge["unlocked"] else "🔒"
            st.markdown(f"""
            <div class="badge-card {locked_class}">
                <div style="font-size:28px;">{icon}</div>
                <div style="font-size:12px;font-weight:700;color:{'white' if badge['unlocked'] else '#718096'};margin-top:6px;">{badge['name']}</div>
                <div style="font-size:10px;color:#718096;margin-top:2px;">{badge['desc']}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
col1, col2 = st.columns([1, 6])
with col1:
    if st.button("← Home"):
        st.switch_page("app.py")
with col2:
    st.markdown("### 🎯 Candidate Portal")

st.markdown("---")

# ============================================================
# STEP: LOGIN
# ============================================================
if st.session_state['cp_step'] == 'login':
    st.markdown("### Welcome to Catalyst 🎯")
    st.markdown("Complete the assessment, earn XP, unlock badges, and get your personalised learning plan.")
    st.markdown("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("Your Full Name", placeholder="John Doe")
        email = st.text_input("Your Email", placeholder="john@example.com")
        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Start Assessment", type="primary", use_container_width=True):
                if name.strip() and email.strip():
                    st.session_state['cp_name'] = name
                    st.session_state['cp_email'] = email
                    update_streak(email)
                    award_xp(email, "return_attempt")
                    st.session_state['cp_step'] = 'input'
                    st.rerun()
                else:
                    st.error("Please enter your name and email")
        with col_b:
            if st.button("Try Demo", use_container_width=True):
                st.session_state['cp_name'] = "Demo Candidate"
                st.session_state['cp_email'] = "demo@catalyst.ai"
                st.session_state['cp_demo_mode'] = True
                update_streak("demo@catalyst.ai")
                st.session_state['cp_step'] = 'input'
                st.rerun()

# ============================================================
# STEP: INPUT
# ============================================================
elif st.session_state['cp_step'] == 'input':
    show_xp_bar(st.session_state['cp_email'])
    st.markdown("")
    st.markdown(f"### Hello, **{st.session_state['cp_name']}** 👋")
    st.markdown("Paste your Job Description and Resume below to begin.")
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Job Description")
        jd = st.text_area(
            "Paste JD",
            value=DEMO_JD if st.session_state['cp_demo_mode'] else "",
            height=300,
            key="cp_jd_input"
        )
    with col2:
        st.markdown("#### Your Resume")
        resume = st.text_area(
            "Paste Resume",
            value=DEMO_RESUME if st.session_state['cp_demo_mode'] else "",
            height=250,
            key="cp_resume_input"
        )
        uploaded = st.file_uploader("Or upload PDF", type=["pdf"])
        if uploaded:
            resume = get_resume_text_from_pdf(uploaded)
            st.success("PDF loaded")

    st.markdown("")
    if st.button("Analyze My Skills →", type="primary", use_container_width=True):
        if not jd.strip() or not resume.strip():
            st.error("Please fill in both fields")
        else:
            with st.spinner("AI is analyzing your profile..."):
                result = extract_skills(jd, resume)
            if "error" in result:
                st.error(result['error'])
            else:
                skill_match = result.get("skill_match", {})
                skills_to_assess = [
                    {"skill": s, "status": v}
                    for s, v in skill_match.items()
                ]
                st.session_state['cp_extraction_result'] = result
                st.session_state['cp_skills_to_assess'] = skills_to_assess
                st.session_state['cp_jd'] = jd
                st.session_state['cp_resume'] = resume
                st.session_state['cp_extraction_done'] = True
                st.session_state['cp_start_time'] = time.time()
                st.session_state['cp_step'] = 'skill_overview'
                st.rerun()

# ============================================================
# STEP: SKILL OVERVIEW
# ============================================================
elif st.session_state['cp_step'] == 'skill_overview':
    show_xp_bar(st.session_state['cp_email'])
    st.markdown("")

    result = st.session_state['cp_extraction_result']
    skill_match = result.get("skill_match", {})

    st.markdown(f"### Skills Analysis — {result.get('job_role', 'Your Role')}")
    st.info("All skills will be tested — even ones on your resume. We verify real proficiency, not just claims.")
    st.markdown("")

    col1, col2, col3 = st.columns(3)
    yes_c = sum(1 for v in skill_match.values() if v == "YES")
    par_c = sum(1 for v in skill_match.values() if v == "PARTIAL")
    no_c  = sum(1 for v in skill_match.values() if v == "NO")

    with col1:
        st.markdown(f'<div class="metric-card"><div style="font-size:36px;color:#68d391;font-weight:800;">{yes_c}</div><div style="color:#a0aec0;">Resume Match</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div style="font-size:36px;color:#f6ad55;font-weight:800;">{par_c}</div><div style="color:#a0aec0;">Partial Match</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div style="font-size:36px;color:#fc8181;font-weight:800;">{no_c}</div><div style="color:#a0aec0;">Not on Resume</div></div>', unsafe_allow_html=True)

    st.markdown("")
    for skill, status in skill_match.items():
        if status == "YES":
            icon, note = "✅", "Resume claims this — MCQ test will verify"
        elif status == "PARTIAL":
            icon, note = "🟡", "Partial match — will assess depth"
        else:
            icon, note = "❌", "Not on resume — will assess if you know it"
        st.markdown(f'<div class="skill-card"><span style="font-weight:700;">{icon} {skill}</span><span style="color:#718096;font-size:12px;margin-left:10px;">{note}</span></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Begin Assessment →", type="primary", use_container_width=True):
            st.session_state['cp_step'] = 'mcq_assessment'
            st.session_state['cp_current_skill_index'] = 0
            st.session_state['cp_skill_scores'] = {}
            st.session_state['cp_skill_reasoning'] = {}
            st.rerun()
    with col2:
        if st.button("← Change Inputs", use_container_width=True):
            st.session_state['cp_step'] = 'input'
            st.rerun()

# ============================================================
# STEP: MCQ ASSESSMENT
# ============================================================
elif st.session_state['cp_step'] == 'mcq_assessment':
    skills = st.session_state['cp_skills_to_assess']
    idx = st.session_state['cp_current_skill_index']
    email = st.session_state['cp_email']

    if idx >= len(skills):
        st.session_state['cp_step'] = 'conversational'
        st.session_state['cp_current_skill_index'] = 0
        st.session_state['cp_chat_history'] = []
        st.rerun()

    skill_info = skills[idx]
    skill = skill_info['skill']
    total = len(skills)

    show_xp_bar(email)
    st.markdown("")
    st.markdown(f"### MCQ Test — {skill}")
    st.progress(idx / total)
    st.markdown(f"Skill **{idx+1}** of **{total}**")
    st.markdown("")

    render_timer_and_anticheat(300)
    st.markdown("")

    if not st.session_state['cp_mcq_questions']:
        with st.spinner(f"Generating questions for {skill}..."):
            focus = extract_focus_area(skill, st.session_state['cp_jd'])
            status = skill_info.get('status', 'NO')
            level = "MEDIUM" if status == "YES" else "LOW"
            questions = generate_mcq(skill, level, focus, count=5)
            st.session_state['cp_mcq_questions'] = questions
            st.session_state['cp_mcq_answers'] = [""] * len(questions)
            st.session_state['cp_mcq_submitted'] = False
        st.rerun()

    questions = st.session_state['cp_mcq_questions']

    if not st.session_state['cp_mcq_submitted']:
        answers = list(st.session_state['cp_mcq_answers'])
        for i, q in enumerate(questions):
            st.markdown(f'<div class="skill-card"><div style="color:#a0aec0;font-size:11px;">Q{i+1} of {len(questions)}</div><div style="color:white;font-size:15px;font-weight:600;margin-top:6px;">{q["question"]}</div></div>', unsafe_allow_html=True)
            selected = st.radio(
                f"q{i}",
                q.get('options', []),
                key=f"mcq_{idx}_{i}",
                label_visibility="collapsed"
            )
            answers[i] = selected if selected else ""
            st.markdown("")
        st.session_state['cp_mcq_answers'] = answers

        if st.button(f"Submit {skill} Test →", type="primary", use_container_width=True):
            result = calculate_mcq_score(answers, questions)
            score = result['score']
            correct = result['correct']
            total_q = result['total']

            st.session_state['cp_skill_scores'][skill] = score
            st.session_state['cp_skill_reasoning'][skill] = f"MCQ: {correct}/{total_q} correct"
            st.session_state['cp_mcq_submitted'] = True

            xp_result = award_xp(email, "correct_mcq", correct * XP_VALUES["correct_mcq"])
            if correct == total_q:
                award_xp(email, "perfect_mcq")
                new_badge = unlock_badge(email, "perfect_mcq")
                if new_badge:
                    st.session_state['cp_new_badges'].append(new_badge)

            if xp_result['leveled_up']:
                st.session_state['cp_leveled_up'] = True
                st.session_state['cp_new_level'] = xp_result['new_level']

            st.rerun()

    else:
        score = st.session_state['cp_skill_scores'].get(skill, 0)
        label = get_score_label(score)
        result_data = calculate_mcq_score(st.session_state['cp_mcq_answers'], questions)

        if st.session_state['cp_leveled_up']:
            show_confetti()
            level = st.session_state['cp_new_level']
            st.markdown(f"""
            <div class="badge-unlock-popup">
                <div style="font-size:44px;">{level['icon']}</div>
                <div style="font-size:20px;font-weight:800;">LEVEL UP!</div>
                <div style="font-size:16px;margin-top:6px;">You are now a {level['name']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.session_state['cp_leveled_up'] = False

        show_badge_unlocks(st.session_state['cp_new_badges'])
        st.session_state['cp_new_badges'] = []
        show_xp_toast(result_data['correct'] * XP_VALUES["correct_mcq"], f"{result_data['correct']} correct answers")

        st.markdown(f"### Results for {skill}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{score}/10")
        with col2:
            st.metric("Correct", f"{result_data['correct']}/{result_data['total']}")
        with col3:
            st.metric("Level", label)

        st.markdown("")
        for r in result_data['results']:
            icon = "✅" if r['is_correct'] else "❌"
            with st.expander(f"{icon} {r['question'][:55]}..."):
                st.markdown(f"**Your answer:** {r['user_answer']}")
                st.markdown(f"**Correct:** {r['correct_answer']}")
                st.markdown(f"**Why:** {r['explanation']}")

        st.markdown("")
        show_xp_bar(email)
        st.markdown("")

        if st.button("Next Skill →", type="primary", use_container_width=True):
            st.session_state['cp_current_skill_index'] = idx + 1
            st.session_state['cp_mcq_questions'] = []
            st.session_state['cp_mcq_answers'] = []
            st.session_state['cp_mcq_submitted'] = False
            st.rerun()

# ============================================================
# STEP: CONVERSATIONAL
# ============================================================
elif st.session_state['cp_step'] == 'conversational':
    skills = st.session_state['cp_skills_to_assess']
    idx = st.session_state['cp_current_skill_index']
    email = st.session_state['cp_email']

    if idx >= len(skills):
        award_xp(email, "full_assessment")
        st.session_state['cp_step'] = 'results'
        st.rerun()

    skill_info = skills[idx]
    skill = skill_info['skill']
    total = len(skills)

    show_xp_bar(email)
    st.markdown("")
    st.markdown(f"### Interview — {skill}")
    st.progress(idx / total)
    st.markdown(f"Skill **{idx+1}** of **{total}** — Conversational round")
    st.markdown("")

    render_timer_and_anticheat(180)
    st.markdown("")

    for chat in st.session_state['cp_chat_history']:
        role = "assistant" if chat['role'] == 'ai' else "user"
        with st.chat_message(role):
            st.write(chat['message'])

    if not st.session_state['cp_current_questions']:
        with st.spinner(f"Preparing questions for {skill}..."):
            questions = generate_questions(
                skill=skill,
                candidate_context=st.session_state['cp_resume']
            )
            st.session_state['cp_current_questions'] = questions
            st.session_state['cp_current_q_index'] = 0
            first_q = questions[0] if questions else f"Tell me about your experience with {skill}."
            st.session_state['cp_current_q_text'] = first_q
            st.session_state['cp_chat_history'].append({
                'role': 'ai',
                'message': f"Now let's talk about **{skill}**.\n\n{first_q}"
            })
        st.rerun()

    answer = st.chat_input("Your answer...")

    if answer:
        st.session_state['cp_chat_history'].append({'role': 'user', 'message': answer})

        with st.spinner("Evaluating..."):
            evaluation = evaluate_answer(
                skill=skill,
                question=st.session_state['cp_current_q_text'],
                answer=answer
            )

        score = evaluation.get('score', 5)
        reasoning = evaluation.get('reasoning', '')
        follow_up = evaluation.get('follow_up', None)
        q_index = st.session_state['cp_current_q_index']
        questions = st.session_state['cp_current_questions']

        if score >= 7:
            xp_action = "great_interview" if score >= 9 else "good_interview"
            xp_result = award_xp(email, xp_action)
            if xp_result['leveled_up']:
                st.session_state['cp_leveled_up'] = True
                st.session_state['cp_new_level'] = xp_result['new_level']
            if score >= 9:
                new_badge = unlock_badge(email, "expert_skill")
                if new_badge:
                    st.session_state['cp_new_badges'].append(new_badge)

        if score < 6 and follow_up and not st.session_state['cp_follow_up_asked']:
            st.session_state['cp_follow_up_asked'] = True
            st.session_state['cp_current_q_text'] = follow_up
            st.session_state['cp_chat_history'].append({
                'role': 'ai',
                'message': f"Interesting. Let me dig deeper — {follow_up}"
            })
            st.rerun()

        st.session_state['cp_follow_up_asked'] = False
        next_q = q_index + 1

        if next_q < len(questions):
            st.session_state['cp_current_q_index'] = next_q
            st.session_state['cp_current_q_text'] = questions[next_q]
            st.session_state['cp_chat_history'].append({
                'role': 'ai', 'message': questions[next_q]
            })
        else:
            existing = st.session_state['cp_skill_scores'].get(skill, 0)
            combined = round((existing + score) / 2)
            st.session_state['cp_skill_scores'][skill] = combined
            st.session_state['cp_skill_reasoning'][skill] = reasoning
            st.session_state['cp_current_questions'] = []
            next_idx = idx + 1
            st.session_state['cp_current_skill_index'] = next_idx

            if next_idx < len(skills):
                next_skill = skills[next_idx]['skill']
                st.session_state['cp_chat_history'].append({
                    'role': 'ai',
                    'message': f"Score recorded for **{skill}**. Moving on to **{next_skill}**..."
                })
            else:
                st.session_state['cp_step'] = 'results'

        st.rerun()

# ============================================================
# STEP: SKILL SPRINT GAME
# ============================================================
elif st.session_state['cp_step'] == 'skill_sprint':
    email = st.session_state['cp_email']
    skill_scores = st.session_state['cp_skill_scores']
    gap_skills = [s for s, sc in skill_scores.items() if sc < 7]

    show_xp_bar(email)
    st.markdown("")

    if not st.session_state['cp_sprint_active'] and not st.session_state['cp_sprint_done']:
        best = get_sprint_best(email)
        st.markdown("## ⚡ Skill Sprint")
        st.markdown("10 rapid-fire questions. 60 seconds. Streak multiplier for consecutive correct answers.")
        st.markdown("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div style="font-size:28px;color:#f6ad55;font-weight:800;">60s</div><div style="color:#a0aec0;">Time limit</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div style="font-size:28px;color:#68d391;font-weight:800;">10</div><div style="color:#a0aec0;">Questions</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div style="font-size:28px;color:#b794f4;font-weight:800;">{best}</div><div style="color:#a0aec0;">Your best score</div></div>', unsafe_allow_html=True)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Sprint!", type="primary", use_container_width=True):
                with st.spinner("Loading questions..."):
                    all_questions = []
                    skills_to_use = gap_skills if gap_skills else list(skill_scores.keys())
                    for skill in skills_to_use[:3]:
                        qs = generate_mcq(skill, "LOW", "", count=4)
                        all_questions.extend(qs)
                    import random
                    random.shuffle(all_questions)
                    st.session_state['cp_sprint_questions'] = all_questions[:10]
                    st.session_state['cp_sprint_current'] = 0
                    st.session_state['cp_sprint_score'] = 0
                    st.session_state['cp_sprint_streak'] = 0
                    st.session_state['cp_sprint_active'] = True
                st.rerun()
        with col2:
            if st.button("Skip to Results →", use_container_width=True):
                st.session_state['cp_step'] = 'results_with_plan'
                st.rerun()

    elif st.session_state['cp_sprint_active']:
        questions = st.session_state['cp_sprint_questions']
        current = st.session_state['cp_sprint_current']
        score = st.session_state['cp_sprint_score']
        streak = st.session_state['cp_sprint_streak']

        if current >= len(questions):
            st.session_state['cp_sprint_done'] = True
            st.session_state['cp_sprint_active'] = False
            st.rerun()

        render_timer_and_anticheat(60)
        st.markdown("")

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;margin-bottom:16px;">
            <div style="color:#a0aec0;">Question {current+1} / {len(questions)}</div>
            <div style="color:#f6ad55;font-weight:700;">Score: {score}</div>
            <div style="color:#68d391;font-weight:700;">🔥 Streak: {streak}x</div>
        </div>
        """, unsafe_allow_html=True)

        q = questions[current]
        st.markdown(f'<div class="sprint-card"><div style="color:white;font-size:16px;font-weight:700;">{q["question"]}</div></div>', unsafe_allow_html=True)
        st.markdown("")

        cols = st.columns(2)
        for i, option in enumerate(q.get('options', [])):
            with cols[i % 2]:
                if st.button(option, key=f"sprint_{current}_{i}", use_container_width=True):
                    correct = q.get("correct", "A")
                    is_correct = option.strip().upper().startswith(correct.upper())
                    multiplier = max(1, streak)
                    points = 10 * multiplier if is_correct else 0

                    if is_correct:
                        st.session_state['cp_sprint_score'] += points
                        st.session_state['cp_sprint_streak'] += 1
                    else:
                        st.session_state['cp_sprint_streak'] = 0

                    st.session_state['cp_sprint_current'] += 1
                    st.rerun()

    elif st.session_state['cp_sprint_done']:
        final_score = st.session_state['cp_sprint_score']
        total_q = len(st.session_state['cp_sprint_questions'])
        pct = min(100, int((final_score / (total_q * 10)) * 100))

        save_sprint_score(email, final_score)
        xp_result = award_xp(email, "skill_sprint_play")
        if pct >= 80:
            award_xp(email, "skill_sprint_win")
            new_badge = unlock_badge(email, "skill_sprint_master")
            if new_badge:
                show_confetti()
                st.session_state['cp_new_badges'].append(new_badge)

        show_badge_unlocks(st.session_state['cp_new_badges'])
        st.session_state['cp_new_badges'] = []

        if pct >= 80:
            show_confetti()
            st.markdown(f"""
            <div class="badge-unlock-popup">
                <div style="font-size:44px;">⚡</div>
                <div style="font-size:22px;font-weight:800;">SPRINT COMPLETE!</div>
                <div style="font-size:30px;font-weight:800;margin:10px 0;">{final_score} points</div>
                <div style="font-size:16px;">Amazing! {pct}% accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:24px;text-align:center;border:1px solid #2d3748;">
                <div style="font-size:44px;">⚡</div>
                <div style="font-size:22px;font-weight:800;color:white;">Sprint Done!</div>
                <div style="font-size:32px;font-weight:800;color:#f6ad55;margin:10px 0;">{final_score} pts</div>
                <div style="color:#a0aec0;">Accuracy: {pct}%</div>
            </div>
            """, unsafe_allow_html=True)

        show_xp_toast(xp_result['xp_gained'], "Skill Sprint completed")
        show_xp_bar(email)
        st.markdown("")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Play Again 🔄", use_container_width=True):
                st.session_state['cp_sprint_done'] = False
                st.session_state['cp_sprint_active'] = False
                st.session_state['cp_sprint_questions'] = []
                st.rerun()
        with col2:
            if st.button("View Results →", type="primary", use_container_width=True):
                st.session_state['cp_step'] = 'results_with_plan'
                st.rerun()

# ============================================================
# STEP: RESULTS
# ============================================================
elif st.session_state['cp_step'] in ['results', 'results_with_plan']:
    skill_scores = st.session_state['cp_skill_scores']
    skill_reasoning = st.session_state['cp_skill_reasoning']
    email = st.session_state['cp_email']
    readiness = calculate_readiness_score(skill_scores)
    job_role = st.session_state['cp_extraction_result'].get('job_role', 'Target Role')
    tab_violations = st.session_state.get('cp_tab_violations', 0)
    selection_chance = calculate_selection_chance(readiness, tab_violations, 70)
    st.session_state['cp_selection_chance'] = selection_chance

    time_taken_mins = 0
    if st.session_state.get('cp_start_time'):
        time_taken_mins = (time.time() - st.session_state['cp_start_time']) / 60

    new_badges = check_and_award_badges(
        email=email,
        readiness_score=readiness,
        tab_violations=tab_violations,
        skill_scores=skill_scores,
        is_first_attempt=True,
        improved=False,
        sprint_pct=0,
        flashcard_done=False,
        time_taken_mins=time_taken_mins
    )

    if new_badges:
        show_confetti()
        show_badge_unlocks(new_badges)

    show_xp_bar(email)
    st.markdown("")
    st.markdown("## Assessment Complete 🎯")
    st.markdown("---")

    show_progress_journey(readiness)
    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=readiness,
            title={'text': "Readiness %", 'font': {'color': 'white'}},
            gauge={
                'axis': {'range': [0, 100], 'tickfont': {'color': 'white'}},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 40], 'color': "#2d1515"},
                    {'range': [40, 70], 'color': "#2d2a15"},
                    {'range': [70, 100], 'color': "#152d1a"}
                ]
            },
            number={'font': {'color': 'white'}}
        ))
        fig.update_layout(height=200, margin=dict(t=40, b=0, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=selection_chance,
            title={'text': "Selection %", 'font': {'color': 'white'}},
            gauge={
                'axis': {'range': [0, 100], 'tickfont': {'color': 'white'}},
                'bar': {'color': "#68d391"},
                'steps': [
                    {'range': [0, 40], 'color': "#2d1515"},
                    {'range': [40, 70], 'color': "#2d2a15"},
                    {'range': [70, 100], 'color': "#152d1a"}
                ]
            },
            number={'font': {'color': 'white'}}
        ))
        fig2.update_layout(height=200, margin=dict(t=40, b=0, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="margin-top:10px;">
            <div style="font-size:32px;color:#f6ad55;font-weight:800;">{len(skill_scores)}</div>
            <div style="color:#a0aec0;margin-bottom:10px;">Skills tested</div>
            <div style="font-size:32px;color:#fc8181;font-weight:800;">{tab_violations}</div>
            <div style="color:#a0aec0;">Tab violations</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        summary = get_profile_summary(email)
        level = summary['level']
        st.markdown(f"""
        <div class="metric-card" style="margin-top:10px;">
            <div style="font-size:36px;">{level['icon']}</div>
            <div style="color:white;font-weight:700;font-size:16px;margin-top:6px;">{level['name']}</div>
            <div style="color:#a0aec0;font-size:12px;margin-top:4px;">{summary['xp']} XP earned</div>
            <div style="color:#b794f4;font-size:12px;margin-top:4px;">🏅 {summary['badges_count']} badges</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Skill Radar")
        if len(skill_scores) >= 3:
            slist = list(skill_scores.keys())
            vlist = list(skill_scores.values())
            fig3 = go.Figure()
            fig3.add_trace(go.Scatterpolar(
                r=vlist + [vlist[0]], theta=slist + [slist[0]],
                fill='toself', fillcolor='rgba(102,126,234,0.25)',
                line=dict(color='#667eea', width=2), name='Your Score'
            ))
            fig3.add_trace(go.Scatterpolar(
                r=[7] * (len(slist) + 1), theta=slist + [slist[0]],
                fill='toself', fillcolor='rgba(104,211,145,0.08)',
                line=dict(color='#68d391', width=1, dash='dash'), name='Target (7/10)'
            ))
            fig3.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color='#718096'))),
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=320,
                legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white')),
                margin=dict(t=30, b=30, l=30, r=30)
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.markdown("#### All Skill Scores")
            for skill, score in skill_scores.items():
                label = get_score_label(score)
                color = "#68d391" if score >= 7 else "#f6ad55" if score >= 5 else "#fc8181"
                st.markdown(f"""
                <div style="background:#1a1a2e;border-radius:10px;padding:14px;margin:6px 0;border-left:4px solid {color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div style="color:white;font-weight:700;">{skill}</div>
                        <div style="color:{color};font-weight:800;font-size:20px;">{score}/10</div>
                    </div>
                    <div style="background:#2d3748;border-radius:6px;height:8px;margin-top:8px;overflow:hidden;">
                        <div style="width:{score*10}%;height:100%;background:{color};border-radius:6px;"></div>
                    </div>
                    <div style="color:#718096;font-size:11px;margin-top:4px;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Skill Breakdown")
        snames = list(skill_scores.keys())
        svals = list(skill_scores.values())
        colors = ['#68d391' if s >= 7 else '#f6ad55' if s >= 5 else '#fc8181' for s in svals]
        fig4 = go.Figure(go.Bar(
            x=svals, y=snames, orientation='h',
            marker_color=colors,
            text=[f"{s}/10" for s in svals],
            textposition='outside',
            textfont=dict(color='white')
        ))
        fig4.update_layout(
            xaxis=dict(range=[0, 12], showgrid=False, color='white'),
            yaxis=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=320,
            font=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=50)
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Your Badges")
    show_all_badges(email)

    st.markdown("---")

    if st.session_state['cp_step'] == 'results':
        if st.button("⚡ Play Skill Sprint Game", type="primary", use_container_width=True):
            st.session_state['cp_step'] = 'skill_sprint'
            st.rerun()
        if st.button("Skip Game → View Learning Plan", use_container_width=True):
            st.session_state['cp_step'] = 'results_with_plan'
            st.rerun()

    if st.session_state['cp_step'] == 'results_with_plan':
        if not st.session_state['cp_learning_plan_generated']:
            if st.button("Generate Learning Plan + YouTube Resources →", type="primary", use_container_width=True):
                with st.spinner("Analyzing gaps..."):
                    gap_analysis = analyze_gaps(skill_scores, job_role)
                    st.session_state['cp_gap_analysis'] = gap_analysis

                gap_skills_raw = gap_analysis.get("gap_skills", [])
                gap_skill_names = [s.split("(")[0].strip() for s in gap_skills_raw]

                with st.spinner("Building learning plan..."):
                    plan = generate_learning_plan(gap_skill_names, job_role)
                    st.session_state['cp_learning_plan'] = plan

                youtube_results = {}
                for skill in gap_skill_names:
                    with st.spinner(f"Finding best YouTube videos for {skill}..."):
                        videos = search_youtube_videos(skill, max_results=2)
                        youtube_results[skill] = videos

                st.session_state['cp_youtube_results'] = youtube_results
                st.session_state['cp_learning_plan_generated'] = True

                xp_r = award_xp(email, "learning_plan")
                new_b = unlock_badge(email, "learning_started")
                if new_b:
                    st.session_state['cp_new_badges'].append(new_b)
                show_xp_toast(xp_r['xp_gained'], "Learning plan generated")

                if not st.session_state['cp_report_saved']:
                    save_candidate_result(
                        st.session_state['cp_name'],
                        email,
                        {
                            'job_role': job_role,
                            'readiness_score': readiness,
                            'skill_scores': skill_scores,
                            'gap_analysis': gap_analysis,
                            'selection_chance': selection_chance,
                            'tab_violations': tab_violations,
                            'willingness_score': 70
                        }
                    )
                    st.session_state['cp_report_saved'] = True

                st.rerun()

        if st.session_state['cp_learning_plan_generated']:
            gap_analysis = st.session_state['cp_gap_analysis']
            learning_plan = st.session_state['cp_learning_plan']
            youtube_results = st.session_state['cp_youtube_results']

            show_badge_unlocks(st.session_state['cp_new_badges'])
            st.session_state['cp_new_badges'] = []

            st.markdown("## Gap Analysis")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### ✅ Strong Skills")
                for s in gap_analysis.get("strong_skills", []):
                    st.markdown(f"- {s}")
            with col2:
                st.markdown("#### ❌ Skill Gaps")
                for s in gap_analysis.get("gap_skills", []):
                    st.markdown(f"- {s}")
            with col3:
                st.markdown("#### 🎯 Adjacent Skills")
                for s in gap_analysis.get("adjacent_skills", []):
                    st.markdown(f"- {s}")

            st.markdown("---")
            st.markdown("## Personalised Learning Plan")
            plan_items = learning_plan.get("learning_plan", [])
            total_time = learning_plan.get("total_time_estimate", "")
            order = learning_plan.get("recommended_order", [])
            st.info(f"Total time: **{total_time}** | Recommended order: {' → '.join(order)}")

            for item in plan_items:
                skill = item.get("skill", "")
                priority = item.get("priority", "")
                time_est = item.get("time_estimate", "")
                mini_project = item.get("mini_project", "")
                icon = "🔴" if priority == "HIGH" else "🟡" if priority == "MEDIUM" else "🟢"

                with st.expander(f"{icon} {skill} — {time_est}", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Priority:** {priority} | **Time:** {time_est}")
                        st.markdown(f"**Mini project:** {mini_project}")
                    with col2:
                        potential = min(100, selection_chance + 10)
                        arrow = "↑" if potential > selection_chance else "→"
                        st.markdown(f"""
                        <div style="background:rgba(104,211,145,0.1);border-radius:10px;padding:10px;text-align:center;">
                            <div style="color:#a0aec0;font-size:11px;">If you learn this</div>
                            <div style="color:#68d391;font-size:16px;font-weight:800;">{arrow} +10% chance</div>
                            <div style="color:#a0aec0;font-size:11px;">{selection_chance}% → {potential}%</div>
                        </div>
                        """, unsafe_allow_html=True)

                    videos = youtube_results.get(skill, [])
                    if videos:
                        st.markdown("**Best YouTube Resources:**")
                        for video in videos:
                            vc1, vc2 = st.columns([1, 4])
                            with vc1:
                                if video.get("thumbnail"):
                                    st.image(video["thumbnail"], width=120)
                                else:
                                    st.markdown("▶")
                            with vc2:
                                title = video.get('title', 'Watch Video')
                                url = video.get('url', '')
                                channel = video.get('channel', '')
                                views = video.get('view_count_display', 'N/A')
                                likes = video.get('like_count_display', 'N/A')
                                st.markdown(f"**{title}**")
                                st.markdown(f"📺 {channel} | 👁️ {views} views | 👍 {likes} likes")
                                if url:
                                    st.markdown(f"[▶ Watch on YouTube →]({url})")
                                else:
                                    st.markdown(f"[Search on YouTube →](https://www.youtube.com/results?search_query={skill}+tutorial+beginners)")
                    else:
                        st.markdown(f"**YouTube Resources:**")
                        st.markdown(f"[🔍 Search '{skill} tutorial for beginners' on YouTube →](https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial+beginners)")

                    fc_key = f"fc_{skill}"
                    st.markdown("**Flashcards:**")
                    if fc_key not in st.session_state['cp_flashcards']:
                        if st.button(f"Generate Flashcards for {skill}", key=f"gen_fc_{skill}"):
                            with st.spinner("Generating..."):
                                try:
                                    level_str = determine_skill_level(skill_scores.get(skill, 5))
                                    prompt = FLASHCARD_PROMPT.format(skill=skill, level=level_str)
                                    response = client.chat.completions.create(
                                        model="llama-3.3-70b-versatile",
                                        messages=[{"role": "user", "content": prompt}],
                                        temperature=0.7
                                    )
                                    raw = response.choices[0].message.content.strip()
                                    if raw.startswith("```"):
                                        raw = raw.split("```")[1]
                                        if raw.startswith("json"):
                                            raw = raw[4:]
                                    fc_data = json.loads(raw.strip())
                                    st.session_state['cp_flashcards'][fc_key] = fc_data.get('flashcards', [])
                                    st.session_state['cp_flashcard_flip'][fc_key] = [False] * len(fc_data.get('flashcards', []))
                                    award_xp(email, "flashcard_done")
                                    unlock_badge(email, "flashcard_master")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Could not generate flashcards: {e}")
                    else:
                        flashcards = st.session_state['cp_flashcards'][fc_key]
                        flips = st.session_state['cp_flashcard_flip'].get(fc_key, [False] * len(flashcards))
                        fc_cols = st.columns(min(3, len(flashcards)))
                        for i, card in enumerate(flashcards):
                            with fc_cols[i % len(fc_cols)]:
                                is_flipped = flips[i] if i < len(flips) else False
                                if not is_flipped:
                                    st.markdown(f"""
                                    <div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;padding:24px;text-align:center;color:white;min-height:100px;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:14px;">{card['front']}</div>
                                    """, unsafe_allow_html=True)
                                    if st.button("Flip →", key=f"flip_{skill}_{i}"):
                                        flips[i] = True
                                        st.session_state['cp_flashcard_flip'][fc_key] = flips
                                        st.rerun()
                                else:
                                    st.markdown(f"""
                                    <div style="background:#1a1a2e;border-radius:12px;padding:24px;text-align:center;color:#a0aec0;min-height:100px;display:flex;align-items:center;justify-content:center;font-size:13px;border:2px solid #667eea;">{card['back']}</div>
                                    """, unsafe_allow_html=True)
                                    if st.button("← Back", key=f"unflip_{skill}_{i}"):
                                        flips[i] = False
                                        st.session_state['cp_flashcard_flip'][fc_key] = flips
                                        st.rerun()

            st.markdown("---")
            st.markdown("## Download Your Report")
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf_report(
                    job_role=job_role,
                    readiness_score=readiness,
                    skill_scores=skill_scores,
                    skill_reasoning=skill_reasoning,
                    gap_analysis=gap_analysis,
                    learning_plan=learning_plan,
                    youtube_results=youtube_results
                )
            xp_r = award_xp(email, "pdf_downloaded")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"catalyst_{st.session_state['cp_name'].replace(' ', '_')}_report.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 Start Over", use_container_width=True):
                    for key, value in defaults.items():
                        st.session_state[key] = value
                    st.rerun()