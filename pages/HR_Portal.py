import streamlit as st
import plotly.graph_objects as go
from utils.storage import load_all_candidates, calculate_willingness_score, calculate_selection_chance
from utils.gamification import get_leaderboard, get_level, ALL_BADGES

# 1. Page Configuration
st.set_page_config(page_title="Catalyst — HR Intelligence", page_icon="👔", layout="wide")

# 2. Sleek Custom Styling
st.markdown("""
<style>
    [data-testid="stSidebar"] {display:none;}
    .main {background-color: #0e1117;}
    
    /* Metric Cards */
    .metric-card {
        background: #1a1c24;
        border: 1px solid #2d3139;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-val { font-size: 28px; font-weight: 800; margin-bottom: 5px; }
    .metric-label { font-size: 12px; color: #808495; text-transform: uppercase; letter-spacing: 1px; }

    /* Comparison Row */
    .comp-row {
        background: #161922;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid #3e4451;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .winner-tag { color: #00ffaa; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 3. Data Processing
all_candidates = load_all_candidates()
candidates_list = []

for email, data in all_candidates.items():
    latest = data.get('latest', {})
    attempts = data.get('attempts', [])
    willingness = calculate_willingness_score(attempts)
    xp = data.get('xp', 0)
    selection_chance = calculate_selection_chance(
        latest.get('readiness_score', 0), 
        latest.get('tab_violations', 0), 
        willingness
    )
    candidates_list.append({
        'name': data.get('name', 'Candidate'),
        'email': email,
        'readiness': latest.get('readiness_score', 0),
        'selection_chance': selection_chance,
        'willingness': willingness,
        'xp': xp,
        'badges': data.get('badges', []),
        'skill_scores': latest.get('skill_scores', {})
    })

# --- HEADER ---
c1, c2 = st.columns([1, 5])
with c1: st.page_link("app.py", label="Home")
with c2: st.title("👔 Hiring Intelligence Dashboard")

# --- TOP METRICS ---
m1, m2, m3, m4, m5 = st.columns(5)
metrics = [
    (len(candidates_list), "Total Applicants", "#63b3ed"),
    (sum(1 for c in candidates_list if c['readiness'] >= 70), "Job Ready", "#68d391"),
    (sum(1 for c in candidates_list if c['selection_chance'] >= 75), "High Potential", "#f6ad55"),
    (round(sum(c['xp'] for c in candidates_list)/len(candidates_list)) if candidates_list else 0, "Avg XP", "#b794f4"),
    (sum(1 for c in all_candidates.values() if c.get('latest',{}).get('tab_violations')==0), "Integrity Pass", "#00ffaa")
]

for col, (val, label, color) in zip([m1, m2, m3, m4, m5], metrics):
    col.markdown(f"""<div class="metric-card"><div class="metric-val" style="color:{color}">{val}</div><div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

# --- DASHBOARD TABS ---
tab_comp, tab_leader, tab_analytics = st.tabs(["📊 Candidate Comparison", "🏆 Leaderboard", "📈 Market Analytics"])

# ══════════════════════════════════════
# COMPARISON TAB (Fixing the </div> error)
# ══════════════════════════════════════
with tab_comp:
    col_a, col_b = st.columns(2)
    names = [c['name'] for c in candidates_list]
    
    with col_a: cand_a_name = st.selectbox("Select Candidate A", names, index=0)
    with col_b: cand_b_name = st.selectbox("Select Candidate B", names, index=min(1, len(names)-1))
    
    ca = next(c for c in candidates_list if c['name'] == cand_a_name)
    cb = next(c for c in candidates_list if c['name'] == cand_b_name)

    st.subheader("Head-to-Head Comparison")
    
    comp_metrics = [
        ("Readiness %", ca['readiness'], cb['readiness']),
        ("Hire Chance %", ca['selection_chance'], cb['selection_chance']),
        ("Willingness %", ca['willingness'], cb['willingness']),
        ("Engagement (XP)", ca['xp'], cb['xp'])
    ]

    for label, val_a, val_b in comp_metrics:
        win_a = "WINNER" if val_a > val_b else ""
        win_b = "WINNER" if val_b > val_a else ""
        
        st.markdown(f"""
        <div class="comp-row">
            <div style="width:20%; text-align:center;">
                <b style="font-size:20px; color:#63b3ed;">{val_a}</b><br><span class="winner-tag">{win_a}</span>
            </div>
            <div style="width:60%; text-align:center; color:#808495; font-size:14px; font-weight:bold;">{label}</div>
            <div style="width:20%; text-align:center;">
                <b style="font-size:20px; color:#f6ad55;">{val_b}</b><br><span class="winner-tag">{win_b}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Radar Chart
    st.write("### Skill Distribution")
    skills = list(set(list(ca['skill_scores'].keys()) + list(cb['skill_scores'].keys())))
    if len(skills) >= 3:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[ca['skill_scores'].get(s, 0) for s in skills], theta=skills, fill='toself', name=ca['name'], line_color='#63b3ed'))
        fig.add_trace(go.Scatterpolar(r=[cb['skill_scores'].get(s, 0) for s in skills], theta=skills, fill='toself', name=cb['name'], line_color='#f6ad55'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════
# LEADERBOARD TAB
# ══════════════════════════════════════
with tab_leader:
    st.subheader("Global Talent Leaderboard")
    lb_data = get_leaderboard()
    for entry in lb_data:
        st.markdown(f"""
        <div style="background:#1a1c24; padding:15px; border-radius:10px; margin-bottom:10px; display:flex; align-items:center; border: 1px solid #2d3139;">
            <div style="font-size:24px; margin-right:20px; width:40px;">#{entry['rank']}</div>
            <div style="flex-grow:1;">
                <div style="font-weight:bold; font-size:16px;">{entry['name']}</div>
                <div style="color:#808495; font-size:12px;">{entry.get('job_role', 'General Applicant')}</div>
            </div>
            <div style="text-align:right;">
                <div style="color:#f6ad55; font-weight:bold;">{entry['xp']} XP</div>
                <div style="color:#68d391; font-size:12px;">{entry['readiness']}% Readiness</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════
# ANALYTICS TAB
# ══════════════════════════════════════
with tab_analytics:
    st.subheader("Hiring Pipeline Analytics")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("Readiness Distribution")
        fig_hist = go.Figure(data=[go.Histogram(x=[c['readiness'] for c in candidates_list], marker_color='#63b3ed')])
        fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_chart2:
        st.write("Willingness vs Selection Chance")
        fig_scat = go.Figure(data=[go.Scatter(x=[c['willingness'] for c in candidates_list], y=[c['selection_chance'] for c in candidates_list], mode='markers', marker=dict(size=12, color='#f6ad55'))])
        fig_scat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=300)
        st.plotly_chart(fig_scat, use_container_width=True)
