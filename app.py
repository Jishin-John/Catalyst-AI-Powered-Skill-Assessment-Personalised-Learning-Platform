import streamlit as st

st.set_page_config(
    page_title="Catalyst — AI Skill Assessment Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {display:none;}
    .main > div {padding-top:0rem;}
    header {display:none;}
    @keyframes fadeInUp {from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
    @keyframes float {0%,100%{transform:translateY(0);}50%{transform:translateY(-12px);}}
    @keyframes shimmer {0%{background-position:-200% center;}100%{background-position:200% center;}}
    .hero-wrap {
        background:linear-gradient(135deg,#0a0a1a 0%,#0d0d2b 40%,#0a1628 100%);
        padding:60px 20px 40px;
        text-align:center;
        border-radius:20px;
        margin-bottom:30px;
    }
    .hero-logo {font-size:72px;animation:float 4s ease-in-out infinite;display:block;margin-bottom:16px;}
    .hero-title {
        font-size:56px;font-weight:900;
        background:linear-gradient(135deg,#667eea,#f093fb,#63b3ed);
        background-size:200% auto;
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        animation:shimmer 3s linear infinite;
        margin-bottom:12px;
    }
    .hero-tagline {font-size:18px;color:#a0aec0;max-width:600px;margin:0 auto 40px;line-height:1.6;}
    .hero-tagline span {color:#63b3ed;font-weight:700;}
    .stats-row {display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:40px;}
    .stat-pill {background:rgba(102,126,234,0.1);border:1px solid rgba(102,126,234,0.3);border-radius:30px;padding:10px 24px;}
    .stat-pill .num {font-size:20px;font-weight:800;color:#667eea;}
    .stat-pill .lbl {font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:1px;}
    .portal-wrap {display:flex;gap:24px;justify-content:center;flex-wrap:wrap;margin-bottom:40px;}
    .portal-card {
        flex:1;min-width:280px;max-width:420px;
        border-radius:20px;padding:32px 24px;
        text-align:center;border:2px solid rgba(102,126,234,0.4);
        background:linear-gradient(135deg,#1a1a3e,#0f1a4e);
        transition:all 0.3s;
    }
    .portal-card.hr {background:linear-gradient(135deg,#2d1a3e,#3d0f4e);border-color:rgba(240,147,251,0.4);}
    .portal-card:hover {transform:translateY(-8px);}
    .portal-icon {font-size:48px;margin-bottom:12px;display:block;}
    .portal-title {font-size:24px;font-weight:800;color:white;margin-bottom:10px;}
    .portal-desc {font-size:13px;color:#a0aec0;line-height:1.6;margin-bottom:16px;}
    .feature-tags {display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-bottom:0;}
    .feature-tag {background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;}
    .steps-row {display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:30px;}
    .step-card {
        background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
        border-radius:14px;padding:16px 12px;text-align:center;
        flex:1;min-width:110px;max-width:140px;
    }
    .step-num {
        width:28px;height:28px;border-radius:50%;
        background:linear-gradient(135deg,#667eea,#764ba2);
        color:white;font-size:13px;font-weight:800;
        display:flex;align-items:center;justify-content:center;margin:0 auto 8px;
    }
    .step-icon {font-size:22px;margin-bottom:6px;}
    .step-label {font-size:11px;color:#a0aec0;font-weight:600;}
    .footer-txt {text-align:center;color:#4a5568;font-size:13px;padding:16px 0;}
    .footer-txt span {color:#667eea;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-wrap">
    <span class="hero-logo">◈</span>
    <div class="hero-title">Catalyst</div>
    <div class="hero-tagline">
        A resume tells you what someone <span>claims</span> to know.<br>
        We find out what they <span>actually</span> know.
    </div>

    <div class="stats-row">
        <div class="stat-pill"><div class="num">AI</div><div class="lbl">Powered Assessment</div></div>
        <div class="stat-pill"><div class="num">Live</div><div class="lbl">YouTube Resources</div></div>
        <div class="stat-pill"><div class="num">Real</div><div class="lbl">Skill Verification</div></div>
        <div class="stat-pill"><div class="num">XP</div><div class="lbl">Gamified Learning</div></div>
    </div>

    <div class="portal-wrap">
        <div class="portal-card">
            <span class="portal-icon">🎯</span>
            <div class="portal-title">Candidate Portal</div>
            <div class="portal-desc">Get assessed on real skills. Earn XP, unlock badges, get a personalised learning roadmap.</div>
            <div class="feature-tags">
                <span class="feature-tag">AI Interview</span>
                <span class="feature-tag">MCQ Tests</span>
                <span class="feature-tag">Anti-Cheat</span>
                <span class="feature-tag">XP + Badges</span>
                <span class="feature-tag">Debug Challenges</span>
                <span class="feature-tag">Skill Sprint</span>
                <span class="feature-tag">YouTube</span>
                <span class="feature-tag">PDF Report</span>
            </div>
        </div>
        <div class="portal-card hr">
            <span class="portal-icon">👔</span>
            <div class="portal-title">HR Portal</div>
            <div class="portal-desc">View all candidate assessments, compare candidates and make data-driven hiring decisions.</div>
            <div class="feature-tags">
                <span class="feature-tag">Leaderboard</span>
                <span class="feature-tag">Comparison</span>
                <span class="feature-tag">Hire Chance %</span>
                <span class="feature-tag">Integrity Score</span>
                <span class="feature-tag">Analytics</span>
                <span class="feature-tag">Willingness</span>
                <span class="feature-tag">Badge View</span>
            </div>
        </div>
    </div>

    <div class="steps-row">
        <div class="step-card"><div class="step-num">1</div><div class="step-icon">📄</div><div class="step-label">Upload JD + Resume</div></div>
        <div class="step-card"><div class="step-num">2</div><div class="step-icon">🤖</div><div class="step-label">AI Extracts Skills</div></div>
        <div class="step-card"><div class="step-num">3</div><div class="step-icon">💬</div><div class="step-label">MCQ + Interview</div></div>
        <div class="step-card"><div class="step-num">4</div><div class="step-icon">📊</div><div class="step-label">Score + Gap Analysis</div></div>
        <div class="step-card"><div class="step-num">5</div><div class="step-icon">🎓</div><div class="step-label">Learning Plan</div></div>
        <div class="step-card"><div class="step-num">6</div><div class="step-icon">📥</div><div class="step-label">Download PDF</div></div>
    </div>

    <div class="footer-txt">
        ◈ Catalyst — Built for <span>Deccan AI Catalyst Hackathon 2026</span> |
        Powered by <span>Agentic AI</span> + <span>Groq</span> + <span>YouTube API</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎯 Candidate Portal", type="primary", use_container_width=True):
            st.switch_page("pages/Candidate_Portal.py")
    with c2:
        if st.button("👔 HR Portal", use_container_width=True):
            st.switch_page("pages/HR_Portal.py")
