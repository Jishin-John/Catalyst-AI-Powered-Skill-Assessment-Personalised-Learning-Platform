import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import os
import json
import time
from dotenv import load_dotenv
from agent.extractor import extract_skills, get_resume_text_from_pdf
from agent.assessor import generate_questions, evaluate_answer, get_score_label, calculate_readiness_score
from agent.gap_analyzer import analyze_gaps, generate_learning_plan
from agent.youtube_search import search_youtube_videos
from agent.mcq_generator import generate_mcq, determine_skill_level, extract_focus_area, calculate_mcq_score
from utils.storage import save_candidate_result, calculate_selection_chance, calculate_willingness_score
from utils.anti_cheat import render_timer_and_anticheat
from utils.pdf_generator import generate_pdf_report
from utils.gamification import (
    award_xp, get_level, get_level_progress_pct, get_xp_to_next,
    unlock_badge, check_and_award_badges, get_all_badges_status,
    update_streak, save_sprint_score, get_sprint_best,
    get_profile_summary, XP_VALUES, ALL_BADGES
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
    @keyframes fadeInUp {from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
    @keyframes popIn {0%{transform:scale(0.5);opacity:0;}70%{transform:scale(1.1);}100%{transform:scale(1);opacity:1;}}
    @keyframes shimmer {0%{background-position:-200% center;}100%{background-position:200% center;}}
    @keyframes float {0%,100%{transform:translateY(0);}50%{transform:translateY(-8px);}}

    .hero-card {background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:20px;padding:24px;border:1px solid #2d3748;margin-bottom:16px;}
    .level-badge {display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:30px;padding:6px 16px;font-size:14px;font-weight:700;color:white;}
    .xp-bar-outer {background:#2d3748;border-radius:10px;height:12px;width:100%;overflow:hidden;margin:8px 0;}
    .xp-bar-inner {height:100%;border-radius:10px;background:linear-gradient(90deg,#667eea,#764ba2,#f093fb);background-size:200% auto;animation:shimmer 2s linear infinite;transition:width 1s ease;}
    .badge-card {background:#1a1a2e;border-radius:12px;padding:12px 8px;text-align:center;border:2px solid #2d3748;transition:all 0.3s;min-height:100px;}
    .badge-card.unlocked {border-color:#667eea;box-shadow:0 0 15px rgba(102,126,234,0.3);}
    .badge-card.locked {opacity:0.35;filter:grayscale(1);}
    .badge-unlock-popup {background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:20px;text-align:center;color:white;animation:popIn 0.5s ease;margin:10px 0;}
    .skill-card {background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;padding:16px;margin:8px 0;border-left:4px solid #667eea;}
    .xp-toast {background:linear-gradient(135deg,#68d391,#38a169);color:white;border-radius:10px;padding:10px 16px;font-weight:700;text-align:center;animation:popIn 0.4s ease;margin:6px 0;}
    .sprint-card {background:linear-gradient(135deg,#1a1a2e,#0f3460);border-radius:16px;padding:20px;border:2px solid #667eea;}
    .metric-card {background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:16px;padding:20px;text-align:center;border:1px solid #2d3748;}
    .debug-code {background:#0d1117;border-radius:12px;padding:20px;font-family:monospace;font-size:13px;color:#e6edf3;border:1px solid #30363d;white-space:pre-wrap;line-height:1.6;margin:12px 0;}
    .scenario-card {background:linear-gradient(135deg,#1a1a2e,#0f2a1a);border-radius:16px;padding:20px;border:2px solid #68d391;margin:10px 0;}
    .tradeoff-card {background:linear-gradient(135deg,#1a1a2e,#2a1a0f);border-radius:16px;padding:20px;border:2px solid #f6ad55;margin:10px 0;}
    .whiteboard-card {background:linear-gradient(135deg,#1a1a2e,#0f1a2a);border-radius:16px;padding:20px;border:2px solid #63b3ed;margin:10px 0;}
    .micro-feedback {background:rgba(104,211,145,0.1);border-left:4px solid #68d391;border-radius:0 10px 10px 0;padding:12px 16px;color:#68d391;font-style:italic;margin:10px 0;}
    .micro-feedback.low {background:rgba(246,173,85,0.1);border-color:#f6ad55;color:#f6ad55;}
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
    'cp_extraction_result': None,
    'cp_skills_to_assess': [],
    'cp_jd': '',
    'cp_resume': '',
    'cp_extraction_done': False,
    'cp_current_skill_index': 0,
    'cp_current_questions': [],
    'cp_current_q_index': 0,
    'cp_current_q_text': '',
    'cp_chat_history': [],
    'cp_skill_scores': {},
    'cp_skill_reasoning': {},
    'cp_follow_up_asked': False,
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
    'cp_new_badges': [],
    'cp_leveled_up': False,
    'cp_new_level': None,
    'cp_sprint_active': False,
    'cp_sprint_questions': [],
    'cp_sprint_current': 0,
    'cp_sprint_score': 0,
    'cp_sprint_streak': 0,
    'cp_sprint_done': False,
    'cp_start_time': None,
    'cp_gamified_data': None,
    'cp_gamified_answered': False,
    'cp_gamified_answer': '',
    'cp_scenario_choice': None,
    'cp_github_url': '',
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def show_xp_bar(email):
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


def show_xp_toast(xp_gained, label):
    st.markdown(f'<div class="xp-toast">+{xp_gained} XP — {label}</div>', unsafe_allow_html=True)


def show_badge_unlocks(badges):
    for badge in badges:
        st.markdown(f"""
        <div class="badge-unlock-popup">
            <div style="font-size:40px;">{badge['icon']}</div>
            <div style="font-size:18px;font-weight:800;margin:8px 0;">Badge Unlocked!</div>
            <div style="font-size:16px;font-weight:700;">{badge['name']}</div>
            <div style="font-size:13px;opacity:0.85;margin-top:4px;">{badge['desc']}</div>
        </div>
        """, unsafe_allow_html=True)


def show_confetti():
    components.html("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <script>
    confetti({particleCount:150,spread:80,origin:{y:0.4},colors:['#667eea','#764ba2','#f093fb','#68d391','#f6ad55']});
    setTimeout(()=>confetti({particleCount:80,angle:60,spread:55,origin:{x:0,y:0.5}}),400);
    setTimeout(()=>confetti({particleCount:80,angle:120,spread:55,origin:{x:1,y:0.5}}),600);
    </script>
    """, height=0)


def show_progress_journey(readiness):
    milestones = [
        {"pct": 0,   "label": "Start",     "color": "#63b3ed"},
        {"pct": 25,  "label": "Beginner",  "color": "#63b3ed"},
        {"pct": 50,  "label": "Learning",  "color": "#f6ad55"},
        {"pct": 75,  "label": "Skilled",   "color": "#68d391"},
        {"pct": 100, "label": "Job Ready", "color": "#b794f4"},
    ]
    cols = st.columns(9)
    for i, m in enumerate(milestones):
        reached = readiness >= m["pct"]
        c = m["color"]
        bg = c if reached else "#2d3748"
        glow = f"box-shadow:0 0 12px {c}66;" if reached else ""
        check = "✓" if reached else f"{m['pct']}%"
        lcolor = "white" if reached else "#718096"
        lweight = "700" if reached else "400"
        with cols[m["col"] if "col" in m else i * 2]:
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="width:40px;height:40px;border-radius:50%;background:{bg};border:3px solid {c};
                display:flex;align-items:center;justify-content:center;color:white;font-weight:800;
                font-size:11px;{glow}margin:0 auto;">{check}</div>
                <div style="color:{lcolor};font-size:10px;font-weight:{lweight};margin-top:4px;">{m['label']}</div>
            </div>
            """, unsafe_allow_html=True)
        if i < len(milestones) - 1:
            lc = c if readiness > m["pct"] else "#2d3748"
            col_idx = (i * 2) + 1
            with cols[col_idx]:
                st.markdown(f'<div style="height:3px;background:{lc};margin-top:20px;border-radius:2px;"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#2d3748;border-radius:10px;height:8px;overflow:hidden;margin:12px 0 4px;">
        <div style="width:{min(100,readiness)}%;height:100%;background:linear-gradient(90deg,#667eea,#68d391);border-radius:10px;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;color:#718096;font-size:11px;">
        <span>0%</span>
        <span style="color:white;font-weight:700;">{readiness}% readiness</span>
        <span>100%</span>
    </div>
    """, unsafe_allow_html=True)


def show_all_badges(email):
    all_badges = get_all_badges_status(email)
    cols = st.columns(5)
    for i, badge in enumerate(all_badges):
        with cols[i % 5]:
            locked_class = "unlocked" if badge["unlocked"] else "locked"
            icon = badge["icon"] if badge["unlocked"] else "🔒"
            st.markdown(f"""
            <div class="badge-card {locked_class}">
                <div style="font-size:26px;">{icon}</div>
                <div style="font-size:11px;font-weight:700;color:{'white' if badge['unlocked'] else '#718096'};margin-top:6px;">{badge['name']}</div>
                <div style="font-size:9px;color:#718096;margin-top:2px;line-height:1.3;">{badge['desc']}</div>
            </div>
            """, unsafe_allow_html=True)


# ─── HEADER ───────────────────────────────────────────
col1, col2 = st.columns([1, 6])
with col1:
    st.page_link("app.py", label="← Home")
with col2:
    st.markdown("### 🎯 Candidate Portal")

st.markdown("---")

# ═══════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════
if st.session_state['cp_step'] == 'login':
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px;">
        <div style="font-size:56px;">🎯</div>
        <div style="font-size:28px;font-weight:800;color:white;margin-top:12px;">Welcome to Catalyst</div>
        <div style="color:#a0aec0;font-size:15px;margin-top:8px;">Get assessed on real skills. Earn XP. Get a personalised learning plan.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("Your Full Name", placeholder="John Doe")
        email = st.text_input("Your Email", placeholder="john@example.com")
        github = st.text_input("GitHub Profile URL (optional)", placeholder="https://github.com/username")
        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Start Assessment 🚀", type="primary", use_container_width=True):
                if name.strip() and email.strip():
                    st.session_state['cp_name'] = name
                    st.session_state['cp_email'] = email
                    st.session_state['cp_github_url'] = github
                    update_streak(email)
                    award_xp(email, "return_attempt")
                    st.session_state['cp_step'] = 'input'
                    st.rerun()
                else:
                    st.error("Please enter your name and email")
        with col_b:
            if st.button("Try Demo ▶", use_container_width=True):
                st.session_state['cp_name'] = "Demo Candidate"
                st.session_state['cp_email'] = "demo@catalyst.ai"
                st.session_state['cp_demo_mode'] = True
                update_streak("demo@catalyst.ai")
                st.session_state['cp_step'] = 'input'
                st.rerun()

# ═══════════════════════════════════════
# INPUT
# ═══════════════════════════════════════
elif st.session_state['cp_step'] == 'input':
    show_xp_bar(st.session_state['cp_email'])
    st.markdown(f"### Hello, **{st.session_state['cp_name']}** 👋")
    st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Job Description")
        jd = st.text_area("Paste JD", value=DEMO_JD if st.session_state['cp_demo_mode'] else "", height=300, key="cp_jd_in")
    with col2:
        st.markdown("#### Your Resume")
        resume = st.text_area("Paste Resume", value=DEMO_RESUME if st.session_state['cp_demo_mode'] else "", height=250, key="cp_resume_in")
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
                skills_to_assess = [{"skill": s, "status": v} for s, v in skill_match.items()]
                st.session_state['cp_extraction_result'] = result
                st.session_state['cp_skills_to_assess'] = skills_to_assess
                st.session_state['cp_jd'] = jd
                st.session_state['cp_resume'] = resume
                st.session_state['cp_start_time'] = time.time()
                st.session_state['cp_step'] = 'skill_overview'
                st.rerun()

# ═══════════════════════════════════════
# SKILL OVERVIEW
# ═══════════════════════════════════════
elif st.session_state['cp_step'] == 'skill_overview':
    show_xp_bar(st.session_state['cp_email'])
    st.markdown("")
    result = st.session_state['cp_extraction_result']
    skill_match = result.get("skill_match", {})

    st.markdown(f"### Skills Analysis — {result.get('job_role', 'Your Role')}")
    st.info("All skills are tested — even ones on your resume. We verify real proficiency, not just claims.")
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
            icon, note = "✅", "Resume claims this — MCQ + interview will verify"
        elif status == "PARTIAL":
            icon, note = "🟡", "Partial match — will assess depth"
        else:
            icon, note = "❌", "Not on resume — will assess if you know it"
        st.markdown(f'<div class="skill-card"><span style="font-weight:700;">{icon} {skill}</span><span style="color:#718096;font-size:12px;margin-left:10px;">{note}</span></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("#### What to expect")
    st.markdown("""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:10px 0;">
        <div style="background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:10px;padding:10px 14px;flex:1;min-width:130px;text-align:center;">
            <div style="font-size:20px;">📝</div>
            <div style="color:white;font-weight:700;font-size:12px;margin-top:4px;">MCQ Test</div>
            <div style="color:#718096;font-size:11px;">Timed + anti-cheat</div>
        </div>
        <div style="background:rgba(104,211,145,0.1);border:1px solid rgba(104,211,145,0.3);border-radius:10px;padding:10px 14px;flex:1;min-width:130px;text-align:center;">
            <div style="font-size:20px;">🐛</div>
            <div style="color:white;font-weight:700;font-size:12px;margin-top:4px;">Debug Challenge</div>
            <div style="color:#718096;font-size:11px;">Fix broken code</div>
        </div>
        <div style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.3);border-radius:10px;padding:10px 14px;flex:1;min-width:130px;text-align:center;">
            <div style="font-size:20px;">🤝</div>
            <div style="color:white;font-weight:700;font-size:12px;margin-top:4px;">AI Whiteboard</div>
            <div style="color:#718096;font-size:11px;">AI asks for advice</div>
        </div>
        <div style="background:rgba(246,173,85,0.1);border:1px solid rgba(246,173,85,0.3);border-radius:10px;padding:10px 14px;flex:1;min-width:130px;text-align:center;">
            <div style="font-size:20px;">⚖️</div>
            <div style="color:white;font-weight:700;font-size:12px;margin-top:4px;">Trade-offs</div>
            <div style="color:#718096;font-size:11px;">Pick 2 of 3</div>
        </div>
        <div style="background:rgba(183,148,244,0.1);border:1px solid rgba(183,148,244,0.3);border-radius:10px;padding:10px 14px;flex:1;min-width:130px;text-align:center;">
            <div style="font-size:20px;">🎮</div>
            <div style="color:white;font-weight:700;font-size:12px;margin-top:4px;">Scenario RPG</div>
            <div style="color:#718096;font-size:11px;">Make decisions</div>
        </div>
        <div style="background:rgba(252,129,129,0.1);border:1px solid rgba(252,129,129,0.3);border-radius:10px;padding:10px 14px;flex:1;min-width:130px;text-align:center;">
            <div style="font-size:20px;">💬</div>
            <div style="color:white;font-weight:700;font-size:12px;margin-top:4px;">Interview</div>
            <div style="color:#718096;font-size:11px;">Conversational Q&A</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Begin Assessment 🚀", type="primary", use_container_width=True):
            st.session_state['cp_step'] = 'mcq_assessment'
            st.session_state['cp_current_skill_index'] = 0
            st.session_state['cp_skill_scores'] = {}
            st.session_state['cp_skill_reasoning'] = {}
            st.rerun()
    with col2:
        if st.button("← Change Inputs", use_container_width=True):
            st.session_state['cp_step'] = 'input'
            st.rerun()

# ═══════════════════════════════════════
# MCQ ASSESSMENT
# ═══════════════════════════════════════
elif st.session_state['cp_step'] == 'mcq_assessment':
    skills = st.session_state['cp_skills_to_assess']
    idx = st.session_state['cp_current_skill_index']
    email = st.session_state['cp_email']

    if idx >= len(skills):
        st.session_state['cp_step'] = 'gamified_assessment'
        st.session_state['cp_current_skill_index'] = 0
        st.rerun()

    skill_info = skills[idx]
    skill = skill_info['skill']
    total = len(skills)

    show_xp_bar(email)
    st.markdown("")
    st.markdown(f"### 📝 MCQ Test — **{skill}**")
    st.progress(idx / total)
    st.markdown(f"Skill **{idx+1}** of **{total}**")
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
    timer_secs = len(questions) * 30
    render_timer_and_anticheat(timer_secs)
    st.markdown("")

    if not st.session_state['cp_mcq_submitted']:
        answers = list(st.session_state['cp_mcq_answers'])
        for i, q in enumerate(questions):
            st.markdown(f'<div class="skill-card"><div style="color:#a0aec0;font-size:11px;margin-bottom:6px;">Q{i+1} of {len(questions)}</div><div style="color:white;font-size:15px;font-weight:600;">{q["question"]}</div></div>', unsafe_allow_html=True)
            selected = st.radio(f"q{i}", q.get('options', []), key=f"mcq_{idx}_{i}", label_visibility="collapsed")
            answers[i] = selected if selected else ""
            st.markdown("")
        st.session_state['cp_mcq_answers'] = answers

        if st.button(f"Submit {skill} Test →", type="primary", use_container_width=True):
            result = calculate_mcq_score(answers, questions)
            score = result['score']
            st.session_state['cp_skill_scores'][skill] = score
            st.session_state['cp_skill_reasoning'][skill] = f"MCQ: {result['correct']}/{result['total']} correct"
            st.session_state['cp_mcq_submitted'] = True
            xp_r = award_xp(email, "correct_mcq", result['correct'] * XP_VALUES["correct_mcq"])
            if result['correct'] == result['total']:
                award_xp(email, "perfect_mcq")
                nb = unlock_badge(email, "perfect_mcq")
                if nb:
                    st.session_state['cp_new_badges'].append(nb)
            if xp_r['leveled_up']:
                st.session_state['cp_leveled_up'] = True
                st.session_state['cp_new_level'] = xp_r['new_level']
            st.rerun()

    else:
        score = st.session_state['cp_skill_scores'].get(skill, 0)
        result_data = calculate_mcq_score(st.session_state['cp_mcq_answers'], questions)

        if st.session_state['cp_leveled_up']:
            show_confetti()
            level = st.session_state['cp_new_level']
            st.markdown(f'<div class="badge-unlock-popup"><div style="font-size:44px;">{level["icon"]}</div><div style="font-size:20px;font-weight:800;">LEVEL UP! You are now {level["name"]}</div></div>', unsafe_allow_html=True)
            st.session_state['cp_leveled_up'] = False

        show_badge_unlocks(st.session_state['cp_new_badges'])
        st.session_state['cp_new_badges'] = []
        show_xp_toast(result_data['correct'] * XP_VALUES["correct_mcq"], f"{result_data['correct']} correct answers")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{score}/10")
        with col2:
            st.metric("Correct", f"{result_data['correct']}/{result_data['total']}")
        with col3:
            st.metric("Level", get_score_label(score))

        for r in result_data['results']:
            icon = "✅" if r['is_correct'] else "❌"
            with st.expander(f"{icon} {r['question'][:60]}..."):
                st.markdown(f"**Your answer:** {r['user_answer']}")
                st.markdown(f"**Correct:** {r['correct_answer']}")
                st.markdown(f"**Why:** {r['explanation']}")

        show_xp_bar(email)
        st.markdown("")

        if st.button("Next Skill →", type="primary", use_container_width=True):
            st.session_state['cp_current_skill_index'] = idx + 1
            st.session_state['cp_mcq_questions'] = []
            st.session_state['cp_mcq_answers'] = []
            st.session_state['cp_mcq_submitted'] = False
            st.rerun()

# ═══════════════════════════════════════
# GAMIFIED ASSESSMENT
# ═══════════════════════════════════════
elif st.session_state['cp_step'] == 'gamified_assessment':
    try:
        from agent.gamified_assessment import (
            generate_debugging_challenge, generate_whiteboard_scenario,
            generate_tradeoff_scenario, generate_scenario_branch,
            evaluate_open_answer
        )
        gamified_available = True
    except ImportError:
        gamified_available = False

    skills = st.session_state['cp_skills_to_assess']
    idx = st.session_state['cp_current_skill_index']
    email = st.session_state['cp_email']

    if idx >= len(skills) or not gamified_available:
        st.session_state['cp_step'] = 'conversational'
        st.session_state['cp_current_skill_index'] = 0
        st.session_state['cp_chat_history'] = []
        st.rerun()

    skill_info = skills[idx]
    skill = skill_info['skill']
    total = len(skills)
    existing_score = st.session_state['cp_skill_scores'].get(skill, 5)

    show_xp_bar(email)
    st.markdown("")
    st.progress(idx / total)
    st.markdown(f"Skill **{idx+1}** of **{total}** — Gamified round")
    st.markdown("")

    render_timer_and_anticheat(120)
    st.markdown("")

    if existing_score >= 7:
        mode = "whiteboard"
    elif existing_score >= 5:
        mode = "tradeoff"
    elif existing_score >= 3:
        mode = "scenario"
    else:
        mode = "debug"

    if not st.session_state['cp_gamified_data']:
        with st.spinner(f"Preparing challenge for {skill}..."):
            try:
                if mode == "debug":
                    data = generate_debugging_challenge(skill, "LOW")
                elif mode == "whiteboard":
                    data = generate_whiteboard_scenario(skill, st.session_state['cp_extraction_result'].get('job_role', 'Developer'))
                elif mode == "tradeoff":
                    data = generate_tradeoff_scenario(skill)
                else:
                    data = generate_scenario_branch(skill, "MEDIUM")
                data['mode'] = mode
                st.session_state['cp_gamified_data'] = data
            except Exception as e:
                st.session_state['cp_step'] = 'conversational'
                st.session_state['cp_current_skill_index'] = 0
                st.session_state['cp_chat_history'] = []
                st.rerun()
        st.rerun()

    data = st.session_state['cp_gamified_data']
    current_mode = data.get('mode', mode)

    if not st.session_state['cp_gamified_answered']:

        if current_mode == "debug":
            st.markdown(f'<div class="skill-card"><div style="font-size:18px;">🐛 Debug Challenge — <span style="color:#667eea;">{skill}</span></div><div style="color:#a0aec0;font-size:13px;margin-top:6px;">Find and fix the bugs. Show your engineering instinct.</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="debug-code">{data.get("broken_code", "")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#f6ad55;font-size:13px;background:rgba(246,173,85,0.1);padding:10px;border-radius:8px;border-left:3px solid #f6ad55;margin-bottom:10px;">💡 Hint: {data.get("hint", "")}</div>', unsafe_allow_html=True)
            answer = st.text_area("Explain the bugs and how you would fix them:", height=140, key=f"debug_ans_{idx}")
            if st.button("Submit Fix →", type="primary", use_container_width=True):
                if answer.strip():
                    with st.spinner("Evaluating..."):
                        eval_result = evaluate_open_answer(skill, data.get("question", ""), answer)
                    score = eval_result.get('score', 5)
                    existing = st.session_state['cp_skill_scores'].get(skill, 0)
                    st.session_state['cp_skill_scores'][skill] = round((existing + score) / 2)
                    st.session_state['cp_skill_reasoning'][skill] = eval_result.get('reasoning', '')
                    st.session_state['cp_gamified_answered'] = True
                    st.session_state['cp_gamified_answer'] = eval_result
                    award_xp(email, "good_interview" if score >= 7 else "correct_mcq", 15)
                    st.rerun()

        elif current_mode == "whiteboard":
            st.markdown(f"""
            <div class="whiteboard-card">
                <div style="font-size:18px;color:#63b3ed;">🤝 AI Collaboration — <span style="color:#667eea;">{skill}</span></div>
                <div style="color:#a0aec0;font-size:13px;margin-top:6px;">The AI needs your expert help. This is a peer conversation, not a test.</div>
                <div style="margin-top:14px;padding:14px;background:rgba(99,179,237,0.08);border-radius:10px;">
                    <div style="color:#63b3ed;font-size:13px;font-weight:700;margin-bottom:6px;">📋 Scenario:</div>
                    <div style="color:#e2e8f0;font-size:14px;">{data.get('scenario', '')}</div>
                </div>
                <div style="margin-top:12px;padding:14px;background:rgba(252,129,129,0.08);border-radius:10px;">
                    <div style="color:#fc8181;font-size:13px;font-weight:700;margin-bottom:6px;">🤖 AI decided:</div>
                    <div style="color:#e2e8f0;font-size:14px;">{data.get('ai_decision', '')}</div>
                </div>
                <div style="margin-top:12px;padding:14px;background:rgba(246,173,85,0.08);border-radius:10px;">
                    <div style="color:#f6ad55;font-size:13px;font-weight:700;margin-bottom:6px;">😟 AI is worried:</div>
                    <div style="color:#e2e8f0;font-size:14px;">{data.get('ai_concern', '')}</div>
                </div>
                <div style="margin-top:14px;color:white;font-size:15px;font-weight:700;">{data.get('question', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            answer = st.text_area("Your recommendation:", height=140, key=f"wb_ans_{idx}")
            if st.button("Share Recommendation →", type="primary", use_container_width=True):
                if answer.strip():
                    with st.spinner("Evaluating..."):
                        eval_result = evaluate_open_answer(skill, data.get("question", ""), answer)
                    score = eval_result.get('score', 5)
                    existing = st.session_state['cp_skill_scores'].get(skill, 0)
                    st.session_state['cp_skill_scores'][skill] = round((existing + score) / 2)
                    st.session_state['cp_skill_reasoning'][skill] = eval_result.get('reasoning', '')
                    st.session_state['cp_gamified_answered'] = True
                    st.session_state['cp_gamified_answer'] = eval_result
                    award_xp(email, "good_interview", 20)
                    st.rerun()

        elif current_mode == "tradeoff":
            st.markdown(f"""
            <div class="tradeoff-card">
                <div style="font-size:18px;color:#f6ad55;">⚖️ Trade-off Challenge — <span style="color:#667eea;">{skill}</span></div>
                <div style="color:#a0aec0;font-size:13px;margin-top:6px;">Engineering is about trade-offs. Show us your philosophy.</div>
                <div style="margin-top:14px;color:#e2e8f0;font-size:14px;">{data.get('scenario', '')}</div>
                <div style="margin-top:14px;color:white;font-size:15px;font-weight:700;">{data.get('question', '')}</div>
                <div style="margin-top:8px;color:#f6ad55;font-size:13px;">You can only choose 2 of these 3:</div>
            </div>
            """, unsafe_allow_html=True)

            attrs = [data.get('attribute_a', 'Performance'), data.get('attribute_b', 'Simplicity'), data.get('attribute_c', 'Cost')]
            chosen = []
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.checkbox(f"✓ {attrs[0]}", key=f"attr_a_{idx}"):
                    chosen.append(attrs[0])
            with col2:
                if st.checkbox(f"✓ {attrs[1]}", key=f"attr_b_{idx}"):
                    chosen.append(attrs[1])
            with col3:
                if st.checkbox(f"✓ {attrs[2]}", key=f"attr_c_{idx}"):
                    chosen.append(attrs[2])

            if len(chosen) > 2:
                st.warning("Pick only 2.")
            elif len(chosen) == 2:
                reasoning = st.text_area(f"Why did you choose {chosen[0]} and {chosen[1]}?", height=100, key=f"tradeoff_r_{idx}")
                if st.button("Submit →", type="primary", use_container_width=True):
                    if reasoning.strip():
                        with st.spinner("Evaluating..."):
                            eval_result = evaluate_open_answer(skill, data.get("question", ""), f"Chose: {', '.join(chosen)}. {reasoning}")
                        score = eval_result.get('score', 5)
                        existing = st.session_state['cp_skill_scores'].get(skill, 0)
                        st.session_state['cp_skill_scores'][skill] = round((existing + score) / 2)
                        st.session_state['cp_skill_reasoning'][skill] = eval_result.get('reasoning', '')
                        st.session_state['cp_gamified_answered'] = True
                        st.session_state['cp_gamified_answer'] = eval_result
                        award_xp(email, "good_interview", 18)
                        st.rerun()

        elif current_mode == "scenario":
            st.markdown(f"""
            <div class="scenario-card">
                <div style="font-size:18px;color:#68d391;">🎮 Scenario — <span style="color:#667eea;">{skill}</span></div>
                <div style="color:#a0aec0;font-size:13px;margin-top:6px;">You own this system. Make the call.</div>
                <div style="margin-top:14px;padding:14px;background:rgba(104,211,145,0.08);border-radius:10px;">
                    <div style="color:#68d391;font-weight:700;margin-bottom:6px;">Your System:</div>
                    <div style="color:#e2e8f0;">{data.get('setup', '')}</div>
                </div>
                <div style="margin-top:12px;padding:14px;background:rgba(252,129,129,0.1);border-radius:10px;border-left:3px solid #fc8181;">
                    <div style="color:#fc8181;font-weight:700;margin-bottom:6px;">🚨 Crisis:</div>
                    <div style="color:#e2e8f0;">{data.get('crisis', '')}</div>
                </div>
                <div style="margin-top:14px;color:white;font-size:15px;font-weight:700;">What do you do?</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"A: {data.get('choice_a', '')[:40]}", use_container_width=True, key=f"sc_a_{idx}"):
                    st.session_state['cp_scenario_choice'] = 'A'
                    st.rerun()
            with col2:
                if st.button(f"B: {data.get('choice_b', '')[:40]}", use_container_width=True, key=f"sc_b_{idx}"):
                    st.session_state['cp_scenario_choice'] = 'B'
                    st.rerun()
            with col3:
                if st.button(f"C: {data.get('choice_c', '')[:40]}", use_container_width=True, key=f"sc_c_{idx}"):
                    st.session_state['cp_scenario_choice'] = 'C'
                    st.rerun()

            if st.session_state['cp_scenario_choice']:
                chosen = st.session_state['cp_scenario_choice']
                best = data.get('best_choice', 'A')
                consequence = data.get(f"consequence_{chosen.lower()}", "")
                if chosen == best:
                    st.markdown(f'<div class="micro-feedback">✓ {consequence} Good instinct!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="micro-feedback low">→ {consequence}</div>', unsafe_allow_html=True)

                follow_up = st.text_area(data.get('follow_up', 'Explain your reasoning:'), height=100, key=f"sc_r_{idx}")
                if st.button("Submit →", type="primary", use_container_width=True):
                    is_best = chosen == best
                    score = st.session_state['cp_skill_scores'].get(skill, 5)
                    st.session_state['cp_skill_scores'][skill] = min(10, score + (2 if is_best else 0))
                    st.session_state['cp_gamified_answered'] = True
                    st.session_state['cp_gamified_answer'] = {'score': st.session_state['cp_skill_scores'][skill], 'micro_feedback': consequence, 'reasoning': follow_up}
                    award_xp(email, "good_interview", 16)
                    st.rerun()

    else:
        eval_result = st.session_state['cp_gamified_answer']
        feedback = eval_result.get('micro_feedback', '')
        score = eval_result.get('score', 5)
        fc = "" if score >= 6 else "low"
        st.markdown(f'<div class="micro-feedback {fc}">{feedback}</div>', unsafe_allow_html=True)
        show_xp_bar(email)
        st.markdown("")

        if st.button("Next Skill →", type="primary", use_container_width=True):
            st.session_state['cp_current_skill_index'] = idx + 1
            st.session_state['cp_gamified_data'] = None
            st.session_state['cp_gamified_answered'] = False
            st.session_state['cp_gamified_answer'] = ''
            st.session_state['cp_scenario_choice'] = None
            st.rerun()

# ═══════════════════════════════════════
# CONVERSATIONAL
# ═══════════════════════════════════════
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
    st.markdown(f"### 💬 Interview — **{skill}**")
    st.progress(idx / total)
    st.markdown(f"Skill **{idx+1}** of **{total}**")
    st.markdown("")

    render_timer_and_anticheat(120)
    st.markdown("")

    for chat in st.session_state['cp_chat_history']:
        role = "assistant" if chat['role'] == 'ai' else "user"
        with st.chat_message(role):
            st.write(chat['message'])

    if not st.session_state['cp_current_questions']:
        with st.spinner(f"Preparing questions for {skill}..."):
            questions = generate_questions(skill=skill, candidate_context=st.session_state['cp_resume'])
            st.session_state['cp_current_questions'] = questions
            st.session_state['cp_current_q_index'] = 0
            first_q = questions[0] if questions else f"Tell me about your experience with {skill}."
            st.session_state['cp_current_q_text'] = first_q
            st.session_state['cp_chat_history'].append({'role': 'ai', 'message': f"Let's talk about **{skill}**.\n\n{first_q}"})
        st.rerun()

    answer = st.chat_input("Your answer...")

    if answer:
        st.session_state['cp_chat_history'].append({'role': 'user', 'message': answer})
        with st.spinner("Evaluating..."):
            evaluation = evaluate_answer(skill=skill, question=st.session_state['cp_current_q_text'], answer=answer)

        score = evaluation.get('score', 5)
        reasoning = evaluation.get('reasoning', '')
        follow_up = evaluation.get('follow_up', None)
        q_index = st.session_state['cp_current_q_index']
        questions = st.session_state['cp_current_questions']

        if score >= 7:
            xp_r = award_xp(email, "great_interview" if score >= 9 else "good_interview")
            if xp_r['leveled_up']:
                st.session_state['cp_leveled_up'] = True
                st.session_state['cp_new_level'] = xp_r['new_level']
            if score >= 9:
                nb = unlock_badge(email, "expert_skill")
                if nb:
                    st.session_state['cp_new_badges'].append(nb)

        if score < 6 and follow_up and not st.session_state['cp_follow_up_asked']:
            st.session_state['cp_follow_up_asked'] = True
            st.session_state['cp_current_q_text'] = follow_up
            st.session_state['cp_chat_history'].append({'role': 'ai', 'message': f"Interesting. Let me dig deeper — {follow_up}"})
            st.rerun()

        st.session_state['cp_follow_up_asked'] = False
        next_q = q_index + 1

        if next_q < len(questions):
            st.session_state['cp_current_q_index'] = next_q
            st.session_state['cp_current_q_text'] = questions[next_q]
            st.session_state['cp_chat_history'].append({'role': 'ai', 'message': questions[next_q]})
        else:
            existing = st.session_state['cp_skill_scores'].get(skill, 0)
            st.session_state['cp_skill_scores'][skill] = round((existing + score) / 2)
            st.session_state['cp_skill_reasoning'][skill] = reasoning
            st.session_state['cp_current_questions'] = []
            next_idx = idx + 1
            st.session_state['cp_current_skill_index'] = next_idx
            if next_idx < len(skills):
                st.session_state['cp_chat_history'].append({'role': 'ai', 'message': f"Score recorded for **{skill}**. Moving to **{skills[next_idx]['skill']}**..."})
            else:
                st.session_state['cp_step'] = 'results'
        st.rerun()

# ═══════════════════════════════════════
# SKILL SPRINT
# ═══════════════════════════════════════
elif st.session_state['cp_step'] == 'skill_sprint':
    email = st.session_state['cp_email']
    skill_scores = st.session_state['cp_skill_scores']
    gap_skills = [s for s, sc in skill_scores.items() if sc < 7]

    show_xp_bar(email)
    st.markdown("")

    if not st.session_state['cp_sprint_active'] and not st.session_state['cp_sprint_done']:
        best = get_sprint_best(email)
        st.markdown("## ⚡ Skill Sprint")
        st.markdown("10 rapid-fire questions. 60 seconds. Streak multiplier for correct answers.")
        st.markdown("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div style="font-size:28px;color:#f6ad55;font-weight:800;">60s</div><div style="color:#a0aec0;">Time limit</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div style="font-size:28px;color:#68d391;font-weight:800;">10</div><div style="color:#a0aec0;">Questions</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div style="font-size:28px;color:#b794f4;font-weight:800;">{best}</div><div style="color:#a0aec0;">Your best</div></div>', unsafe_allow_html=True)
        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Sprint!", type="primary", use_container_width=True):
                with st.spinner("Loading..."):
                    import random
                    all_qs = []
                    for s in (gap_skills if gap_skills else list(skill_scores.keys()))[:3]:
                        all_qs.extend(generate_mcq(s, "LOW", "", count=4))
                    random.shuffle(all_qs)
                    st.session_state['cp_sprint_questions'] = all_qs[:10]
                    st.session_state['cp_sprint_current'] = 0
                    st.session_state['cp_sprint_score'] = 0
                    st.session_state['cp_sprint_streak'] = 0
                    st.session_state['cp_sprint_active'] = True
                st.rerun()
        with col2:
            if st.button("Skip → View Results", use_container_width=True):
                st.session_state['cp_step'] = 'results_plan'
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
        <div style="display:flex;justify-content:space-between;background:#1a1a2e;padding:12px 16px;border-radius:10px;margin-bottom:12px;">
            <div style="color:#a0aec0;">Q{current+1}/{len(questions)}</div>
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
                    is_correct = option.strip().upper().startswith(q.get("correct", "A").upper())
                    multiplier = max(1, streak)
                    if is_correct:
                        st.session_state['cp_sprint_score'] += 10 * multiplier
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
        xp_r = award_xp(email, "skill_sprint_play")
        if pct >= 80:
            award_xp(email, "skill_sprint_win")
            nb = unlock_badge(email, "skill_sprint_master")
            if nb:
                show_confetti()
                show_badge_unlocks([nb])

        if pct >= 80:
            show_confetti()
            st.markdown(f'<div class="badge-unlock-popup"><div style="font-size:44px;">⚡</div><div style="font-size:22px;font-weight:800;">SPRINT COMPLETE!</div><div style="font-size:32px;font-weight:800;margin:10px 0;">{final_score} pts</div><div>{pct}% accuracy</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background:#1a1a2e;border-radius:16px;padding:24px;text-align:center;border:1px solid #2d3748;"><div style="font-size:44px;">⚡</div><div style="font-size:22px;font-weight:800;color:white;">Sprint Done!</div><div style="font-size:32px;font-weight:800;color:#f6ad55;margin:10px 0;">{final_score} pts</div><div style="color:#a0aec0;">{pct}% accuracy</div></div>', unsafe_allow_html=True)

        show_xp_toast(xp_r['xp_gained'], "Sprint completed")
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
                st.session_state['cp_step'] = 'results_plan'
                st.rerun()

# ═══════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════
elif st.session_state['cp_step'] in ['results', 'results_plan']:
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
        email=email, readiness_score=readiness,
        tab_violations=tab_violations, skill_scores=skill_scores,
        is_first_attempt=True, improved=False, sprint_pct=0,
        flashcard_done=False, time_taken_mins=time_taken_mins
    )
    if new_badges:
        show_confetti()
        show_badge_unlocks(new_badges)

    show_xp_bar(email)
    st.markdown("")
    st.markdown("## 🎯 Assessment Complete")
    st.markdown("---")

    # Progress Journey
    milestones_data = [
        {"pct": 0,   "label": "Start",     "color": "#63b3ed"},
        {"pct": 25,  "label": "Beginner",  "color": "#63b3ed"},
        {"pct": 50,  "label": "Learning",  "color": "#f6ad55"},
        {"pct": 75,  "label": "Skilled",   "color": "#68d391"},
        {"pct": 100, "label": "Job Ready", "color": "#b794f4"},
    ]
    journey_cols = st.columns(9)
    col_positions = [0, 2, 4, 6, 8]
    for i, m in enumerate(milestones_data):
        reached = readiness >= m["pct"]
        c = m["color"]
        bg = c if reached else "#2d3748"
        glow = f"box-shadow:0 0 12px {c}66;" if reached else ""
        check = "✓" if reached else f"{m['pct']}%"
        lc = "white" if reached else "#718096"
        lw = "700" if reached else "400"
        with journey_cols[col_positions[i]]:
            st.markdown(f"""
            <div style="text-align:center;">
                <div style="width:40px;height:40px;border-radius:50%;background:{bg};
                border:3px solid {c};display:flex;align-items:center;justify-content:center;
                color:white;font-weight:800;font-size:11px;{glow}margin:0 auto;">{check}</div>
                <div style="color:{lc};font-size:10px;font-weight:{lw};margin-top:4px;">{m['label']}</div>
            </div>
            """, unsafe_allow_html=True)
        if i < len(milestones_data) - 1:
            lc2 = c if readiness > m["pct"] else "#2d3748"
            with journey_cols[col_positions[i] + 1]:
                st.markdown(f'<div style="height:3px;background:{lc2};margin-top:20px;border-radius:2px;"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#2d3748;border-radius:10px;height:8px;overflow:hidden;margin:12px 0 4px;">
        <div style="width:{min(100,readiness)}%;height:100%;background:linear-gradient(90deg,#667eea,#68d391);border-radius:10px;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;color:#718096;font-size:11px;margin-bottom:16px;">
        <span>0%</span>
        <span style="color:white;font-weight:700;">{readiness}% readiness</span>
        <span>100%</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=readiness,
            title={'text': "Readiness %", 'font': {'color': 'white', 'size': 13}},
            gauge={'axis': {'range': [0, 100], 'tickfont': {'color': 'white'}},
                   'bar': {'color': "#667eea"},
                   'steps': [{'range': [0, 40], 'color': "#2d1515"},
                              {'range': [40, 70], 'color': "#2d2a15"},
                              {'range': [70, 100], 'color': "#152d1a"}]},
            number={'font': {'color': 'white'}}
        ))
        fig.update_layout(height=200, margin=dict(t=40,b=0,l=10,r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number", value=selection_chance,
            title={'text': "Selection %", 'font': {'color': 'white', 'size': 13}},
            gauge={'axis': {'range': [0, 100], 'tickfont': {'color': 'white'}},
                   'bar': {'color': "#68d391"},
                   'steps': [{'range': [0, 40], 'color': "#2d1515"},
                              {'range': [40, 70], 'color': "#2d2a15"},
                              {'range': [70, 100], 'color': "#152d1a"}]},
            number={'font': {'color': 'white'}}
        ))
        fig2.update_layout(height=200, margin=dict(t=40,b=0,l=10,r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="margin-top:10px;">
            <div style="font-size:32px;color:#f6ad55;font-weight:800;">{len(skill_scores)}</div>
            <div style="color:#a0aec0;margin-bottom:10px;">Skills tested</div>
            <div style="font-size:32px;color:{'#fc8181' if tab_violations>0 else '#68d391'};font-weight:800;">{tab_violations}</div>
            <div style="color:#a0aec0;">Violations</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        summary = get_profile_summary(email)
        level = summary['level']
        st.markdown(f"""
        <div class="metric-card" style="margin-top:10px;">
            <div style="font-size:36px;">{level['icon']}</div>
            <div style="color:white;font-weight:700;font-size:16px;margin-top:6px;">{level['name']}</div>
            <div style="color:#a0aec0;font-size:12px;">{summary['xp']} XP</div>
            <div style="color:#b794f4;font-size:12px;">🏅 {summary['badges_count']} badges</div>
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
                fill='toself', fillcolor='rgba(240,147,251,0.25)',
                line=dict(color='#f093fb', width=2), name='Your Score'
            ))
            fig3.add_trace(go.Scatterpolar(
                r=[7] * (len(slist) + 1), theta=slist + [slist[0]],
                fill='toself', fillcolor='rgba(99,179,237,0.15)',
                line=dict(color='#63b3ed', width=1.5, dash='dash'), name='Target (7/10)'
            ))
            fig3.update_layout(
                polar=dict(
                    bgcolor='white',
                    radialaxis=dict(visible=True, range=[0, 10],
                                   tickfont=dict(color='#333'),
                                   gridcolor='#ddd', linecolor='#ddd'),
                    angularaxis=dict(tickfont=dict(color='#333', size=11),
                                    linecolor='#ddd', gridcolor='#ddd')
                ),
                showlegend=True, paper_bgcolor='white', plot_bgcolor='white',
                height=340,
                legend=dict(bgcolor='white', font=dict(color='#333')),
                margin=dict(t=30, b=30, l=30, r=30)
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.markdown("#### Skill Scores")
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
            textposition='outside', textfont=dict(color='white')
        ))
        fig4.update_layout(
            xaxis=dict(range=[0, 12], showgrid=False, color='white'),
            yaxis=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=320, font=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=50)
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Your Badges")
    show_all_badges(email)
    st.markdown("---")

    if st.session_state['cp_step'] == 'results':
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⚡ Play Skill Sprint", type="primary", use_container_width=True):
                st.session_state['cp_step'] = 'skill_sprint'
                st.rerun()
        with col2:
            if st.button("View Learning Plan →", use_container_width=True):
                st.session_state['cp_step'] = 'results_plan'
                st.rerun()

    if st.session_state['cp_step'] == 'results_plan':
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
                for s in gap_skill_names:
                    with st.spinner(f"Finding YouTube videos for {s}..."):
                        videos = search_youtube_videos(s, max_results=2)
                        youtube_results[s] = videos

                st.session_state['cp_youtube_results'] = youtube_results
                st.session_state['cp_learning_plan_generated'] = True

                xp_r = award_xp(email, "learning_plan")
                nb = unlock_badge(email, "learning_started")
                if nb:
                    st.session_state['cp_new_badges'].append(nb)
                show_xp_toast(xp_r['xp_gained'], "Learning plan generated")

                if not st.session_state['cp_report_saved']:
                    save_candidate_result(
                        st.session_state['cp_name'], email,
                        {'job_role': job_role, 'readiness_score': readiness,
                         'skill_scores': skill_scores, 'gap_analysis': gap_analysis,
                         'selection_chance': selection_chance,
                         'tab_violations': tab_violations, 'willingness_score': 70}
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
            st.info(f"Total time: **{total_time}** | Order: {' → '.join(order)}")

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
                        st.markdown(f"""
                        <div style="background:rgba(104,211,145,0.1);border-radius:10px;padding:10px;text-align:center;">
                            <div style="color:#a0aec0;font-size:11px;">Learn this</div>
                            <div style="color:#68d391;font-size:16px;font-weight:800;">↑ +10%</div>
                            <div style="color:#a0aec0;font-size:11px;">{selection_chance}% → {potential}%</div>
                        </div>
                        """, unsafe_allow_html=True)

                    videos = youtube_results.get(skill, [])
                    if videos:
                        st.markdown("**Best YouTube Resources:**")
                        for video in videos:
                            title = video.get('title', 'Watch Video')
                            url = video.get('url', '')
                            channel = video.get('channel', '')
                            views = video.get('view_count_display', 'N/A')
                            likes = video.get('like_count_display', 'N/A')
                            thumbnail = video.get('thumbnail', '')
                            video_id = video.get('video_id', '')

                            vc1, vc2 = st.columns([1, 4])
                            with vc1:
                                if thumbnail:
                                    st.markdown(f'<a href="{url}" target="_blank"><img src="{thumbnail}" style="width:120px;border-radius:8px;" /></a>', unsafe_allow_html=True)
                                elif video_id:
                                    st.markdown(f'<a href="{url}" target="_blank"><img src="https://img.youtube.com/vi/{video_id}/mqdefault.jpg" style="width:120px;border-radius:8px;" /></a>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<a href="{url}" target="_blank" style="display:flex;align-items:center;justify-content:center;width:120px;height:67px;background:#fc4444;border-radius:8px;color:white;font-size:24px;text-decoration:none;">▶</a>', unsafe_allow_html=True)
                            with vc2:
                                st.markdown(f"**{title}**")
                                st.markdown(f"📺 {channel} | 👁️ {views} views | 👍 {likes} likes")
                                if url:
                                    st.markdown(f"[▶ Watch on YouTube →]({url})")
                    else:
                        fallback = f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial+beginners"
                        st.markdown(f"""
                        <div style="background:#1a1a2e;border-radius:10px;padding:12px;border:1px solid #2d3748;margin:6px 0;">
                            <div style="display:flex;align-items:center;gap:12px;">
                                <a href="{fallback}" target="_blank" style="display:flex;align-items:center;justify-content:center;width:80px;height:50px;background:#fc4444;border-radius:8px;color:white;font-size:20px;text-decoration:none;min-width:80px;">▶</a>
                                <div>
                                    <div style="color:white;font-weight:700;">Search {skill} on YouTube</div>
                                    <div style="color:#718096;font-size:12px;">Best beginner tutorials</div>
                                    <a href="{fallback}" target="_blank" style="color:#63b3ed;font-size:12px;">Search now →</a>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    fc_key = f"fc_{skill}"
                    st.markdown("**Flashcards:**")
                    if fc_key not in st.session_state['cp_flashcards']:
                        if st.button(f"Generate Flashcards for {skill}", key=f"gen_fc_{skill}"):
                            with st.spinner("Generating..."):
                                try:
                                    level_str = determine_skill_level(skill_scores.get(skill, 5))
                                    prompt = FLASHCARD_PROMPT.format(skill=skill, level=level_str)
                                    resp = client.chat.completions.create(
                                        model="llama-3.3-70b-versatile",
                                        messages=[{"role": "user", "content": prompt}],
                                        temperature=0.7
                                    )
                                    raw = resp.choices[0].message.content.strip()
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
                                    st.error(f"Could not generate: {e}")
                    else:
                        flashcards = st.session_state['cp_flashcards'][fc_key]
                        flips = st.session_state['cp_flashcard_flip'].get(fc_key, [False] * len(flashcards))
                        fc_cols = st.columns(min(3, max(1, len(flashcards))))
                        for i, card in enumerate(flashcards):
                            with fc_cols[i % len(fc_cols)]:
                                is_flipped = flips[i] if i < len(flips) else False
                                if not is_flipped:
                                    st.markdown(f'<div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;padding:20px;text-align:center;color:white;min-height:90px;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:13px;">{card["front"]}</div>', unsafe_allow_html=True)
                                    if st.button("Flip →", key=f"flip_{skill}_{i}"):
                                        flips[i] = True
                                        st.session_state['cp_flashcard_flip'][fc_key] = flips
                                        st.rerun()
                                else:
                                    st.markdown(f'<div style="background:#1a1a2e;border-radius:12px;padding:20px;text-align:center;color:#a0aec0;min-height:90px;display:flex;align-items:center;justify-content:center;font-size:12px;border:2px solid #667eea;">{card["back"]}</div>', unsafe_allow_html=True)
                                    if st.button("← Back", key=f"unflip_{skill}_{i}"):
                                        flips[i] = False
                                        st.session_state['cp_flashcard_flip'][fc_key] = flips
                                        st.rerun()

            st.markdown("---")
            st.markdown("## Download Your Report")
            with st.spinner("Generating PDF..."):
                pdf_bytes = generate_pdf_report(
                    job_role=job_role, readiness_score=readiness,
                    skill_scores=skill_scores, skill_reasoning=skill_reasoning,
                    gap_analysis=gap_analysis, learning_plan=learning_plan,
                    youtube_results=youtube_results
                )
            award_xp(email, "pdf_downloaded")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"catalyst_{st.session_state['cp_name'].replace(' ','_')}_report.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 Start Over", use_container_width=True):
                    for key, value in defaults.items():
                        st.session_state[key] = value
                    st.rerun()
