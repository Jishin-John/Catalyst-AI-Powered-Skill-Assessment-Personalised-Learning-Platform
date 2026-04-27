import streamlit as st

st.set_page_config(
    page_title="Catalyst — AI Skill Assessment",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the "Modern Dark" aesthetic
st.markdown("""
<style>
    /* Hide Default Elements */
    [data-testid="stSidebar"] {display: none;}
    header {visibility: hidden;}
    .main > div {padding-top: 2rem;}

    /* Background Container */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a3a, #070717);
    }

    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 3rem 1rem;
        margin-bottom: 2rem;
    }

    .main-logo {
        font-size: 80px;
        margin-bottom: 0;
        background: linear-gradient(to bottom, #ffffff, #63b3ed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-title {
        font-size: 64px;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 10px;
        color: white;
    }

    .hero-subtitle {
        color: #a0aec0;
        font-size: 20px;
        max-width: 700px;
        margin: 0 auto 40px auto;
    }

    /* Glass Cards */
    .portal-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        height: 100%;
        transition: transform 0.3s ease, border 0.3s ease;
        text-align: center;
    }

    .portal-card:hover {
        transform: translateY(-10px);
        border-color: #63b3ed;
        background: rgba(255, 255, 255, 0.05);
    }

    .portal-icon {
        font-size: 50px;
        margin-bottom: 20px;
    }

    .portal-name {
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin-bottom: 15px;
    }

    .portal-text {
        color: #718096;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 25px;
    }

    /* Feature Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin: 4px;
        background: rgba(99, 179, 237, 0.1);
        color: #63b3ed;
        border: 1px solid rgba(99, 179, 237, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown(f"""
<div class="hero-container">
    <div class="main-logo">◈</div>
    <h1 class="hero-title">Catalyst</h1>
    <p class="hero-subtitle">
        Bridging the gap between <b>claims</b> and <b>competence</b>. 
        AI-driven skill verification for the modern workforce.
    </p>
</div>
""", unsafe_allow_html=True)

# Portal Selection
col_left, col_c1, col_space, col_c2, col_right = st.columns([1, 4, 1, 4, 1])

with col_c1:
    st.markdown("""
    <div class="portal-card">
        <div class="portal-icon">🎯</div>
        <div class="portal-name">Candidate Portal</div>
        <p class="portal-text">
            Validate your expertise through adaptive AI interviews, 
            earn verified credentials, and follow a custom learning roadmap.
        </p>
        <div style="margin-bottom: 20px;">
            <span class="badge">AI INTERVIEW</span>
            <span class="badge">XP SYSTEM</span>
            <span class="badge">LEARNING PATH</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Enter Candidate Portal", type="primary", use_container_width=True, key="c_btn"):
        st.switch_page("pages/Candidate_Portal.py")

with col_c2:
    st.markdown("""
    <div class="portal-card">
        <div class="portal-icon">👔</div>
        <div class="portal-name">HR Portal</div>
        <p class="portal-text">
            Access high-signal candidate data, compare skill distributions, 
            and hire with confidence using integrity-backed analytics.
        </p>
        <div style="margin-bottom: 20px;">
            <span class="badge">DASHBOARD</span>
            <span class="badge">INTEGRITY SCORE</span>
            <span class="badge">HIRE CHANCE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Enter HR Portal", use_container_width=True, key="h_btn"):
        st.switch_page("pages/HR_Portal.py")

# Footer Process Steps
st.markdown("<br><br>", unsafe_allow_html=True)
steps_cols = st.columns(5)
steps = [
    ("📄", "Extract"), 
    ("🤖", "Analyze"), 
    ("💬", "Assess"), 
    ("📊", "Verify"), 
    ("🎓", "Improve")
]

for i, col in enumerate(steps_cols):
    with col:
        st.markdown(f"""
        <div style="text-align: center; opacity: 0.6;">
            <div style="font-size: 24px;">{steps[i][0]}</div>
            <div style="font-size: 12px; color: white; font-weight: 600; margin-top: 5px;">{steps[i][1]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #4a5568; font-size: 12px; letter-spacing: 1px;">
    BUILT FOR DECCAN AI HACKATHON 2026 | AGENTIC AI + GROQ + YOUTUBE API
</div>
""", unsafe_allow_html=True)
