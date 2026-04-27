import streamlit as st

st.set_page_config(
    page_title="Catalyst — AI Skill Assessment Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to match the screenshots exactly
st.markdown("""
<style>
    /* Hide Streamlit elements */
    [data-testid="stSidebar"] {display: none;}
    header {visibility: hidden;}
    .main > div {padding-top: 2rem; background-color: #0e1117;}

    /* Hero Section */
    .hero {
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 20px;
    }
    
    .hero-logo { font-size: 50px; color: white; margin-bottom: 10px; }
    .hero-title { font-size: 52px; font-weight: 700; color: white; margin-top: -10px; }
    .hero-subtitle { color: #808495; font-size: 18px; margin-bottom: 30px; }
    
    /* Stats Row */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 50px;
        margin-bottom: 30px;
    }
    .stat-box { text-align: center; }
    .stat-val { font-size: 32px; font-weight: 700; color: #5dade2; }
    .stat-lab { font-size: 12px; color: #808495; margin-top: -5px; }
    
    .hero-footer { color: #50535c; font-size: 14px; font-style: italic; margin-bottom: 40px; }

    /* Portal Cards */
    .card {
        border-radius: 30px;
        padding: 60px 40px;
        text-align: center;
        min-height: 450px;
        display: flex;
        flex-direction: column;
        align-items: center;
        color: white;
    }
    
    .candidate-card {
        background: linear-gradient(135deg, #7b68ee 0%, #a29bfe 100%);
    }
    
    .hr-card {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%, #fecfef 100%);
    }

    .card-icon { font-size: 60px; margin-bottom: 20px; }
    .card-title { font-size: 32px; font-weight: 700; margin-bottom: 15px; }
    .card-desc { font-size: 16px; opacity: 0.9; line-height: 1.4; margin-bottom: 30px; max-width: 400px; }

    /* Badges/Pills */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 8px;
        max-width: 450px;
    }
    .badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        backdrop-filter: blur(5px);
    }

    /* Standardizing Button Spacing */
    div.stButton > button {
        border-radius: 10px;
        height: 50px;
        font-weight: 600;
        border: none;
        margin-top: 10px;
    }
    
    /* Red Button for Candidate */
    .candidate-btn div.stButton > button {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    /* Dark Button for HR */
    .hr-btn div.stButton > button {
        background-color: #1c1e23 !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero">
    <div class="hero-logo">◈</div>
    <div class="hero-title">Catalyst</div>
    <div class="hero-subtitle">AI-Powered Skill Assessment & Personalised Learning Platform</div>
    <div class="stats-container">
        <div class="stat-box"><div class="stat-val">AI</div><div class="stat-lab">Powered Assessment</div></div>
        <div class="stat-box"><div class="stat-val">Live</div><div class="stat-lab">YouTube Resources</div></div>
        <div class="stat-box"><div class="stat-val">Real</div><div class="stat-lab">Skill Verification</div></div>
        <div class="stat-box"><div class="stat-val">Smart</div><div class="stat-lab">Learning Plans</div></div>
    </div>
    <div class="hero-footer">A resume tells you what someone claims to know — not how well they actually know it.</div>
</div>
""", unsafe_allow_html=True)

# --- Portal Columns ---
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="card candidate-card">
        <div class="card-icon">🎯</div>
        <div class="card-title">Candidate Portal</div>
        <div class="card-desc">
            Get assessed on your real skills through an AI-powered interview. Discover your gaps and get a personalised learning roadmap.
        </div>
        <div class="badge-container">
            <div class="badge">AI Interview</div>
            <div class="badge">Skill Scoring</div>
            <div class="badge">Anti-Cheat Timer</div>
            <div class="badge">Learning Plan</div>
            <div class="badge">YouTube Resources</div>
            <div class="badge">PDF Report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="candidate-btn">', unsafe_allow_html=True)
    if st.button("Enter Candidate Portal →", use_container_width=True, key="c_btn"):
        st.switch_page("pages/Candidate_Portal.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card hr-card" style="color: #333;">
        <div class="card-icon">👔</div>
        <div class="card-title">HR Portal</div>
        <div class="card-desc">
            View all candidate assessments, track progress over time, and make data-driven hiring decisions with detailed analytics.
        </div>
        <div class="badge-container">
            <div class="badge" style="background: rgba(0,0,0,0.05);">Candidate Dashboard</div>
            <div class="badge" style="background: rgba(0,0,0,0.05);">Progress Tracking</div>
            <div class="badge" style="background: rgba(0,0,0,0.05);">Selection Chances</div>
            <div class="badge" style="background: rgba(0,0,0,0.05);">Willingness Score</div>
            <div class="badge" style="background: rgba(0,0,0,0.05);">Comparison View</div>
            <div class="badge" style="background: rgba(0,0,0,0.05);">Analytics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="hr-btn">', unsafe_allow_html=True)
    if st.button("Enter HR Portal →", use_container_width=True, key="h_btn"):
        st.switch_page("pages/HR_Portal.py")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<p style="text-align: center; color: #50535c; font-size: 13px;">
    ◈ Catalyst — Built for Deccan AI Hackathon 2026 | Powered by Agentic AI + Groq + YouTube API
</p>
""", unsafe_allow_html=True)
