import streamlit as st
import os
from dotenv import load_dotenv
from memory.student_intelligence import StudentIntelligenceSystem
import bcrypt

# --- BACKEND AUTO-START (SAFE) ---
def start_backend_if_needed():
    if st.session_state.get("backend_started", False):
        return
    
    import requests
    import subprocess
    import time
    import sys
    
    # 1. Health Check
    url = "http://127.0.0.1:8000/health"
    try:
        res = requests.get(url, timeout=1)
        if res.status_code == 200:
            st.session_state.backend_started = True
            return
    except:
        pass

    # 2. Detect & Start Backend
    print("[SYSTEM] Initializing Cognitive Engine...")
    
    # Platform-agnostic Python executable detection
    py_exe = sys.executable
    
    # Local Windows venv detection (for local dev stability)
    for venv_path in ["jarvis_env_312/Scripts/python.exe", "jarvis_env/Scripts/python.exe"]:
        abs_venv = os.path.abspath(venv_path)
        if os.path.exists(abs_venv):
            py_exe = abs_venv
            break
    
    try:
        # Start uvicorn with logs suppressed
        # Use 127.0.0.1 for local/cloud internal loopback stability
        cmd = [py_exe, "-m", "uvicorn", "api.server:app", "--host", "127.0.0.1", "--port", "8000"]
        
        # On some Cloud environments, we might need to specify the full path to uvicorn
        # if -m uvicorn fails. But usually -m works if installed.
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Give it a bit more time to ignite
        time.sleep(3) 
        st.session_state.backend_started = True
        print(f"[SYSTEM] Engine started via {py_exe}")
    except Exception as e:
        print(f"[ERROR] Engine failed to ignite: {e}")

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
    "db_config": {"dbname": "cognix.db", "user": "postgres", "password": "", "host": "localhost", "use_sqlite": True},
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

start_backend_if_needed()

# Check current status for UI
def get_backend_status():
    import requests
    try:
        res = requests.get("http://127.0.0.1:8000/health", timeout=1)
        return res.status_code == 200
    except:
        return False

st.session_state.backend_active = get_backend_status()

# Fetch extended health info if active
if st.session_state.backend_active:
    try:
        import requests
        h_info = requests.get("http://127.0.0.1:8000/health", timeout=1).json()
        st.session_state.hw_info = h_info.get("hardware", "Unknown")
    except:
        st.session_state.hw_info = "Searching..."
else:
    st.session_state.hw_info = "Offline"

with st.sidebar:
    render_logo(size="medium", align="flex-start")
    
    # User Profile Block (Sleek SaaS Layout)
    u = st.session_state.user
    role_badge = "Admin" if u['role'] == 'super_admin' else "Student"
    user_email = u.get('email') or u.get('username', '')
    initial = u['name'][0].upper() if u['name'] else "?"
    
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

    # --- SYSTEM PULSE CARD ---
    status_color = "#10b981" if st.session_state.backend_active else "#ef4444"
    status_text = "Operational" if st.session_state.backend_active else "Offline"
    hw_icon = "🚀" if "GPU" in st.session_state.hw_info else "⚙️"
    
    st.markdown(f"""
    <div style="background: {THEMES[st.session_state.theme]['hover']}; padding: 12px; border-radius: 12px; border-left: 4px solid {status_color}; margin-bottom: 24px;">
        <div style="font-size: 10px; font-weight: 800; color: {THEMES[st.session_state.theme]['muted']}; letter-spacing: 0.1em; margin-bottom: 4px;">SYSTEM PULSE</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 13px; font-weight: 600;">Core Engine</span>
            <span style="color: {status_color}; font-size: 11px; font-weight: 700;">● {status_text}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
            <span style="font-size: 13px; font-weight: 600;">Hardware</span>
            <span style="font-size: 11px; opacity: 0.8;">{hw_icon} {st.session_state.hw_info}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.backend_active and not st.session_state.get("hide_backend_warning"):
        if st.button("🔌 Reconnect Brain", use_container_width=True):
            st.rerun()
        st.markdown("---")
    
    # Navigation
    st.markdown(f"<div style='font-size:14px; font-weight:600; color:{THEMES[st.session_state.theme]['muted']}; margin-bottom:12px;'>NAVIGATION</div>", unsafe_allow_html=True)
    
    nav_options = ["Dashboard", "Profile", "Subjects", "Study", "Practice", "Chat"]
    if st.session_state.user['role'] in ['admin', 'super_admin']:
        nav_options.append("Upload")
    if st.session_state.user['role'] == 'super_admin':
        nav_options.append("Admin Requests")
        
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
        
    idx = nav_options.index(st.session_state.current_page) if st.session_state.current_page in nav_options else 0
    selected_page = st.radio("Menu", options=nav_options, index=idx, label_visibility="collapsed")
    
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
    
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
    
    # Settings
    with st.expander("⚙️ SYSTEM SETTINGS"):
        def update_theme():
            st.session_state.theme = st.session_state.theme_selector
        def update_accent():
            st.session_state.accent = st.session_state.accent_selector
            
        st.selectbox("Theme", options=list(THEMES.keys()), 
                     index=list(THEMES.keys()).index(st.session_state.theme),
                     key="theme_selector", on_change=update_theme)
        st.selectbox("Accent", options=[k for k in ACCENTS.keys() if not k.endswith("_solid")], 
                     index=[k for k in ACCENTS.keys() if not k.endswith("_solid")].index(st.session_state.accent),
                     key="accent_selector", on_change=update_accent)

        st.divider()

        # Hard Reset (Integrated into Settings)
        with st.popover("🗑️ Hard Reset", use_container_width=True):
            st.error("⚠️ This will wipe all progress.")
            pw = st.text_input("Password to confirm", type="password", key="settings_reset_pw")
            if st.button("🔥 WIPE NOW", type="primary", use_container_width=True):
                u_data = db.get_user_by_id(st.session_state.user['id'])
                if bcrypt.checkpw(pw.encode('utf-8'), u_data['password'].encode('utf-8') if isinstance(u_data['password'], str) else u_data['password']):
                    if db.hard_reset_academic_progress(st.session_state.user['id']):
                        st.toast("🔥 Progress wiped.")
                        st.success("Success!")
                        st.rerun()
                else: st.error("Incorrect password")

        st.divider()
        
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
    import traceback
    st.error(f"⚠️ System Loading Error: {str(e)}")
    with st.expander("🔍 Diagnostic Details (Traceback)"):
        st.code(traceback.format_exc())
    st.info("Tip: Ensure you have run 'pip install -r requirements.txt' in your active environment.")
