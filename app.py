import streamlit as st
import os
from dotenv import load_dotenv
from memory.student_intelligence import StudentIntelligenceSystem

# 1. INITIALIZATION & CONFIG
load_dotenv()

# MUST be the first Streamlit command
st.set_page_config(
    page_title="cogniX",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. SESSION STATE DEFAULTS
state_defaults = {
    "theme": "light",
    "accent": "blue",
    "user": None,
    "auth_selection": None,
    "current_page": "Dashboard",
    "forgot_password_mode": False,
    "otp_sent": False,
    "email_verified": False,
    "signup_otp": None,
    "signup_email": None,
    "reset_user": None,
    "active_topic": None,
    "active_subject": None,
    "db_config": {"dbname": "cognix_db", "user": "postgres", "password": "", "host": "localhost", "use_sqlite": True},
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 3. IMPORTS
from ui.styles import build_css, THEMES, ACCENTS
from ui.components import render_logo, render_topbar
from ui.auth import render_login_signup
import upload.db as db

# ── INITIALIZE DATABASE ──────────────────────────────────────────────
db.init_db()


# ── SIS CACHE ────────────────────────────────────────────────────────
@st.cache_resource
def get_sis(db_config):
    return StudentIntelligenceSystem(db_config)

# 4. GLOBAL STYLING
def apply_global_styles():
    st.markdown(build_css(st.session_state.theme, st.session_state.accent), unsafe_allow_html=True)

apply_global_styles()

# 5. AUTHENTICATION GUARD
if st.session_state.user is None:
    render_login_signup()
    st.stop()

# 6. MAIN APPLICATION UI
sis = get_sis(st.session_state.db_config)

with st.sidebar:
    render_logo(size="medium", align="flex-start")
    
    # User Profile Block (Sleek SaaS Layout)
        st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-top:16px; margin-bottom:12px; padding:12px; background:{THEMES[st.session_state.theme]['hover']}; border-radius:12px;">
        <div style="background:{THEMES[st.session_state.theme]['accent']}; color:white; width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:16px !important; flex-shrink:0;">
            {initial}
        </div>
        <div style="overflow:hidden;">
            <div style="font-weight:700; font-size:14px !important; color:{THEMES[st.session_state.theme]['text']} !important; white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">{u['name']}</div>
            <div style="font-size:12px !important; color:{THEMES[st.session_state.theme]['muted']} !important; white-space:nowrap; text-overflow:ellipsis; overflow:hidden;">{user_email}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("👤 View Profile", use_container_width=True):
        st.session_state.current_page = "Profile"
        st.rerun()
    
    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Navigation
    st.markdown(f"<div style='font-size:14px; font-weight:600; color:{THEMES[st.session_state.theme]['muted']}; margin-bottom:12px;'>NAVIGATION</div>", unsafe_allow_html=True)
    
    nav_options = ["Dashboard", "Profile", "Subjects", "Study", "Practice", "Chat"]
    if st.session_state.user['role'] in ['admin', 'super_admin']:
        nav_options.append("Upload")
    if st.session_state.user['role'] == 'super_admin':
        nav_options.append("Admin Requests")
        
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
        
    def on_nav_change():
        st.session_state.current_page = st.session_state.nav_radio
        
    idx = nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0
    selected_page = st.radio("Menu", options=nav_options, index=idx, key="nav_radio", label_visibility="collapsed", on_change=on_nav_change)
    
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
    
    # Settings
    with st.expander("⚙️ Account Settings"):
        st.session_state.theme = st.selectbox("Theme", options=list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme))
        st.session_state.accent = st.selectbox("Accent", options=list(ACCENTS.keys()), index=list(ACCENTS.keys()).index(st.session_state.accent))
        if st.button("Logout", use_container_width=True, type="primary"):
            st.session_state.user = None
            st.rerun()

# 7. ROUTING
page = st.session_state.current_page

try:
    if page == "Dashboard":
        from ui.dashboard import render_dashboard
        render_dashboard()
    elif page == "Profile":
        from ui.profile_page import render_profile_page
        render_profile_page()
    elif page == "Subjects":

        from ui.subjects_page import render_subjects_page
        render_subjects_page(sis)
    elif page == "Study":
        from ui.study_page import render_study_page
        render_study_page()
    elif page == "Practice":
        from ui.practice_page import render_practice_page
        render_practice_page()
    elif page == "Chat":
        from ui.chat import render_chat
        render_chat()
    elif page == "Upload":
        from upload.upload_page import render_upload_page
        render_upload_page()
    elif page == "Admin Requests":
        from ui.admin_requests_page import render_admin_requests_page
        render_admin_requests_page()
except Exception as e:
    st.error(f"Module Loading Error: {e}")
    st.info("Please try refreshing the page or contact the super admin.")
