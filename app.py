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
header{display:none;}
.main > div{padding-top:0;}
@keyframes float{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
@keyframes shimmer{0%{background-position:-200% center;}100%{background-position:200% center;}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#0a0a1a,#0d0d2b,#0a1628);padding:60px 20px 40px;border-radius:20px;text-align:center;margin-bottom:30px;">
    <div style="font-size:64px;animation:float 4s ease-in-out infinite;margin-bottom:16px;">◈</div>
    <div style="font-size:52px;font-weight:900;background:linear-gradient(135deg,#667eea,#f093fb,#63b3ed);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;">Catalyst</div>
    <div style="font-size:18px;color:#a0aec0;max-width:580px;margin:0 auto 36px;line-height:1.6;">A resume tells you what someone <span style="color:#63b3ed;font-weight:700;">claims</span> to know. We find out what they <span style="color:#63b3ed;font-weight:700;">actually</span> know.</div>

    <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-bottom:36px;">
        <div style="background:rgba(102,126,234,0.12);border:1px solid rgba(102,126,234,0.3);border-radius:30px;padding:8px 20px;">
            <div style="font-size:18px;font-weight:800;color:#667eea;">AI</div>
            <div style="font-size:10px;color:#718096;text-transform:uppercase;letter-spacing:1px;">Powered</div>
        </div>
        <div style="background:rgba(102,126,234,0.12);border:1px solid rgba(102,126,234,0.3);border-radius:30px;padding:8px 20px;">
            <div style="font-size:18px;font-weight:800;color:#667eea;">Live</div>
            <div style="font-size:10px;color:#718096;text-transform:uppercase;letter-spacing:1px;">YouTube</div>
        </div>
        <div style="background:rgba(102,126,234,0.12);border:1px solid rgba(102,126,234,0.3);border-radius:30px;padding:8px 20px;">
            <div style="font-size:18px;font-weight:800;color:#667eea;">XP</div>
            <div style="font-size:10px;color:#718096;text-transform:uppercase;letter-spacing:1px;">Gamified</div>
        </div>
        <div style="background:rgba(102,126,234,0.12);border:1px solid rgba(102,126,234,0.3);border-radius:30px;padding:8px 20px;">
            <div style="font-size:18px;font-weight:800;color:#667eea;">Real</div>
            <div style="font-size:10px;color:#718096;text-transform:uppercase;letter-spacing:1px;">Skills Only</div>
        </div>
    </div>

    <div style="display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin-bottom:36px;">
        <div style="flex:1;min-width:260px;max-width:380px;background:linear-gradient(135deg,#1a1a3e,#0f1a4e);border:2px solid rgba(102,126,234,0.4);border-radius:18px;padding:28px 20px;">
            <div style="font-size:44px;margin-bottom:10px;">🎯</div>
            <div style="font-size:22px;font-weight:800;color:white;margin-bottom:8px;">Candidate Portal</div>
            <div style="font-size:13px;color:#a0aec0;line-height:1.6;margin-bottom:14px;">Get assessed on real skills. Earn XP, unlock badges, get a personalised learning roadmap.</div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;justify-content:center;">
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">AI Interview</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">MCQ Tests</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">Anti-Cheat</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">XP + Badges</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">YouTube</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">PDF Report</span>
            </div>
        </div>
        <div style="flex:1;min-width:260px;max-width:380px;background:linear-gradient(135deg,#2d1a3e,#3d0f4e);border:2px solid rgba(240,147,251,0.4);border-radius:18px;padding:28px 20px;">
            <div style="font-size:44px;margin-bottom:10px;">👔</div>
            <div style="font-size:22px;font-weight:800;color:white;margin-bottom:8px;">HR Portal</div>
            <div style="font-size:13px;color:#a0aec0;line-height:1.6;margin-bottom:14px;">View assessments, compare candidates and make data-driven hiring decisions.</div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;justify-content:center;">
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">Leaderboard</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">Comparison</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">Hire Chance</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">Analytics</span>
                <span style="background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.8);padding:3px 10px;border-radius:20px;font-size:11px;">Integrity</span>
            </div>
        </div>
    </div>

    <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:30px;">
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 10px;text-align:center;min-width:100px;">
            <div style="font-size:20px;">📄</div>
            <div style="font-size:11px;color:#a0aec0;font-weight:600;margin-top:4px;">Upload JD + Resume</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 10px;text-align:center;min-width:100px;">
            <div style="font-size:20px;">🤖</div>
            <div style="font-size:11px;color:#a0aec0;font-weight:600;margin-top:4px;">AI Extracts Skills</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 10px;text-align:center;min-width:100px;">
            <div style="font-size:20px;">💬</div>
            <div style="font-size:11px;color:#a0aec0;font-weight:600;margin-top:4px;">MCQ + Interview</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 10px;text-align:center;min-width:100px;">
            <div style="font-size:20px;">📊</div>
            <div style="font-size:11px;color:#a0aec0;font-weight:600;margin-top:4px;">Gap Analysis</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 10px;text-align:center;min-width:100px;">
            <div style="font-size:20px;">🎓</div>
            <div style="font-size:11px;color:#a0aec0;font-weight:600;margin-top:4px;">Learning Plan</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px 10px;text-align:center;min-width:100px;">
            <div style="font-size:20px;">📥</div>
            <div style="font-size:11px;color:#a0aec0;font-weight:600;margin-top:4px;">Download PDF</div>
        </div>
    </div>

    <div style="color:#4a5568;font-size:13px;">◈ Catalyst — Built for <span style="color:#667eea;">Deccan AI Catalyst Hackathon 2026</span> | Powered by <span style="color:#667eea;">Agentic AI + Groq + YouTube API</span></div>
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
