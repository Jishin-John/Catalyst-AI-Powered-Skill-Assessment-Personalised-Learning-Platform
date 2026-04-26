import streamlit as st

st.set_page_config(
    page_title="Catalyst — AI Skill Assessment Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    .main > div {padding-top: 0rem;}
    
    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 60px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 40px;
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    
    @keyframes pulse {
        0%, 100% {transform: scale(1);}
        50% {transform: scale(1.05);}
    }
    
    .hero-title {
        font-size: 56px;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 20px;
        color: #a0aec0;
        margin-bottom: 40px;
    }
    
    .portal-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 40px 30px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        animation: fadeIn 1.2s ease-in;
    }
    
    .portal-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    .portal-card-hr {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .portal-card-hr:hover {
        box-shadow: 0 20px 40px rgba(240, 147, 251, 0.4);
    }
    
    .portal-icon {
        font-size: 60px;
        margin-bottom: 20px;
    }
    
    .portal-title {
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin-bottom: 10px;
    }
    
    .portal-desc {
        font-size: 15px;
        color: rgba(255,255,255,0.85);
        line-height: 1.6;
        margin-bottom: 20px;
    }
    
    .feature-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        margin: 3px;
    }
    
    .stats-row {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin: 30px 0;
    }
    
    .stat-item {
        text-align: center;
        color: white;
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: 800;
        color: #63b3ed;
    }
    
    .stat-label {
        font-size: 14px;
        color: #a0aec0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="portal-icon">◈</div>
    <div class="hero-title">Catalyst</div>
    <div class="hero-subtitle">AI-Powered Skill Assessment & Personalised Learning Platform</div>
    <div class="stats-row">
        <div class="stat-item">
            <div class="stat-number">AI</div>
            <div class="stat-label">Powered Assessment</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">Live</div>
            <div class="stat-label">YouTube Resources</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">Real</div>
            <div class="stat-label">Skill Verification</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">Smart</div>
            <div class="stat-label">Learning Plans</div>
        </div>
    </div>
    <p style="color: #718096; font-size: 16px;">A resume tells you what someone claims to know — not how well they actually know it.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="portal-card">
        <div class="portal-icon">🎯</div>
        <div class="portal-title">Candidate Portal</div>
        <div class="portal-desc">
            Get assessed on your real skills through an AI-powered interview.
            Discover your gaps and get a personalised learning roadmap.
        </div>
        <div>
            <span class="feature-badge">AI Interview</span>
            <span class="feature-badge">Skill Scoring</span>
            <span class="feature-badge">Anti-Cheat Timer</span>
            <span class="feature-badge">Learning Plan</span>
            <span class="feature-badge">YouTube Resources</span>
            <span class="feature-badge">PDF Report</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
   if st.button("Enter Candidate Portal →", type="primary", use_container_width=True):
    st.switch_page("Candidate_Portal")
       
with col2:
    st.markdown("""
    <div class="portal-card portal-card-hr">
        <div class="portal-icon">👔</div>
        <div class="portal-title">HR Portal</div>
        <div class="portal-desc">
            View all candidate assessments, track progress over time,
            and make data-driven hiring decisions with detailed analytics.
        </div>
        <div>
            <span class="feature-badge">Candidate Dashboard</span>
            <span class="feature-badge">Progress Tracking</span>
            <span class="feature-badge">Selection Chances</span>
            <span class="feature-badge">Willingness Score</span>
            <span class="feature-badge">Comparison View</span>
            <span class="feature-badge">Analytics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Enter HR Portal →", use_container_width=True):
    st.switch_page("HR_Portal")
st.markdown("---")
st.markdown("""
<p style="text-align: center; color: #718096; font-size: 14px;">
    ◈ Catalyst — Built for Deccan AI Hackathon 2026 | Powered by Agentic AI + Groq + YouTube API
</p>
""", unsafe_allow_html=True)
