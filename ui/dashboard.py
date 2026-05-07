import streamlit as st
import upload.db as db
import pandas as pd
from ui.styles import THEMES, ACCENTS
from core.gemini_engine import ask_gemini

def _t():
    return THEMES.get(st.session_state.get("theme", "light"), THEMES["light"])

def render_dashboard():
    u = st.session_state.user
    t = _t()
    
    # ── Welcome Section ──────────────────────────────────────────────
    st.markdown(f"<h1 id='welcome-to-cognix'>Welcome back, <span class='username-highlight'>{u['name']}</span></h1>", unsafe_allow_html=True)


    stats = db.get_dashboard_stats(u['id'])



    # ── Stats Row (Massive) ──────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    
    def metric_card(col, title, value, label=""):
        with col:
            with st.container(border=True):
                st.markdown(f"<div style='text-align:center; padding: 12px 0;'>"
                            f"<div style='font-size:20px; color:{t['muted']}; text-transform:uppercase; font-weight:700; letter-spacing:0.05em;'>{title}</div>"
                            f"<div style='font-size:56px; font-weight:800; color:{t['text']}; margin: 12px 0;'>{value}</div>"
                            f"<div style='font-size:18px; color:{t['muted']}; font-weight:500;'>{label}</div>"
                            f"</div>", unsafe_allow_html=True)

    
    def render_metric(title, value, label, color_type):
        with st.container(border=True):
            st.markdown(f"<div style='text-align:center; padding: 12px 0;'>"
                        f"<div style='font-size:20px; color:{t['muted']}; text-transform:uppercase; font-weight:700; letter-spacing:0.05em;'>{title}</div>"
                        f"<div style='font-size:56px; font-weight:800; color:{t['text']}; margin: 12px 0;'>{value}</div>"
                        f"<div style='font-size:18px; color:{t['muted']}; font-weight:500;'>{label}</div>"
                        f"</div>", unsafe_allow_html=True)

    # 2. METRICS ROW
    cols = st.columns(4)
    with cols[0]:
        render_metric("TOPICS", stats['topics_completed'], "Total Completed", "blue")
    with cols[1]:
        render_metric("ACCURACY", f"{int(stats['avg_accuracy'])}%", "Avg Proficiency", "green")
    with cols[2]:
        render_metric("WEAK", stats['weak_count'], "To Improve", "orange")
    with cols[3]:
        # Active is currently selected or recently accessed
        active_count = len(stats.get('active_topics', []))
        render_metric("ACTIVE", active_count, "Neural Paths", "purple")

    st.write("")
    
    # 3. PREMIUM PROGRESS VISUALIZATION
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0; color:#1E293B;'>🎯 Academic Mastery</h3>", unsafe_allow_html=True)
        
        c_left, c_right = st.columns([1, 1.2])
        progress_data = db.get_overall_progress_data(u['id'])
        
        if progress_data:
            try:
                import plotly.graph_objects as go
                
                # --- LEFT: OVERALL DONUT ---
                with c_left:
                    labels = ['Completed', 'Learning', 'Unstarted']
                    values = [progress_data['completed'], progress_data['learning'], progress_data['unstarted']]
                    colors = ['#10B981', '#3B82F6', '#F1F5F9']
                    
                    total = max(1, sum(values))
                    fig = go.Figure(data=[go.Pie(
                        labels=labels, 
                        values=values, 
                        hole=.75, 
                        marker_colors=colors,
                        textinfo='none',
                        hoverinfo='label+percent'
                    )])
                    fig.update_layout(
                        showlegend=False,
                        annotations=[dict(text=f"{int(progress_data['completed']/total*100)}%", x=0.5, y=0.5, font_size=48, font_color='#1E293B', font_family='Inter', showarrow=False)],
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=280,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("<div style='text-align:center; font-size:14px; color:#64748B; font-weight:500;'>Overall Curriculum</div>", unsafe_allow_html=True)

                # --- RIGHT: SUBJECT-WISE PREMIUM BARS ---
                with c_right:
                    subj_stats = db.get_subject_completion_stats(u['id'])
                    if subj_stats:
                        subj_names = [s['subject'] for s in subj_stats]
                        # 50/50 logic for consistency
                        subj_perc = []
                        for s in subj_stats:
                            # Re-calculate with tiered logic for the graph
                            # Note: db returns raw completion count. 
                            # We'll assume topics studied but not completed are 'learning'
                            # But for simplicity in bar, we use the completed %
                            p = (s['completed_topics'] or 0) / max(1, s['total_topics']) * 100
                            subj_perc.append(p)

                        fig_subj = go.Figure(go.Bar(
                            x=subj_perc,
                            y=subj_names,
                            orientation='h',
                            marker=dict(
                                color=subj_perc,
                                colorscale=[[0, '#DBEAFE'], [1, '#3B82F6']],
                                line=dict(width=0),
                            ),
                            text=[f"{int(p)}%" for p in subj_perc],
                            textposition='outside',
                            width=0.6,
                        ))
                        fig_subj.update_layout(
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 115]),
                            yaxis=dict(showgrid=False, zeroline=False, autorange="reversed", tickfont=dict(size=14, color='#475569')),
                            margin=dict(l=0, r=0, t=20, b=0),
                            height=280,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                        )
                        st.plotly_chart(fig_subj, use_container_width=True)
                        st.markdown("<div style='text-align:center; font-size:14px; color:#64748B; font-weight:500;'>Subject Specialization</div>", unsafe_allow_html=True)

            except ImportError:
                # Fallback
                total = max(1, progress_data['completed'] + progress_data['learning'] + progress_data['unstarted'])
                perc = int(progress_data['completed'] / total * 100)
                st.progress(progress_data['completed'] / total)
                st.markdown(f"<div style='text-align:center; font-size:32px; font-weight:700;'>{perc}% Mastery</div>", unsafe_allow_html=True)
                
                subj_stats = db.get_subject_completion_stats(u['id'])
                for s in subj_stats:
                    p = (s['completed_topics'] or 0) / max(1, s['total_topics'])
                    st.write(f"{s['subject']} ({int(p*100)}%)")
                    st.progress(p)

    st.divider()

    # 4. INSIGHTS & ACTIVITY
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💡 Learning Insights")
        
        # AI Analytical Insight Logic
        if "dash_insight" not in st.session_state or st.button("🔄 Refresh Analysis"):
            with st.spinner("Synthesizing academic report..."):
                prompt = (
                    f"Academic Profile: {u['name']}\n"
                    f"Metrics: {stats['topics_completed']} completed, {int(stats['avg_accuracy'])}% accuracy, {stats['weak_count']} active/weak topics.\n"
                    f"Task: Provide a professional, data-driven academic assessment. "
                    f"Include: \n"
                    f"1. Performance Observation (based on accuracy).\n"
                    f"2. Weak Topic Recommendations (for the {stats['weak_count']} active areas).\n"
                    f"3. Strategic Study Suggestion (next steps).\n"
                    f"Tone: Analytical, clinical, and academic. No motivational or neural-pathway metaphors."
                )
                try:
                    st.session_state.dash_insight = ask_gemini(prompt)
                except:
                    st.session_state.dash_insight = "Academic analysis currently unavailable. Continue your curriculum to generate more telemetry data."
        
        st.markdown(f"""
            <div style="background: {t['hover']}; padding: 24px; border-radius: 12px; border-left: 5px solid {t['accent']}; margin-bottom: 24px;">
                <div style="font-size: 16px; line-height: 1.6; color: {t['text']}; font-family: 'Inter', sans-serif;">
                    {st.session_state.dash_insight}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.subheader("Recent Activity")
        if stats['recently_studied']:
            for recent in stats['recently_studied']:
                with st.container(border=True):
                    c_a, c_b = st.columns([3, 1])
                    with c_a:
                        status_label = "✅ Done" if recent.get('completed') else "📖 Studying"
                        st.write(f"**{recent['name']}** — {status_label}")
                        st.caption(f"Last accessed: {recent['last_accessed']}")
                    with c_b:
                        if st.button("Resume", key=f"dash_{recent['topic_id']}", use_container_width=True):
                            st.session_state["selected_topic"] = recent['topic_id']
                            st.session_state["current_page"] = "Study"
                            st.rerun()
        else:
            st.info("No recent activity. Start studying to see insights!")

    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)
