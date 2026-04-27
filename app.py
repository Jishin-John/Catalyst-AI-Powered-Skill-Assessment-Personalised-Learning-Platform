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

    @keyframes fadeInUp {
        from {opacity:0;transform:translateY(30px);}
        to {opacity:1;transform:translateY(0);}
    }
    @keyframes float {
        0%,100% {transform:translateY(0px);}
        50% {transform:translateY(-12px);}
    }
    @keyframes shimmer {
        0% {background-position:-200% center;}
        100% {background-position:200% center;}
    }
    @keyframes pulse-glow {
        0%,100% {box-shadow:0 0 20px rgba(102,126,234,0.3);}
        50% {box-shadow:0 0 40px rgba(102,126,234,0.7);}
    }

    * {box-sizing:border-box;}

    .hero-wrap {
        min-height:100vh;
        background:linear-gradient(135deg,#0a0a1a 0%,#0d0d2b 40%,#0a1628 100%);
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        padding:40px 20px;
        position:relative;
        overflow:hidden;
    }
    .hero-wrap::before {
        content:'';
        position:absolute;
        width:600px;height:600px;
        border-radius:50%;
        background:radial-gradient(circle,rgba(102,126,234,0.15) 0%,transparent 70%);
        top:-100px;left:-100px;
        pointer-events:none;
    }
    .hero-wrap::after {
        content:'';
        position:absolute;
        width:400px;height:400px;
        border-radius:50%;
        background:radial-gradient(circle,rgba(240,147,251,0.1) 0%,transparent 70%);
        bottom:-50px;right:-50px;
        pointer-events:none;
    }
    .hero-logo {
        font-size:72px;
        animation:float 4s ease-in-out infinite;
        margin-bottom:16px;
        filter:drop-shadow(0 0 20px rgba(102,126,234,0.8));
    }
    .hero-title {
        font-size:64px;
        font-weight:900;
        background:linear-gradient(135deg,#667eea,#f093fb,#63b3ed);
        background-size:200% auto;
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        animation:shimmer 3s linear infinite,fadeInUp 0.8s ease;
        text-align:center;
        margin-bottom:12px;
        letter-spacing:-2px;
    }
    .hero-tagline {
        font-size:20px;
        color:#a0aec0;
        text-align:center;
        max-width:600px;
        line-height:1.6;
        animation:fadeInUp 1s ease 0.2s both;
        margin-bottom:40px;
    }
    .hero-tagline span {color:#63b3ed;font-weight:700;}
    .stats-row {
        display:flex;
        gap:24px;
        justify-content:center;
        flex-wrap:wrap;
        margin-bottom:48px;
        animation:fadeInUp 1s ease 0.4s both;
    }
    .stat-pill {
        background:rgba(102,126,234,0.1);
        border:1px solid rgba(102,126,234,0.3);
        border-radius:30px;
        padding:10px 24px;
        text-align:center;
        transition:all 0.3s ease;
    }
    .stat-pill:hover {
        background:rgba(102,126,234,0.2);
        border-color:rgba(102,126,234,0.6);
        transform:translateY(-3px);
    }
    .stat-pill .num {font-size:22px;font-weight:800;color:#667eea;}
    .stat-pill .lbl {font-size:11px;color:#718096;text-transform:uppercase;letter-spacing:1px;}
    .portals-row {
        display:flex;
        gap:24px;
        justify-content:center;
        flex-wrap:wrap;
        width:100%;
        max-width:900px;
        animation:fadeInUp 1s ease 0.6s both;
        margin-bottom:48px;
    }
    .portal-card {
        flex:1;
        min-width:300px;
        max-width:420px;
        border-radius:24px;
        padding:36px 28px;
        text-align:center;
        cursor:pointer;
        transition:all 0.4s ease;
        position:relative;
        overflow:hidden;
    }
    .portal-card::before {
        content:'';
        position:absolute;
        top:0;left:-100%;
        width:100%;height:100%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.05),transparent);
        transition:left 0.5s ease;
    }
    .portal-card:hover::before {left:100%;}
    .portal-card.candidate {
        background:linear-gradient(135deg,#1a1a3e,#0f1a4e);
        border:2px solid rgba(102,126,234,0.4);
    }
    .portal-card.candidate:hover {
        border-color:#667eea;
        transform:translateY(-10px) scale(1.02);
        animation:pulse-glow 2s ease infinite;
    }
    .portal-card.hr {
        background:linear-gradient(135deg,#2d1a3e,#3d0f4e);
        border:2px solid rgba(240,147,251,0.4);
    }
    .portal-card.hr:hover {
        border-color:#f093fb;
        transform:translateY(-10px) scale(1.02);
        box-shadow:0 20px 40px rgba(240,147,251,0.3);
    }
    .portal-icon {
        font-size:56px;
        margin-bottom:16px;
        animation:float 3s ease-in-out infinite;
    }
    .portal-card.hr .portal-icon {animation-delay:-1.5s;}
    .portal-title {font-size:26px;font-weight:800;color:white;margin-bottom:12px;}
    .portal-desc {font-size:14px;color:#a0aec0;line-height:1.7;margin-bottom:20px;}
    .feature-tags {
        display:flex;flex-wrap:wrap;gap:6px;
        justify-content:center;margin-bottom:24px;
    }
    .feature-tag {
        background:rgba(255,255,255,0.08);
        color:rgba(255,255,255,0.8);
        padding:4px 12px;border-radius:20px;
        font-size:11px;border:1px solid rgba(255,255,255,0.1);
        transition:all 0.2s;
    }
    .feature-tag:hover {
        background:rgba(255,255,255,0.15);
        border-color:rgba(255,255,255,0.3);
    }
    .how-section {
        width:100%;max-width:900px;
        animation:fadeInUp 1s ease 0.8s both;
        margin-bottom:40px;
    }
    .how-title {
        text-align:center;font-size:24px;
        font-weight:800;color:white;margin-bottom:24px;
    }
    .steps-row {
        display:flex;gap:16px;
        justify-content:center;flex-wrap:wrap;
    }
    .step-card {
        background:rgba(255,255,255,0.04);
        border:1px solid rgba(255,255,255,0.08);
        border-radius:16px;padding:20px 16px;
        text-align:center;flex:1;
        min-width:130px;max-width:160px;
        transition:all 0.3s ease;
    }
    .step-card:hover {
        background:rgba(102,126,234,0.1);
        border-color:rgba(102,126,234,0.3);
        transform:translateY(-6px);
    }
    .step-num {
        width:32px;height:32px;border-radius:50%;
        background:linear-gradient(135deg,#667eea,#764ba2);
        color:white;font-size:14px;font-weight:800;
        display:flex;align-items:center;justify-content:center;
        margin:0 auto 10px;
    }
    .step-icon {font-size:24px;margin-bottom:8px;}
    .step-label {font-size:12px;color:#a0aec0;font-weight:600;line-height:1.4;}
    .footer-bar {
        animation:fadeInUp 1s ease 1s both;
        text-align:center;color:#4a5568;
        font-size:13px;padding:16px;
    }
    .footer-bar span {color:#667eea;}

    .stPageLink a {
        display:block !important;
        text-align:center !important;
        background:linear-gradient(135deg,#667eea,#764ba2) !important;
        color:white !important;
        border-radius:50px !important;
        padding:14px 32px !important;
        font-weight:700 !important;
        font-size:15px !important;
        text-decoration:none !important;
        border:none !important;
        transition:all 0.3s !important;
        box-shadow:0 8px 24px rgba(102,126,234,0.4) !important;
        width:100% !important;
    }
    .stPageLink a:hover {
        box-shadow:0 12px 32px rgba(102,126,234,0.6) !important;
        transform:translateY(-2px) !important;
    }
    .hr-link a {
        background:linear-gradient(135deg,#f093fb,#f5576c) !important;
        box-shadow:0 8px 24px rgba(240,147,251,0.4) !important;
    }
    .hr-link a:hover {
        box-shadow:0 12px 32px rgba(240,147,251,0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- PARTICLES ---
import random
particles_html = ""
for i in range(20):
    left = random.randint(0, 100)
    delay = random.uniform(0, 8)
    duration = random.uniform(6, 14)
    size = random.randint(2, 5)
    r = random.randint(100, 200)
    g = random.randint(100, 200)
    particles_html += f"""
    <div style="position:absolute;left:{left}%;width:{size}px;height:{size}px;
    border-radius:50%;background:rgba({r},{g},234,0.5);
    animation:particle-float {duration}s linear {delay}s infinite;pointer-events:none;"></div>
    """

st.markdown(f"""
<style>
@keyframes particle-float {{
    0% {{transform:translateY(100vh) rotate(0deg);opacity:0;}}
    10% {{opacity:1;}}
    90% {{opacity:1;}}
    100% {{transform:translateY(-100px) rotate(720deg);opacity:0;}}
}}
</style>

<div class="hero-wrap">
    {particles_html}

    <div class="hero-logo">◈</div>
    <div class="hero-title">Catalyst</div>
    <div class="hero-tagline">
        A resume tells you what someone <span>claims</span> to know.<br>
        We find out what they <span>actually</span> know.
    </div>

    <div class="stats-row">
        <div class="stat-pill">
            <div class="num">AI</div>
            <div class="lbl">Powered Assessment</div>
        </div>
        <div class="stat-pill">
            <div class="num">Live</div>
            <div class="lbl">YouTube Resources</div>
        </div>
        <div class="stat-pill">
            <div class="num">Real</div>
            <div class="lbl">Skill Verification</div>
        </div>
        <div class="stat-pill">
            <div class="num">XP</div>
            <div class="lbl">Gamified Learning</div>
        </div>
    </div>

    <div class="portals-row">
        <div class="portal-card candidate">
            <div class="portal-icon">🎯</div>
            <div class="portal-title">Candidate Portal</div>
            <div class="portal-desc">
                Get assessed on your real skills through an AI interview.
                Earn XP, unlock badges, and get a personalised learning roadmap.
            </div>
            <div class="feature-tags">
                <span class="feature-tag">AI Interview</span>
                <span class="feature-tag">MCQ Tests</span>
                <span class="feature-tag">Anti-Cheat</span>
                <span class="feature-tag">XP + Badges</span>
                <span class="feature-tag">Debug Challenges</span>
                <span class="feature-tag">Skill Sprint</span>
                <span class="feature-tag">YouTube Resources</span>
                <span class="feature-tag">PDF Report</span>
            </div>
        </div>

        <div class="portal-card hr">
            <div class="portal-icon">👔</div>
            <div class="portal-title">HR Portal</div>
            <div class="portal-desc">
                View all candidate assessments, track progress,
                compare candidates and make data-driven hiring decisions.
            </div>
            <div class="feature-tags">
                <span class="feature-tag">Leaderboard</span>
                <span class="feature-tag">Comparison</span>
                <span class="feature-tag">Progress Tracking</span>
                <span class="feature-tag">Hire Chance %</span>
                <span class="feature-tag">Integrity Score</span>
                <span class="feature-tag">Analytics</span>
                <span class="feature-tag">Willingness Score</span>
                <span class="feature-tag">Badge View</span>
            </div>
        </div>
    </div>

    <div class="how-section">
        <div class="how-title">How it works</div>
        <div class="steps-row">
            <div class="step-card">
                <div class="step-num">1</div>
                <div class="step-icon">📄</div>
                <div class="step-label">Upload JD + Resume</div>
            </div>
            <div class="step-card">
                <div class="step-num">2</div>
                <div class="step-icon">🤖</div>
                <div class="step-label">AI Extracts Skills</div>
            </div>
            <div class="step-card">
                <div class="step-num">3</div>
                <div class="step-icon">💬</div>
                <div class="step-label">MCQ + Interview</div>
            </div>
            <div class="step-card">
                <div class="step-num">4</div>
                <div class="step-icon">📊</div>
                <div class="step-label">Score + Gap Analysis</div>
            </div>
            <div class="step-card">
                <div class="step-num">5</div>
                <div class="step-icon">🎓</div>
                <div class="step-label">Learning Plan</div>
            </div>
            <div class="step-card">
                <div class="step-num">6</div>
                <div class="step-icon">📥</div>
                <div class="step-label">Download PDF</div>
            </div>
        </div>
    </div>

    <div class="footer-bar">
        ◈ Catalyst — Built for <span>Deccan AI Catalyst Hackathon 2026</span> |
        Powered by <span>Agentic AI</span> + <span>Groq</span> + <span>YouTube API</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="stPageLink">', unsafe_allow_html=True)
        st.page_link(
            "pages/Candidate_Portal.py",
            label="🎯 Enter Candidate Portal",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stPageLink hr-link">', unsafe_allow_html=True)
        st.page_link(
            "pages/HR_Portal.py",
            label="👔 Enter HR Portal",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
