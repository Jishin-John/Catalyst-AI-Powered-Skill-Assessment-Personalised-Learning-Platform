import streamlit as st
import plotly.graph_objects as go
from utils.storage import load_all_candidates, calculate_willingness_score, calculate_selection_chance
from utils.gamification import (
    get_leaderboard, get_profile_summary, get_level,
    get_all_badges_status, ALL_BADGES
)

st.set_page_config(
    page_title="Catalyst — HR Portal",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {display:none;}

    @keyframes fadeInUp {
        from {opacity:0;transform:translateY(16px);}
        to {opacity:1;transform:translateY(0);}
    }

    .stat-card {
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:16px;
        padding:20px;
        text-align:center;
        border:1px solid #2d3748;
        animation:fadeInUp 0.4s ease;
    }
    .leaderboard-row {
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:12px;
        padding:14px 18px;
        margin:6px 0;
        border:1px solid #2d3748;
        display:flex;
        align-items:center;
        gap:16px;
        animation:fadeInUp 0.3s ease;
    }
    .leaderboard-row.top1 {border-color:#f6ad55;box-shadow:0 0 20px rgba(246,173,85,0.2);}
    .leaderboard-row.top2 {border-color:#a0aec0;box-shadow:0 0 12px rgba(160,174,192,0.15);}
    .leaderboard-row.top3 {border-color:#f6855a;box-shadow:0 0 12px rgba(246,133,90,0.15);}
    .tag {
        display:inline-block;
        padding:3px 10px;
        border-radius:12px;
        font-size:11px;
        font-weight:700;
        margin:2px;
    }
    .tag-green {background:rgba(104,211,145,0.15);color:#68d391;}
    .tag-red {background:rgba(252,129,129,0.15);color:#fc8181;}
    .section-title {
        font-size:20px;
        font-weight:800;
        color:white;
        margin:20px 0 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col1, col2 = st.columns([1, 6])
with col1:
 st.page_link("app.py", label="← Home")
with col2:
    st.markdown("### 👔 HR Portal — Hiring Intelligence Dashboard")

st.markdown("---")

all_candidates = load_all_candidates()
leaderboard = get_leaderboard(top_n=50)

if not all_candidates:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;">
        <div style="font-size:60px;margin-bottom:16px;">📭</div>
        <div style="font-size:22px;font-weight:700;color:white;margin-bottom:8px;">No candidates yet</div>
        <div style="color:#718096;">Share the Candidate Portal with applicants.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/Candidate_Portal.py", label="Go to Candidate Portal")
    st.stop()

# --- BUILD CANDIDATES LIST ---
candidates_list = []
for email, data in all_candidates.items():
    latest = data.get('latest', {})
    attempts = data.get('attempts', [])
    willingness = calculate_willingness_score(attempts)
    xp = data.get('xp', 0)
    level = get_level(xp)
    selection_chance = calculate_selection_chance(
        latest.get('readiness_score', 0),
        latest.get('tab_violations', 0),
        willingness
    )
    candidates_list.append({
        'name': data.get('name', 'Unknown'),
        'email': email,
        'job_role': latest.get('job_role', 'N/A'),
        'readiness': latest.get('readiness_score', 0),
        'selection_chance': selection_chance,
        'willingness': willingness,
        'tab_violations': latest.get('tab_violations', 0),
        'attempts': len(attempts),
        'skill_scores': latest.get('skill_scores', {}),
        'gap_analysis': latest.get('gap_analysis', {}),
        'xp': xp,
        'level': level,
        'badges_count': len(data.get('badges', [])),
        'badges': data.get('badges', []),
        'sprint_best': data.get('skill_sprint_best', 0),
        'streak': data.get('streak', 0)
    })

candidates_list.sort(key=lambda x: x['selection_chance'], reverse=True)

# --- SUMMARY METRICS ---
total = len(candidates_list)
strong = sum(1 for c in candidates_list if c['readiness'] >= 70)
avg_r = round(sum(c['readiness'] for c in candidates_list) / total) if total else 0
avg_xp = round(sum(c['xp'] for c in candidates_list) / total) if total else 0
high_chance = sum(1 for c in candidates_list if c['selection_chance'] >= 70)
honest = sum(1 for c in candidates_list if c['tab_violations'] == 0)

col1, col2, col3, col4, col5, col6 = st.columns(6)
for col, (val, label, color) in zip(
    [col1, col2, col3, col4, col5, col6],
    [
        (total,      "Total Candidates",  "#63b3ed"),
        (strong,     "Job Ready (70%+)",  "#68d391"),
        (avg_r,      "Avg Readiness %",   "#f6ad55"),
        (high_chance,"High Hire Chance",  "#b794f4"),
        (avg_xp,     "Avg XP Earned",     "#f093fb"),
        (honest,     "Zero Violations",   "#68d391"),
    ]
):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:26px;color:{color};font-weight:800;">{val}</div>
            <div style="color:#a0aec0;font-size:11px;margin-top:4px;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Leaderboard",
    "📊 Comparison",
    "👥 Profiles",
    "📈 Analytics"
])

# ═══════════════════════════════════
# TAB 1 — LEADERBOARD
# ═══════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">🏆 Top Candidates by XP</div>', unsafe_allow_html=True)

    rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}

    for entry in leaderboard:
        rank = entry['rank']
        row_class = f"top{rank}" if rank <= 3 else ""
        rank_display = rank_icons.get(rank, f"#{rank}")

        st.markdown(f"""
        <div class="leaderboard-row {row_class}">
            <div style="font-size:22px;min-width:36px;text-align:center;">{rank_display}</div>
            <div style="flex:1;">
                <div style="color:white;font-weight:700;font-size:14px;">{entry['name']}</div>
                <div style="color:#718096;font-size:11px;">{entry.get('job_role','N/A')}</div>
            </div>
            <div style="text-align:center;min-width:60px;">
                <div style="font-size:18px;">{entry['level_icon']}</div>
                <div style="color:#a0aec0;font-size:10px;">{entry['level']}</div>
            </div>
            <div style="text-align:center;min-width:70px;">
                <div style="color:#f6ad55;font-weight:800;font-size:16px;">{entry['xp']}</div>
                <div style="color:#a0aec0;font-size:10px;">XP</div>
            </div>
            <div style="text-align:center;min-width:60px;">
                <div style="color:#b794f4;font-weight:800;font-size:16px;">🏅 {entry['badges_count']}</div>
                <div style="color:#a0aec0;font-size:10px;">badges</div>
            </div>
            <div style="text-align:center;min-width:70px;">
                <div style="color:#68d391;font-weight:800;font-size:16px;">{entry['readiness']}%</div>
                <div style="color:#a0aec0;font-size:10px;">readiness</div>
            </div>
            <div style="text-align:center;min-width:70px;">
                <div style="color:#f6ad55;font-weight:800;font-size:16px;">⚡ {entry['sprint_best']}</div>
                <div style="color:#a0aec0;font-size:10px;">sprint</div>
            </div>
            <div style="text-align:center;min-width:60px;">
                <div style="color:#fc8181;font-weight:800;font-size:16px;">🔥 {entry['streak']}</div>
                <div style="color:#a0aec0;font-size:10px;">streak</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if leaderboard:
        st.markdown("#### XP Distribution")
        names = [e['name'] for e in leaderboard[:10]]
        xps = [e['xp'] for e in leaderboard[:10]]
        bar_colors = [
            '#f6ad55' if i == 0 else '#a0aec0' if i == 1
            else '#f6855a' if i == 2 else '#667eea'
            for i in range(len(names))
        ]
        fig_lb = go.Figure(go.Bar(
            x=names, y=xps,
            marker_color=bar_colors,
            text=[f"{x} XP" for x in xps],
            textposition='outside',
            textfont=dict(color='white')
        ))
        fig_lb.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=300,
            xaxis=dict(color='white', showgrid=False),
            yaxis=dict(color='white', showgrid=False),
            margin=dict(t=20, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_lb, use_container_width=True)

# ═══════════════════════════════════
# TAB 2 — COMPARISON
# ═══════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">📊 Interactive Candidate Comparison</div>', unsafe_allow_html=True)

    if len(candidates_list) < 2:
        st.info("Need at least 2 candidates to compare.")
    else:
        names_all = [c['name'] for c in candidates_list]
        col1, col2 = st.columns(2)
        with col1:
            c1_name = st.selectbox("Candidate A", names_all, index=0)
        with col2:
            c2_name = st.selectbox("Candidate B", names_all,
                                   index=min(1, len(names_all)-1))

        c1 = next((c for c in candidates_list if c['name'] == c1_name), None)
        c2 = next((c for c in candidates_list if c['name'] == c2_name), None)

        if c1 and c2 and c1_name != c2_name:
            st.markdown("")

            metrics_cmp = [
                ("Readiness %",       c1['readiness'],        c2['readiness']),
                ("Selection Chance %", c1['selection_chance'], c2['selection_chance']),
                ("Willingness %",     c1['willingness'],      c2['willingness']),
                ("XP Earned",         c1['xp'],               c2['xp']),
                ("Badges",            c1['badges_count'],     c2['badges_count']),
                ("Sprint Best",       c1['sprint_best'],      c2['sprint_best']),
            ]

            for label, v1, v2 in metrics_cmp:
                winner = 1 if v1 > v2 else 2 if v2 > v1 else 0
                c1_col = "#68d391" if winner == 1 else "#fc8181" if winner == 2 else "#f6ad55"
                c2_col = "#68d391" if winner == 2 else "#fc8181" if winner == 1 else "#f6ad55"

                w1 = '<div style="color:#68d391;font-size:10px;font-weight:700;">WINNER</div>' if winner == 1 else ''
                w2 = '<div style="color:#68d391;font-size:10px;font-weight:700;">WINNER</div>' if winner == 2 else ''

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:10px;padding:12px 16px;margin:5px 0;border:1px solid #2d3748;">
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <div style="text-align:center;min-width:100px;">
                            <div style="font-size:20px;font-weight:800;color:{c1_col};">{v1}</div>
                            {w1}
                        </div>
                        <div style="flex:1;text-align:center;color:#a0aec0;font-size:12px;font-weight:600;">{label}</div>
                        <div style="text-align:center;min-width:100px;">
                            <div style="font-size:20px;font-weight:800;color:{c2_col};">{v2}</div>
                            {w2}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            skills1 = c1.get('skill_scores', {})
            skills2 = c2.get('skill_scores', {})
            all_skills = list(set(list(skills1.keys()) + list(skills2.keys())))

            if len(all_skills) >= 3:
                st.markdown("#### Skill Radar Comparison")
                s1_vals = [skills1.get(s, 0) for s in all_skills]
                s2_vals = [skills2.get(s, 0) for s in all_skills]
                theta = all_skills + [all_skills[0]]

                fig_cmp = go.Figure()
                fig_cmp.add_trace(go.Scatterpolar(
                    r=s1_vals + [s1_vals[0]], theta=theta,
                    fill='toself',
                    fillcolor='rgba(102,126,234,0.2)',
                    line=dict(color='#667eea', width=2),
                    name=c1_name
                ))
                fig_cmp.add_trace(go.Scatterpolar(
                    r=s2_vals + [s2_vals[0]], theta=theta,
                    fill='toself',
                    fillcolor='rgba(240,147,251,0.2)',
                    line=dict(color='#f093fb', width=2),
                    name=c2_name
                ))
                fig_cmp.update_layout(
                    polar=dict(radialaxis=dict(
                        visible=True, range=[0, 10],
                        tickfont=dict(color='#718096')
                    )),
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=380,
                    legend=dict(
                        bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    ),
                    margin=dict(t=30, b=30, l=30, r=30)
                )
                st.plotly_chart(fig_cmp, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"#### {c1_name} — Badges")
                c1_badges = [b for b in ALL_BADGES if b['id'] in c1.get('badges', [])]
                if c1_badges:
                    icons = " ".join([f'<span style="font-size:20px;" title="{b["name"]}">{b["icon"]}</span>' for b in c1_badges])
                    st.markdown(f'<div style="background:#1a1a2e;border-radius:10px;padding:12px;">{icons}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#718096;font-size:13px;">No badges yet</div>', unsafe_allow_html=True)

            with col2:
                st.markdown(f"#### {c2_name} — Badges")
                c2_badges = [b for b in ALL_BADGES if b['id'] in c2.get('badges', [])]
                if c2_badges:
                    icons = " ".join([f'<span style="font-size:20px;" title="{b["name"]}">{b["icon"]}</span>' for b in c2_badges])
                    st.markdown(f'<div style="background:#1a1a2e;border-radius:10px;padding:12px;">{icons}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#718096;font-size:13px;">No badges yet</div>', unsafe_allow_html=True)

            st.markdown("")
            winner_name = (
                c1_name if c1['selection_chance'] > c2['selection_chance']
                else c2_name if c2['selection_chance'] > c1['selection_chance']
                else "Tied"
            )
            st.markdown(f"""
            <div style="background:rgba(104,211,145,0.08);border:1px solid rgba(104,211,145,0.3);border-radius:14px;padding:18px;text-align:center;">
                <div style="color:#a0aec0;font-size:12px;">Overall Recommendation</div>
                <div style="color:#68d391;font-size:22px;font-weight:800;margin-top:8px;">
                    {'🏆 ' + winner_name if winner_name != 'Tied' else '🤝 Both are equal'}
                </div>
                <div style="color:#718096;font-size:12px;margin-top:6px;">Based on readiness, hire chance, willingness and integrity</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════
# TAB 3 — INDIVIDUAL PROFILES
# ═══════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">👥 Individual Candidate Profiles</div>', unsafe_allow_html=True)

    for c in candidates_list:
        readiness = c['readiness']
        chance = c['selection_chance']
        violations = c['tab_violations']
        xp = c['xp']
        level = c['level']
        integrity = max(0, 100 - violations * 15)

        rank_tag = (
            "🥇 Top Candidate" if chance >= 70
            else "🥈 Moderate Match" if chance >= 50
            else "🥉 Needs Development"
        )

        with st.expander(
            f"{level['icon']} {c['name']} — {c['job_role']} | "
            f"{chance}% hire chance | {xp} XP",
            expanded=False
        ):
            col1, col2, col3, col4 = st.columns(4)
            for col, (label, val, color) in zip(
                [col1, col2, col3, col4],
                [
                    ("Readiness",  f"{readiness}%", "#667eea"),
                    ("Hire Chance",f"{chance}%",    "#68d391"),
                    ("Willingness",f"{c['willingness']}%","#f6ad55"),
                    ("Integrity",  f"{integrity}%", "#b794f4"),
                ]
            ):
                with col:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div style="font-size:22px;color:{color};font-weight:800;">{val}</div>
                        <div style="color:#a0aec0;font-size:11px;margin-top:4px;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div style="background:#1a1a2e;border-radius:12px;padding:14px;border:1px solid #2d3748;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                        <span style="font-size:26px;">{level['icon']}</span>
                        <div>
                            <div style="color:white;font-weight:700;">{level['name']}</div>
                            <div style="color:#a0aec0;font-size:11px;">{xp} XP</div>
                        </div>
                    </div>
                    <div style="display:flex;gap:14px;flex-wrap:wrap;">
                        <div style="text-align:center;">
                            <div style="color:#b794f4;font-weight:800;">🏅 {c['badges_count']}</div>
                            <div style="color:#a0aec0;font-size:10px;">badges</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="color:#f6ad55;font-weight:800;">⚡ {c['sprint_best']}</div>
                            <div style="color:#a0aec0;font-size:10px;">sprint</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="color:#fc8181;font-weight:800;">🔥 {c['streak']}</div>
                            <div style="color:#a0aec0;font-size:10px;">streak</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="color:#68d391;font-weight:800;">📝 {c['attempts']}</div>
                            <div style="color:#a0aec0;font-size:10px;">attempts</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                skill_scores = c.get('skill_scores', {})
                if skill_scores:
                    snames = list(skill_scores.keys())
                    svals = list(skill_scores.values())
                    colors_s = [
                        '#68d391' if s >= 7 else '#f6ad55' if s >= 5 else '#fc8181'
                        for s in svals
                    ]
                    fig_ind = go.Figure(go.Bar(
                        x=svals, y=snames, orientation='h',
                        marker_color=colors_s,
                        text=[f"{s}/10" for s in svals],
                        textposition='outside',
                        textfont=dict(color='white')
                    ))
                    fig_ind.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=200,
                        xaxis=dict(range=[0, 12], color='white', showgrid=False),
                        yaxis=dict(color='white'),
                        margin=dict(t=5, b=5, l=5, r=40)
                    )
                    st.plotly_chart(fig_ind, use_container_width=True)

            gap = c.get('gap_analysis', {})
            strong_s = gap.get('strong_skills', [])
            gap_s = gap.get('gap_skills', [])

            if strong_s:
                tags = " ".join([
                    f'<span class="tag tag-green">{s.split("(")[0].strip()}</span>'
                    for s in strong_s
                ])
                st.markdown(f"**Strong:** {tags}", unsafe_allow_html=True)
            if gap_s:
                tags = " ".join([
                    f'<span class="tag tag-red">{s.split("(")[0].strip()}</span>'
                    for s in gap_s
                ])
                st.markdown(f"**Gaps:** {tags}", unsafe_allow_html=True)

            unlocked = [b for b in ALL_BADGES if b['id'] in c.get('badges', [])]
            if unlocked:
                icons = " ".join([
                    f'<span style="font-size:16px;" title="{b["name"]}">{b["icon"]}</span>'
                    for b in unlocked
                ])
                st.markdown(f"**Badges:** {icons}", unsafe_allow_html=True)

            st.markdown(f"**Rank:** {rank_tag}")

            if violations > 2:
                st.warning(f"⚠️ {violations} tab switches — review integrity")
            if c['willingness'] >= 70:
                st.success("✅ High willingness to learn")
            if xp >= 500:
                st.success("🎮 Highly engaged on platform")

# ═══════════════════════════════════
# TAB 4 — ANALYTICS
# ═══════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">📈 Hiring Analytics</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Readiness Distribution")
        readiness_vals = [c['readiness'] for c in candidates_list]
        fig_hist = go.Figure(go.Histogram(
            x=readiness_vals, nbinsx=10,
            marker_color='#667eea', opacity=0.85
        ))
        fig_hist.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=280,
            xaxis=dict(title='Readiness %', color='white', showgrid=False),
            yaxis=dict(title='Count', color='white', showgrid=False),
            margin=dict(t=10, b=40, l=40, r=10)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.markdown("#### Selection Chance vs Readiness")
        fig_scatter = go.Figure(go.Scatter(
            x=[c['readiness'] for c in candidates_list],
            y=[c['selection_chance'] for c in candidates_list],
            mode='markers+text',
            text=[c['name'] for c in candidates_list],
            textposition='top center',
            textfont=dict(color='white', size=10),
            marker=dict(
                size=14,
                color=[c['xp'] for c in candidates_list],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title='XP',
                    tickfont=dict(color='white')
                )
            )
        ))
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=280,
            xaxis=dict(title='Readiness %', color='white', showgrid=False),
            yaxis=dict(title='Selection %', color='white', showgrid=False),
            margin=dict(t=10, b=40, l=40, r=10)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Willingness vs Hire Chance")
        names_s = [c['name'] for c in candidates_list]
        fig_will = go.Figure()
        fig_will.add_trace(go.Bar(
            name='Willingness %',
            x=names_s,
            y=[c['willingness'] for c in candidates_list],
            marker_color='#f6ad55'
        ))
        fig_will.add_trace(go.Bar(
            name='Hire Chance %',
            x=names_s,
            y=[c['selection_chance'] for c in candidates_list],
            marker_color='#68d391'
        ))
        fig_will.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=280,
            xaxis=dict(color='white', showgrid=False),
            yaxis=dict(color='white', range=[0, 100], showgrid=False),
            legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white')),
            margin=dict(t=10, b=40, l=40, r=10)
        )
        st.plotly_chart(fig_will, use_container_width=True)

    with col2:
        st.markdown("#### Level Distribution")
        level_counts = {}
        for c in candidates_list:
            lname = c['level']['name']
            level_counts[lname] = level_counts.get(lname, 0) + 1

        level_colors = {
            'Rookie': '#a0aec0', 'Learner': '#63b3ed',
            'Skilled': '#68d391', 'Advanced': '#f6ad55',
            'Expert': '#b794f4', 'Master': '#fc8181'
        }
        lnames = list(level_counts.keys())
        lvals = list(level_counts.values())
        lcolors = [level_colors.get(n, '#667eea') for n in lnames]

        fig_pie = go.Figure(go.Pie(
            labels=lnames, values=lvals,
            marker=dict(colors=lcolors),
            textfont=dict(color='white'),
            hole=0.4
        ))
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=280,
            legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='white')),
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Average Skill Scores Across All Candidates")

    all_skill_scores = {}
    for c in candidates_list:
        for skill, score in c.get('skill_scores', {}).items():
            if skill not in all_skill_scores:
                all_skill_scores[skill] = []
            all_skill_scores[skill].append(score)

    if all_skill_scores:
        avg_by_skill = {
            k: round(sum(v) / len(v), 1)
            for k, v in all_skill_scores.items()
        }
        avg_by_skill = dict(
            sorted(avg_by_skill.items(), key=lambda x: x[1], reverse=True)
        )

        fig_skills = go.Figure(go.Bar(
            x=list(avg_by_skill.values()),
            y=list(avg_by_skill.keys()),
            orientation='h',
            marker_color=[
                '#68d391' if v >= 7 else '#f6ad55' if v >= 5 else '#fc8181'
                for v in avg_by_skill.values()
            ],
            text=[f"{v}/10" for v in avg_by_skill.values()],
            textposition='outside',
            textfont=dict(color='white')
        ))
        fig_skills.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=max(250, len(avg_by_skill) * 35),
            xaxis=dict(range=[0, 12], color='white', showgrid=False),
            yaxis=dict(color='white'),
            margin=dict(t=10, b=10, l=10, r=50)
        )
        st.plotly_chart(fig_skills, use_container_width=True)

        weakest = min(avg_by_skill, key=avg_by_skill.get)
        strongest = max(avg_by_skill, key=avg_by_skill.get)
        st.info(
            f"📊 Strongest: **{strongest}** ({avg_by_skill[strongest]}/10) | "
            f"Biggest gap: **{weakest}** ({avg_by_skill[weakest]}/10)"
        )
