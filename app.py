import streamlit as st

st.set_page_config(
    page_title="Catalyst — AI Skill Assessment",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebar"]{display:none;}
header{visibility:hidden;}
.block-container{padding-top:2rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown("# ◈ Catalyst")
    st.markdown("### AI-Powered Skill Assessment & Personalised Learning Platform")
    st.markdown("> *A resume tells you what someone **claims** to know — not how well they actually know it.*")
    st.markdown("---")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("AI", "Powered", "Assessment")
    with col_b:
        st.metric("Live", "YouTube", "Resources")
    with col_c:
        st.metric("XP", "Gamified", "Learning")
    with col_d:
        st.metric("Real", "Skills", "Only")

    st.markdown("---")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("### 🎯 Candidate Portal")
        st.markdown("""
**For job seekers and candidates.**

Get assessed on your real skills through an AI interview system.
Earn XP, unlock badges, and receive a personalised learning roadmap.

**Features:**
- AI-powered conversational interview
- Timed MCQ tests with anti-cheat
- Debug code challenges
- Trade-off decision scenarios
- Skill Sprint rapid-fire game
- Live YouTube video recommendations
- XP, levels and achievement badges
- Downloadable PDF assessment report
        """)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎯 Enter Candidate Portal", type="primary", use_container_width=True):
            st.switch_page("pages/Candidate_Portal.py")

    with col_p2:
        st.markdown("### 👔 HR Portal")
        st.markdown("""
**For hiring managers and recruiters.**

View all candidate assessments, track progress over time,
and make data-driven hiring decisions with full analytics.

**Features:**
- Candidate leaderboard ranked by XP
- Side-by-side candidate comparison
- Hire chance percentage per candidate
- Tab violation and integrity tracking
- Willingness to learn score
- Skill radar chart comparison
- Full analytics dashboard
- Badge collection view per candidate
        """)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👔 Enter HR Portal", use_container_width=True):
            st.switch_page("pages/HR_Portal.py")

    st.markdown("---")

    st.markdown("#### How it works")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    steps = [
        ("📄", "Upload JD + Resume"),
        ("🤖", "AI Extracts Skills"),
        ("💬", "MCQ + Interview"),
        ("📊", "Gap Analysis"),
        ("🎓", "Learning Plan"),
        ("📥", "Download PDF"),
    ]
    for col, (icon, label) in zip([col1,col2,col3,col4,col5,col6], steps):
        with col:
            st.markdown(f"**{icon}**")
            st.caption(label)

    st.markdown("---")
    st.caption("◈ Catalyst — Built for Deccan AI Catalyst Hackathon 2026 | Powered by Agentic AI + Groq + YouTube API")
