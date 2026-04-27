import streamlit as st
import plotly.graph_objects as go
from utils.storage import load_all_candidates, calculate_willingness_score, calculate_selection_chance
from utils.gamification import get_leaderboard, get_level, ALL_BADGES

st.set_page_config(
    page_title="Catalyst — HR Portal",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLEAN CSS TO MATCH SCREENSHOTS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {display:none;}
    header {visibility: hidden;}
    .main > div {padding-top: 1rem; background-color: #0e1117;}

    /* Metric Cards */
    .metric-container {
        background: #1c1e27;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2d3748;
    }
    .metric-value { font-size: 28px; font-weight: 800; margin-bottom: 2px; }
    .metric-label { color: #808495; font-size: 11px; text-transform: capitalize; }

    /* Comparison Bar */
    .cmp-card {
        background: #161b22;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        border: 1px solid #30363d;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .winner-tag { color: #68d391; font-size: 10px; font-weight: 700; margin-top: 2px; }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: transparent !important;
        border: none !important;
        color: #808495 !important;
    }
    .stTabs [aria-selected="true"] {
        color: white !important;
        border-bottom: 2px solid #ff4b4b !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_h1, col_h2 = st.columns([1, 8])
with col_h1:
    if st.button("← Home"): st.switch_page("app.py")
with col_h2:
    st.markdown("### 👔 HR Portal — Hiring Intelligence Dashboard")

# --- DATA PROCESSING ---
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
        'name': data.get('name', 'Unknown'),
        'readiness': latest.get('readiness_score', 0),
        'selection_chance': selection_chance,
        'willingness': willingness,
        'xp': xp,
        'skill_scores': latest.get('skill_scores', {}),
        'badges': data.get('badges', []),
        'sprint_best': data.get('skill_sprint_best', 0),
        'tab_violations': latest.get('tab_violations', 0)
    })

# --- TOP METRICS BAR ---
m1, m2, m3, m4, m5, m6 = st.columns(6)
metrics = [
    (len(candidates_list), "Total Candidates", "#63b3ed"),
    (sum(1 for c in candidates_list if c['readiness'] >= 70), "Job Ready (70%+)", "#68d391"),
    (round(sum(c['readiness'] for c in candidates_list)/len(candidates_list)) if candidates_list else 0, "Avg Readiness %", "#f6ad55"),
    (sum(1 for c in candidates_list if c['selection_chance'] >= 70), "High Hire Chance", "#b794f4"),
    (round(sum(c['xp'] for c in candidates_list)/len(candidates_list)) if candidates_list else 0, "Avg XP Earned", "#f093fb"),
    (sum(1 for c in candidates_list if c['tab_violations'] == 0), "Zero Violations", "#68d391")
]

for col, (val, label, color) in zip([m1, m2, m3, m4, m5, m6], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color:{color};">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# --- NAVIGATION TABS ---
tab_lb, tab_comp, tab_prof, tab_ana = st.tabs(["🏆 Leaderboard", "📊 Comparison", "👥 Profiles", "📈 Analytics"])

# COMPARISON TAB (Matching Image 1 & 2)
with tab_comp:
    st.markdown("#### 📊 Interactive Candidate Comparison")
    
    c_names = [c['name'] for c in candidates_list]
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1: name_a = st.selectbox("Candidate A", c_names, index=0)
    with col_sel2: name_b = st.selectbox("Candidate B", c_names, index=min(1, len(c_names)-1))
    
    cA = next(c for c in candidates_list if c['name'] == name_a)
    cB = next(c for c in candidates_list if c['name'] == name_b)

    metrics_to_show = [
        ("Readiness %", cA['readiness'], cB['readiness']),
        ("Selection Chance %", cA['selection_chance'], cB['selection_chance']),
        ("Willingness %", cA['willingness'], cB['willingness']),
        ("XP Earned", cA['xp'], cB['xp']),
        ("Badges", len(cA['badges']), len(cB['badges'])),
        ("Sprint Best", cA['sprint_best'], cB['sprint_best'])
    ]

    for label, vA, vB in metrics_to_show:
        winA = vA > vB
        winB = vB > vA
        st.markdown(f"""
        <div class="cmp-card">
            <div style="width:100px; text-align:center;">
                <div style="font-size:22px; font-weight:800; color:{'#68d391' if winA else '#fc8181' if winB else '#fff'};">{vA}</div>
                {"<div class='winner-tag'>WINNER</div>" if winA else ""}
            </div>
            <div style="color:#808495; font-size:12px; font-weight:600;">{label}</div>
            <div style="width:100px; text-align:center;">
                <div style="font-size:22px; font-weight:800; color:{'#68d391' if winB else '#fc8181' if winA else '#fff'};">{vB}</div>
                {"<div class='winner-tag'>WINNER</div>" if winB else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # RADAR CHART (Matching Image 4)
    st.markdown("<br>", unsafe_allow_html=True)
    all_skills = list(set(list(cA['skill_scores'].keys()) + list(cB['skill_scores'].keys())))
    if len(all_skills) >= 3:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[cA['skill_scores'].get(s,0) for s in all_skills], theta=all_skills, fill='toself', name=name_a, line_color='#f093fb'))
        fig.add_trace(go.Scatterpolar(r=[cB['skill_scores'].get(s,0) for s in all_skills], theta=all_skills, fill='toself', name=name_b, line_color='#63b3ed'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # BADGES ROW (Matching Image 4 footer)
    b1, b2 = st.columns(2)
    with b1:
        st.markdown(f"**{name_a} — Badges**")
        badges_a = "".join([f"<span title='{b['id']}'>{b['icon']}</span> " for b in ALL_BADGES if b['id'] in cA['badges']])
        st.markdown(f"<div style='background:#1c1e27; padding:15px; border-radius:10px;'>{badges_a if badges_a else 'No badges'}</div>", unsafe_allow_html=True)
    with b2:
        st.markdown(f"**{name_b} — Badges**")
        badges_b = "".join([f"<span title='{b['id']}'>{b['icon']}</span> " for b in ALL_BADGES if b['id'] in cB['badges']])
        st.markdown(f"<div style='background:#1c1e27; padding:15px; border-radius:10px;'>{badges_b if badges_b else 'No badges'}</div>", unsafe_allow_html=True)

    # RECOMMENDATION
    winner_name = name_a if cA['selection_chance'] > cB['selection_chance'] else name_b
    st.markdown(f"""
    <div style="background:rgba(104,211,145,0.1); border:1px solid #68d391; border-radius:12px; padding:20px; text-align:center; margin-top:20px;">
        <div style="color:#808495; font-size:12px;">Overall Recommendation</div>
        <div style="color:#68d391; font-size:24px; font-weight:800;">🏆 {winner_name}</div>
        <div style="color:#50535c; font-size:11px;">Based on readiness, hire chance, willingness and integrity</div>
    </div>
    """, unsafe_allow_html=True)

# Other tabs would follow similar clean logic...
