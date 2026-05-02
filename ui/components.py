"""
JARVIS OS — Reusable UI Components (Streamlit-native)
Clean SaaS-level components following strict typography and spacing.
"""
import streamlit as st
import os
import base64
from ui.styles import THEMES, ACCENTS


def _t():
    """Current theme palette."""
    return THEMES.get(st.session_state.get("theme", "light"), THEMES["light"])


def _a():
    """Current accent color."""
    return ACCENTS.get(st.session_state.get("accent", "blue"), ACCENTS["blue"])


def render_logo(size="small", align="flex-start"):
    """
    Renders the cogniX logo with SaaS-standard typography.
    """
    logo_path = "assets/logo.png"
    
    # SaaS scale (Enlarged for Massive UI)
    if size == "small":
        img_width = 36
        font_size = "1.6rem"
        spacing = "10px"
    elif size == "medium":
        img_width = 48
        font_size = "2rem"
        spacing = "12px"
    elif size == "large":
        img_width = 80
        font_size = "3rem"
        spacing = "16px"
    elif size == "xlarge":
        img_width = 130
        font_size = "4.5rem"
        spacing = "22px"
    else: # giant
        img_width = 180
        font_size = "7rem"
        spacing = "35px"

    # Horizontal layout
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; justify-content: {align}; gap: {spacing}; margin-bottom: 2px;'>
            <img src="data:image/png;base64,{_get_logo_base64(logo_path)}" width="{img_width}px" style="object-fit: contain;">
            <div style='font-family: "Inter", sans-serif; line-height: 1;'>
                <span style='font-size: {font_size}; font-weight: 400; color: #94a3b8; letter-spacing: -0.02em;'>cogni</span>
                <span style='font-size: {font_size}; font-weight: 700; color: #3b82f6; margin-left: -1px; letter-spacing: -0.02em;'>X</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def _get_logo_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOP BAR — Single Line SaaS Header
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_topbar():
    t = _t()
    
    # Container for the top bar to keep it tight
    with st.container():
        left, right = st.columns([3, 1])
        with left:
            render_logo(size="small", align="flex-start")
        with right:
            st.markdown(
                f"<div style='text-align:right; color:{t['muted']}; font-size:12px; font-weight:500; padding-top:4px;'>"
                f"<span style='color:{t['success']}; margin-right:4px;'>●</span> System Online</div>",
                unsafe_allow_html=True,
            )
    st.markdown("<div style='margin-bottom: 12px; border-bottom: 1px solid "+t['border']+";'></div>", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FOCUS BAR — Study Context
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_focus_bar(sis, context="subjects"):
    t = _t()
    
    if not st.session_state.get("selected_topic"):
        return

    topic_name = sis.get_topic_name(st.session_state.selected_topic)
    subj = st.session_state.get("selected_subject") or "—"
    chap = st.session_state.get("selected_chapter") or "—"

    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"<span style='font-size:12px; color:{t['muted']}; text-transform:uppercase; letter-spacing:0.05em;'>Current Focus</span>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:15px; font-weight:500;'>{subj} <span style='color:{t['muted']};'>›</span> {chap} <span style='color:{t['muted']};'>›</span> {topic_name}</div>", unsafe_allow_html=True)
        with c2:
            if context == "subjects":
                st.button("💬 Chat", key="focus_go_chat", use_container_width=True)
            else:
                st.button("📚 Topics", key="focus_go_subj", use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOPIC CARD — SaaS Grid Item
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_topic_card(topic_name, accuracy, trend, status, topic_id, chapter, subject):
    is_current = (st.session_state.get("selected_topic") == topic_id)
    is_done = (status.lower() == "completed")
    t = _t()

    with st.container(border=True):
        col_badge, col_empty = st.columns([1, 1])
        with col_badge:
            if is_current:
                st.markdown(f"<div style='background:{t['active_bg']}; color:{t['accent']}; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; display:inline-block; margin-bottom:8px;'>ACTIVE</div>", unsafe_allow_html=True)
            elif is_done:
                st.markdown(f"<div style='background:#DCFCE7; color:#166534; font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; display:inline-block; margin-bottom:8px;'>DONE ✅</div>", unsafe_allow_html=True)
        
        st.markdown(f"<div style='font-size:18px; font-weight:600; margin-bottom:4px;'>{topic_name}</div>", unsafe_allow_html=True)

        # Simple accuracy label
        acc_color = t['success'] if accuracy > 0.75 else t['warning'] if accuracy > 0.4 else t['error']
        st.markdown(f"<div style='font-size:13px; color:{t['muted']}; margin-bottom:12px;'>Accuracy: <span style='color:{acc_color}; font-weight:600;'>{int(accuracy * 100)}%</span></div>", unsafe_allow_html=True)

        # Compact Metric
        st.progress(min(accuracy, 1.0))
        
        st.markdown(f"<div style='font-size:12px; color:{t['muted']}; margin-top:8px;'>{status.title()} · {trend.title()}</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        
        btn_label = "Review Topic" if is_done else "Study Now"
        btn_type = "primary" if (is_current or is_done) else "secondary"
        
        if st.button(btn_label, key=f"comp_study_{topic_id}", use_container_width=True, type=btn_type):
            # Mark as studied in DB
            import upload.db as db
            user_id = st.session_state.user['id']
            db.mark_topic_studied(user_id, topic_id)
            
            st.session_state.selected_topic = topic_id
            st.session_state.selected_subject = subject
            st.session_state.selected_chapter = chapter
            st.session_state.current_page = "Study"
            st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHAT BUBBLE — Clean Threading
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_chat_bubble(role, content, tracking=None, image=None):
    t = _t()
    
    if role == "You":
        with st.chat_message("user"):
            if image:
                st.image(image)
            st.markdown(content)
    else:
        with st.chat_message("assistant"):
            if image:
                st.image(image)
            st.markdown(content)
            if tracking and tracking.get("logged"):
                st.markdown(
                    f"<div style='font-size:12px; color:{t['muted']}; margin-top:8px; border-left:2px solid {t['accent']}; padding-left:8px;'>"
                    f"📌 <b>{tracking['topic_name']}</b> · {tracking['proficiency'].title()}</div>",
                    unsafe_allow_html=True
                )
