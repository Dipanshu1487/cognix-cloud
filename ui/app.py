"""
cogniX OS — Main Application (Streamlit-native)
Uses st.tabs, st.columns, st.container, st.expander for ALL layout.
CSS is limited to styling only.
Run: streamlit run ui/app.py
"""
import streamlit as st
import requests
import pandas as pd
import re
import sqlite3
import smtplib
from email.mime.text import MIMEText
import random
import os
import bcrypt
from PIL import Image

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from core.listener import listen
import core.voice as voice
from memory.student_intelligence import StudentIntelligenceSystem
from ui.styles import build_css, THEMES, ACCENTS
from core.gemini_engine import ask_gemini
from ui.components import (
    render_topbar, render_focus_bar,
    render_topic_card, render_chat_bubble,
    render_logo
)
import upload.db as db


# ── Cache SIS ────────────────────────────────────────────────────────
@st.cache_resource
def get_sis(db_config_tuple):
    return StudentIntelligenceSystem(dict(db_config_tuple))

def _t():
    """Current theme palette."""
    return THEMES.get(st.session_state.get("theme", "light"), THEMES["light"])

def send_otp(receiver_email, otp):
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    EMAIL = os.getenv("GMAIL_USER")
    PASSWORD = os.getenv("GMAIL_PASS")

    if not EMAIL or not PASSWORD:
        raise ValueError("Email credentials not configured in .env")

    body = f"""
Hello,

Welcome to cogniX — your AI-powered academic learning system.

Please use the verification code below to complete your signup:

━━━━━━━━━━━━━━━━━━━━━━━
🔐 Verification Code: {otp}
━━━━━━━━━━━━━━━━━━━━━━━

This code is valid for a short time. Do not share it.

— Team cogniX
"""

    msg = MIMEText(body)
    msg["Subject"] = "Verify Your Email for cogniX"
    msg["From"] = f"cogniX <{EMAIL}>"
    msg["To"] = receiver_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("SMTP Error:", e)
        return False


# ── Page Config ──────────────────────────────────────────────────────
# ── Page Config (MUST BE FIRST) ───────────────────────────────────────
st.set_page_config(page_title="cogniX OS", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════
# 1. INITIALIZATION (Top of file)
# ══════════════════════════════════════════════════════════════════════
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Load other defaults
_defaults = {
    "messages":         [],
    "accent":           "blue",
    "scale":            "medium",
    "chat_style":       "comfortable",
    "voice_enabled":    True,
    "auto_send":        False,
    "selected_topic":   None,
    "selected_subject": None,
    "selected_chapter": None,
    "current_page":     "Dashboard",
    "chat_image":       None,
    "uploader_key":     0,
    "processing":       False,
    "pending_text":     None,
    "pending_img":      None,
    "user":             None, # Stores {id, name, username, role}
    "auth_selection":   None, # Stores if user clicked Admin or Student
    "db_config":        {"dbname": "cognix_db", "user": "postgres", "password": "", "host": "localhost", "use_sqlite": True},
    "signup_otp":       None,
    "signup_email":     None,
    "email_verified":   False,
    "otp_sent":         False,
    "forgot_password_mode": False,
    "reset_user":       None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

_db_tuple = tuple(sorted(st.session_state.db_config.items()))
sis = get_sis(_db_tuple)

# ── Initialize Database ──────────────────────────────────────────────
db.init_db()

# ══════════════════════════════════════════════════════════════════════
# 2. THEME ENGINE
# ══════════════════════════════════════════════════════════════════════
def apply_theme():
    """Injects the theme CSS at the start of the render cycle."""
    css = build_css(
        theme_key=st.session_state.theme, 
        accent_key=st.session_state.accent, 
        scale_key=st.session_state.scale
    )
    st.markdown(css, unsafe_allow_html=True)

# 3. APPLY IMMEDIATELY
apply_theme()


# ══════════════════════════════════════════════════════════════════════
# 3.5 AUTHENTICATION SYSTEM (Two-Step Flow)
# ══════════════════════════════════════════════════════════════════════
if st.session_state.user is None:
    # Inject Optimized High-Visibility CSS
    st.markdown("""
        <style>
        /* Refined Large Buttons */
        .stButton button {
            height: 90px !important;
            font-size: 2.2rem !important;
            border-radius: 20px !important;
            font-weight: 700 !important;
        }
        
        /* Refined Large Tabs */
        .stTabs [data-baseweb="tab"] {
            font-size: 2.2rem !important;
            height: 90px !important;
        }
        
        /* Refined Large Inputs */
        div[data-baseweb="input"] input {
            font-size: 1.5rem !important;
            padding: 16px !important;
        }
        
        /* Refined Large Labels */
        div[data-testid="stWidgetLabel"] p {
            font-size: 2rem !important;
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 3.8, 0.1])
    
    with c2:
        with st.container(border=True):
            # STEP 1: Selection Screen
            if st.session_state.auth_selection is None:
                st.markdown("<div style='padding: 40px 20px;'>", unsafe_allow_html=True)
                render_logo(size="xlarge", align="center")
                st.markdown("<h1 id='welcome-to-cognix' style='text-align: center; font-size: 4.5rem; line-height: 1.1;'>Welcome to cogniX</h1>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #64748B; margin-top: -16px; font-size: 1.8rem;'>Your AI-powered academic learning system</p>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                col_a, col_s = st.columns(2)
                with col_a:
                    if st.button("🛠️ Admin Block", use_container_width=True):
                        st.session_state.auth_selection = "admin"
                        st.rerun()
                with col_s:
                    if st.button("🎓 Student Block", use_container_width=True, type="primary"):
                        st.session_state.auth_selection = "user"
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            
            # STEP 2: Login/Signup Screen
            else:
                sel = st.session_state.auth_selection
                st.markdown(f"<h1 style='text-align: center; font-size: 3.5rem; line-height: 1.2;'>{sel.title()} Access</h1>", unsafe_allow_html=True)
                
                col_back, _ = st.columns([1.2, 2])
                with col_back:
                    if st.button("← Change Mode", use_container_width=True):
                        st.session_state.auth_selection = None
                        st.rerun()
                
                tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
                
                with tab_login:
                    l_user = st.text_input("Username", key="l_user")
                    l_pass = st.text_input("Password", type="password", key="l_pass")
                    if st.button("Login", use_container_width=True, type="primary"):
                        conn = sqlite3.connect("cognix.db")
                        conn.row_factory = sqlite3.Row
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM users WHERE username = ?", (l_user,))
                        user_row = cur.fetchone()
                        
                        valid = False
                        if user_row:
                            try:
                                if bcrypt.checkpw(l_pass.encode('utf-8'), user_row['password']):
                                    if sel == 'admin':
                                        if user_row['role'] in ['admin', 'super_admin']:
                                            valid = True
                                    else:
                                        if user_row['role'] == 'user':
                                            valid = True
                            except:
                                pass
                        
                        if valid:
                            st.session_state.user = {
                                "id": user_row['id'],
                                "name": user_row['name'],
                                "username": user_row['username'],
                                "role": user_row['role']
                            }
                            conn.close()
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
                        conn.close()

                    if st.button("Forgot Password?", type="secondary", use_container_width=True):
                        st.session_state.forgot_password_mode = True
                        st.rerun()

                if st.session_state.forgot_password_mode:
                    st.subheader("Reset Password")
                    reset_email = st.text_input("Enter Registered Email")
                    
                    if not st.session_state.otp_sent:
                        if st.button("Send Reset OTP"):
                            conn = sqlite3.connect("cognix.db")
                            cur = conn.cursor()
                            cur.execute("SELECT id FROM users WHERE email = ?", (reset_email,))
                            user_data = cur.fetchone()
                            conn.close()
                            
                            if user_data:
                                otp = str(random.randint(1000, 9999))
                                st.session_state.signup_otp = otp
                                st.session_state.reset_user = user_data[0]
                                if send_otp(reset_email, otp):
                                    st.session_state.otp_sent = True
                                    st.success("OTP sent to your email")
                                    st.rerun()
                            else:
                                st.error("Account not found")
                    else:
                        entered_otp = st.text_input("Enter OTP")
                        new_pass = st.text_input("New Password", type="password")
                        if st.button("Reset Password"):
                            if entered_otp == st.session_state.signup_otp:
                                hashed_new = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
                                db.change_password(st.session_state.reset_user, hashed_new)
                                st.success("Password reset! Please login.")
                                st.session_state.forgot_password_mode = False
                                st.session_state.otp_sent = False
                                st.rerun()
                            else:
                                st.error("Invalid OTP")
                        if st.button("Back"):
                            st.session_state.forgot_password_mode = False
                            st.rerun()
                                
                with tab_signup:
                    st.subheader("Create Account")
                    s_name = st.text_input("Full Name", key="s_name")
                    s_user = st.text_input("Username", key="s_user")
                    
                    user_valid = False
                    if s_user:
                        if len(s_user) < 4 or len(s_user) > 15:
                            st.error("❌ Username must be 4-15 characters.")
                        elif not re.match("^[a-zA-Z0-9_]*$", s_user):
                            st.error("❌ Alphanumeric and underscores only.")
                        else:
                            conn = sqlite3.connect("cognix.db", check_same_thread=False)
                            cur = conn.cursor()
                            cur.execute("SELECT id FROM users WHERE username = ?", (s_user,))
                            if cur.fetchone():
                                st.error("❌ Already taken.")
                            else:
                                st.success("✅ Available")
                                user_valid = True
                            conn.close()
                                
                    s_pass = st.text_input("Password", type="password", key="s_pass")
                    pass_valid = False
                    if s_pass:
                        l_ok, u_ok, low_ok, d_ok = len(s_pass)>=6, bool(re.search(r"[A-Z]",s_pass)), bool(re.search(r"[a-z]",s_pass)), bool(re.search(r"[0-9]",s_pass))
                        st.markdown(f"{'✅' if l_ok else '❌'} 6+ chars | {'✅' if u_ok else '❌'} Upper | {'✅' if d_ok else '❌'} Digit")
                        if l_ok and u_ok and low_ok and d_ok: pass_valid = True
                            
                    s_email = st.text_input("Email", key="s_email")
                    email_valid = False
                    if s_email:
                        if "@" in s_email and "." in s_email:
                            email_valid = True
                        else:
                            st.error("❌ Invalid email format")

                    st.divider()

                    if not st.session_state.email_verified:
                        if not st.session_state.otp_sent:
                            if st.button("Send Verification Code", disabled=not (user_valid and email_valid)):
                                st.session_state.signup_otp = str(random.randint(1000, 9999))
                                st.session_state.signup_email = s_email
                                with st.spinner("Sending OTP..."):
                                    try:
                                        success = send_otp(s_email, st.session_state.signup_otp)
                                        if success:
                                            st.session_state.otp_sent = True
                                            st.success("Verification code sent to your email")
                                            st.rerun()
                                        else:
                                            st.error("Failed to send email.")
                                    except Exception:
                                        st.error("Failed to send email. Please check your system configuration.")
                        else:
                            st.info(f"OTP sent to {st.session_state.signup_email}")
                            entered_otp = st.text_input("Enter Verification Code", key="entered_otp")
                            col_v1, col_v2 = st.columns(2)
                            with col_v1:
                                if st.button("Verify OTP", type="primary", use_container_width=True):
                                    if entered_otp == st.session_state.signup_otp:
                                        st.session_state.email_verified = True
                                        st.rerun()
                                    else:
                                        st.error("❌ Incorrect OTP")
                            with col_v2:
                                if st.button("Resend Code", use_container_width=True):
                                    st.session_state.signup_otp = str(random.randint(1000, 9999))
                                    with st.spinner("Resending OTP..."):
                                        try:
                                            success = send_otp(s_email, st.session_state.signup_otp)
                                            if success:
                                                st.success("Verification code sent to your email")
                                            else:
                                                st.error("Failed to send email. Check credentials.")
                                        except Exception as e:
                                            st.error(f"Configuration Error: {e}")
                    else:
                        st.success("✅ Email Verified")
                        if st.button("Sign Up", use_container_width=True, type="primary", disabled=not (s_name and user_valid and pass_valid and st.session_state.email_verified)):
                            hashed_pw = bcrypt.hashpw(s_pass.encode('utf-8'), bcrypt.gensalt())
                            conn = sqlite3.connect("cognix.db", check_same_thread=False)
                            cur = conn.cursor()
                            if sel == 'admin':
                                # Create an admin request instead of direct user
                                cur.execute("INSERT INTO admin_requests (name, username, email, password) VALUES (?, ?, ?, ?)", (s_name, s_user, s_email, hashed_pw))
                                msg = "✅ Request Sent! Wait for Super Admin approval."
                            else:
                                cur.execute("INSERT INTO users (name, username, email, password, role) VALUES (?, ?, ?, ?, ?)", (s_name, s_user, s_email, hashed_pw, sel))
                                msg = "✅ Created! Now Login."
                            conn.commit()
                            conn.close()
                            
                            st.session_state.signup_otp = None
                            st.session_state.email_verified = False
                            st.session_state.otp_sent = False
                            st.session_state.signup_email = None
                            
                            st.success(msg)
    st.stop()



# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Branding ──
    render_logo(size="medium", align="flex-start")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── User Profile Segment ──────────────────────────────────────────
    with st.container():
        st.markdown(f"<div style='font-size:14px; font-weight:600; color:{_t()['text']}; margin-bottom:4px;'>{st.session_state.user['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:12px; color:{_t()['muted']}; margin-bottom:12px;'>@{st.session_state.user['username']}</div>", unsafe_allow_html=True)
        if st.button("View Profile", use_container_width=True):
            st.session_state.current_page = "Profile"
            st.rerun()
    
    st.divider()

    if st.session_state.user['role'] == "admin":
        nav_options = ["Dashboard", "Subjects", "Study", "Practice", "Upload", "Chat", "Settings"]
    else:
        nav_options = ["Dashboard", "Subjects", "Study", "Practice", "Chat", "Settings"]
    
    # Super Admin Extras
    if st.session_state.user['role'] == 'super_admin':
        nav_options.insert(2, "Admin Requests")
    
    # Sync radio index with current_page state
    if st.session_state.current_page not in nav_options and st.session_state.current_page != "Profile":
        st.session_state.current_page = "Dashboard"
        
    try:
        page_idx = nav_options.index(st.session_state.current_page)
    except ValueError:
        # If we are on Profile, we don't have a radio index to select
        page_idx = 0 
    
    def on_nav_change():
        st.session_state.current_page = st.session_state.nav_radio

    st.radio(
        "Navigation",
        nav_options,
        index=page_idx,
        key="nav_radio",
        on_change=on_nav_change
    )

    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state.user = None
        st.rerun()

    st.divider()

    with st.expander("⚙ Quick Settings"):
        # 4. THEME SELECTOR
        current_theme = st.session_state.theme
        selected_theme = st.selectbox(
            "Theme Mode", 
            ["light", "dark", "grey"], 
            index=["light", "dark", "grey"].index(current_theme)
        )
        
        # If changed: update and rerun
        if selected_theme != current_theme:
            st.session_state.theme = selected_theme
            st.rerun()

        st.selectbox("Accent", ["blue", "purple", "green"], 
                     index=["blue", "purple", "green"].index(st.session_state.accent),
                     key="sb_accent", on_change=lambda: st.session_state.update({"accent": st.session_state.sb_accent}))
        st.selectbox("Scale", ["small", "medium", "large"], 
                     index=["small", "medium", "large"].index(st.session_state.scale),
                     key="sb_scale", on_change=lambda: st.session_state.update({"scale": st.session_state.sb_scale}))
        st.divider()
        st.toggle("Voice Output", value=st.session_state.voice_enabled, key="sb_voice", 
                  on_change=lambda: st.session_state.update({"voice_enabled": st.session_state.sb_voice}))
        st.toggle("Auto Send Voice", value=st.session_state.auto_send, key="sb_auto", 
                  on_change=lambda: st.session_state.update({"auto_send": st.session_state.sb_auto}))

    with st.expander("🔌 Database"):
        db_cfg = st.session_state.db_config
        use_sqlite = st.toggle("Use SQLite (Local)", value=db_cfg.get("use_sqlite", True))
        db_host = st.text_input("Host", value=db_cfg.get("host", "localhost"), disabled=use_sqlite)
        db_name = st.text_input("Database", value=db_cfg.get("dbname", "cognix_db"), disabled=use_sqlite)
        db_user = st.text_input("User", value=db_cfg.get("user", "postgres"), disabled=use_sqlite)
        db_pass = st.text_input("Password", value=db_cfg.get("password", ""), type="password", disabled=use_sqlite)
        if st.button("Update Connection", use_container_width=True):
            st.session_state.db_config = {
                "host": db_host, "dbname": db_name,
                "user": db_user, "password": db_pass,
                "use_sqlite": use_sqlite,
            }
            st.rerun()

    if st.checkbox("🐞 Debug"):
        st.json(dict(st.session_state), expanded=False)


# ══════════════════════════════════════════════════════════════════════
# ACTIONS
# ══════════════════════════════════════════════════════════════════════
def process_query(query_text, image_data=None):
    full_query = query_text or ""
    if st.session_state.selected_topic:
        topic_name = sis.get_topic_name(st.session_state.selected_topic)
        full_query = f"[Topic: {topic_name}] {full_query}"

    # Build explicit Chat Memory
    chat_memory = "--- Chat History ---\n"
    if len(st.session_state.messages) > 0:
        for msg in st.session_state.messages[-5:]:
            role = "User" if msg["role"] == "You" else "cogniX"
            chat_memory += f"{role}: {msg['content']}\n"
    chat_memory += "--------------------\n\n"

    st.session_state.messages.append({"role": "You", "content": query_text or "Image Uploaded", "image": image_data})


    try:
        if image_data:
            ai_prompt = f"{chat_memory}You are cogniX, an AI-powered academic assistant. User uploaded an image.\nUser query: {query_text or 'Explain this image'}\nInstructions: Analyze the image step-by-step and answer accurately."
            cognix_resp = ask_gemini(ai_prompt, image_data)
        else:
            q_lower = full_query.lower()
            # Route system commands to backend, route conversations to Gemini for memory
            if any(w in q_lower for w in ["open ", "play ", "close ", "volume"]):
                resp = requests.post("http://127.0.0.1:8000/chat", json={"query": full_query}, timeout=30)
                cognix_resp = resp.json().get("response", "No response.") if resp.status_code == 200 else f"Error {resp.status_code}"
            else:
                ai_prompt = f"{chat_memory}You are cogniX, an intelligent academic AI assistant. Answer the following user query accurately based on the context above.\nCurrent Query: {full_query}"
                cognix_resp = ask_gemini(ai_prompt, None)
    except Exception as e:
        cognix_resp = f"Error connecting to AI engine: {e}"

    tracking = {"topic_name": "Unknown", "proficiency": "unknown", "trend": "stable", "logged": False}
    try:
        user_id = st.session_state.user['id']
        res = sis.process_chat_interaction(user_id=user_id, query=query_text)
        if res:
            status = sis.get_topic_status(user_id, res["subtopic_id"])
            tracking.update({
                "topic_name": res["topic_name"],
                "proficiency": status["proficiency"],
                "trend": status["trend"],
                "logged": True,
            })
    except Exception:
        pass

    st.session_state.messages.append({"role": "cogniX", "content": cognix_resp, "tracking": tracking})

    if st.session_state.voice_enabled:
        voice.stop_speaking()
        voice.speak_async(cognix_resp)



def handle_mic():
    txt = listen()
    if txt:
        st.session_state.chat_input_box = txt
        submit_chat()

def submit_chat():
    text = st.session_state.get("chat_input_box", "")
    img = st.session_state.get("chat_image")
    
    if not text and not img:
        st.warning("Please enter text or upload an image.")
        return
        
    # Store for processing
    st.session_state.pending_text = text
    st.session_state.pending_img = img
    
    # Clear inputs properly
    st.session_state.chat_input_box = ""
    st.session_state.chat_image = None
    st.session_state.uploader_key += 1
    
    st.session_state.processing = True

# ══════════════════════════════════════════════════════════════════════
# VIEW: CHAT
# ══════════════════════════════════════════════════════════════════════
def render_chat():
    # Fix Logo Cut / Top Padding
    st.markdown("<div style='padding-top:20px'></div>", unsafe_allow_html=True)

    st.title("💬 Chat")
    st.write("")

    render_focus_bar(sis, context="chat")

    # Messages Area
    chat_container = st.container(height=500, border=False)
    with chat_container:
        if not st.session_state.messages:
            st.info("Ask anything or upload a problem to get started.")
        else:
            for msg in st.session_state.messages:
                render_chat_bubble(msg["role"], msg["content"], msg.get("tracking"), msg.get("image"))
            
    st.write("") # Smooth spacing

    # 🛑 Processing State & Stop Button
    if st.session_state.get("processing", False):
        st.divider()
        stop_col, _ = st.columns([1, 4])
        with stop_col:
            if st.button("🛑 Stop cogniX", key="stop_jarvis_btn", use_container_width=True):
                st.session_state.processing = False
                st.session_state.pending_text = None
                st.session_state.pending_img = None
                st.rerun()
            
        with st.spinner("cogniX is thinking..."):
            process_query(st.session_state.pending_text, st.session_state.pending_img)
            st.session_state.processing = False
            st.session_state.pending_text = None
            st.session_state.pending_img = None
            st.rerun()
        st.divider()

    # Image Preview area (above input)
    if st.session_state.chat_image:
        with st.container(border=True):
            col_pre, col_del = st.columns([1, 4])
            with col_pre:
                st.image(st.session_state.chat_image, width=150)
            with col_del:
                st.caption("Image ready to send")
                if st.button("❌ Remove Image"):
                    st.session_state.chat_image = None
                    st.rerun()

    # Combined Input Bar Container (Panel)
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1, 2, 7, 1])
        
        with c1:
            if voice.is_speaking:
                if st.button("🔴", help="Stop cogniX Voice", use_container_width=True):
                    voice.stop_speaking()
                    st.rerun()
            else:
                if st.button("🎤", help="Voice Input", use_container_width=True):
                     handle_mic()

        with c2:
            # File uploader with enough space to avoid overlap
            uploaded_file = st.file_uploader("📎", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key=f"uploader_{st.session_state.uploader_key}")
            if uploaded_file and st.session_state.chat_image != uploaded_file.getvalue():
                st.session_state.chat_image = uploaded_file.getvalue()
                st.rerun()

        with c3:
            st.text_input("Type your message...", label_visibility="collapsed", key="chat_input_box", on_change=submit_chat, disabled=st.session_state.get("processing", False))

        with c4:
            if st.button("➤", type="primary", use_container_width=True, help="Send Message", disabled=st.session_state.get("processing", False)):
                submit_chat()

# ══════════════════════════════════════════════════════════════════════
# VIEW: SETTINGS
# ══════════════════════════════════════════════════════════════════════
def render_settings():
    st.title("⚙️ Settings")
    st.caption("Customize your cogniX experience.")
    st.write("")

    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Appearance")
        with st.container(border=True):
            new_theme = st.selectbox("UI Theme", ["dark", "grey", "light"],
                                     index=["dark", "grey", "light"].index(st.session_state.theme),
                                     key="settings_theme")
            new_accent = st.selectbox("Accent Color", ["blue", "purple", "green"],
                                      index=["blue", "purple", "green"].index(st.session_state.accent),
                                      key="settings_accent")
            new_scale = st.selectbox("Interface Scale", ["small", "medium", "large"],
                                     index=["small", "medium", "large"].index(st.session_state.scale),
                                     key="settings_scale")

            if st.button("Apply Changes", use_container_width=True, type="primary"):
                st.session_state.theme = new_theme
                st.session_state.accent = new_accent
                st.session_state.scale = new_scale
                st.rerun()

    with col_r:
        st.subheader("Voice & Interaction")
        with st.container(border=True):
            st.toggle("Voice Output", key="settings_voice", value=st.session_state.voice_enabled)
            st.toggle("Auto Send Voice Input", key="settings_auto", value=st.session_state.auto_send)

            if st.button("Save Voice Settings", use_container_width=True):
                st.session_state.voice_enabled = st.session_state.settings_voice
                st.session_state.auto_send = st.session_state.settings_auto
                st.rerun()

        st.write("")
        st.subheader("System Info")
        with st.container(border=True):
            info_l, info_r = st.columns(2)
            info_l.caption("Version")
            info_r.write("**3.2.0**")
            info_l2, info_r2 = st.columns(2)
            info_l2.caption("Database")
            info_r2.write(f"**{'SQLite' if st.session_state.db_config.get('use_sqlite') else 'PostgreSQL'}**")
            info_l3, info_r3 = st.columns(2)
            info_l3.caption("Theme")
            info_r3.write(f"**{st.session_state.theme.title()}**")

    st.divider()

    # 4. HARD RESET SECTION
    st.subheader("⚠️ Dangerous Zone")
    with st.container(border=True):
        st.markdown("<p style='color:#EF4444; font-size:18px; font-weight:600;'>Hard Reset Academic Progress</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; margin-bottom:24px;'>This will permanently delete all your topics studied, accuracy scores, and session history. This action cannot be undone.</p>", unsafe_allow_html=True)
        
        with st.popover("🔥 Reset Everything", use_container_width=True):
            st.markdown("### Secure Reset")
            st.write("To proceed, please verify your account password.")
            
            reset_pw = st.text_input("Enter Account Password", type="password", key="reset_auth_pw")
            
            # Double Confirmation Checkbox
            st.warning("Final Warning: This will wipe ALL your academic data.")
            confirm_check = st.checkbox("I understand that this action is permanent and irreversible.")
            
            if st.button("🔴 CONFIRM HARD RESET", use_container_width=True, type="primary"):
                # 1. Verify Password
                u = st.session_state.user
                conn = sqlite3.connect("cognix.db")
                cur = conn.cursor()
                cur.execute("SELECT password FROM users WHERE id = ?", (u['id'],))
                actual_pw = cur.fetchone()[0]
                conn.close()
                
                if reset_pw != actual_pw:
                    st.error("Incorrect password. Reset aborted.")
                elif not confirm_check:
                    st.warning("Please check the confirmation box to proceed.")
                else:
                    # 2. Execute Reset
                    if db.hard_reset_academic_progress(u['id']):
                        st.session_state.reset_success = True
                        st.toast("Progress Wiped", icon="🔥")
                        # Clear any relevant session state
                        if "selected_topic" in st.session_state:
                            del st.session_state.selected_topic
                        st.rerun()
                    else:
                        st.error("Reset failed due to a system error.")

# ══════════════════════════════════════════════════════════════════════
# VIEW: PROFILE
# ══════════════════════════════════════════════════════════════════════
def render_profile():
    st.title("👤 My Profile")
    st.caption("Manage your account details, achievements, and security.")
    
    u = st.session_state.user
    
    # Refresh full profile from DB to get the latest photo, email, etc.
    profile_data = db.get_user_profile(u['id'])
    
    # If for some reason DB fetch fails, fallback to session_state
    if profile_data:
        email = profile_data.get('email') or 'Not provided'
        profile_photo = profile_data.get('profile_photo')
        join_date = profile_data.get('join_date') or 'Unknown'
        name = profile_data.get('name') or u.get('name', 'Unknown')
        
        # Keep session_state synced with DB
        st.session_state.user['name'] = name
    else:
        email = "Not provided"
        profile_photo = None
        join_date = "Unknown"
        name = u.get('name', 'Unknown')

    # 1. PROFILE HEADER (Photo & Core Info)
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if profile_photo and os.path.exists(profile_photo):
                st.image(profile_photo, use_container_width=True)
            else:
                st.markdown("<h1 style='text-align: center; font-size: 80px; margin: 0;'>👤</h1>", unsafe_allow_html=True)
            
            # Photo Upload & Management
            uploaded_file = st.file_uploader("Change Photo", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed", key="profile_pic_uploader")
            
            # Action Buttons
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if uploaded_file is not None:
                    if st.button("💾 Save & Crop", use_container_width=True, type="primary"):
                        save_dir = os.path.abspath("uploads/profiles")
                        os.makedirs(save_dir, exist_ok=True)
                        file_ext = os.path.splitext(uploaded_file.name)[1]
                        file_name = f"user_{u.get('id', '0')}{file_ext}"
                        file_path = os.path.join(save_dir, file_name)
                        
                        # Open and Crop to Square
                        img = Image.open(uploaded_file)
                        width, height = img.size
                        size = min(width, height)
                        left = (width - size) / 2
                        top = (height - size) / 2
                        right = (width + size) / 2
                        bottom = (height + size) / 2
                        img = img.crop((left, top, right, bottom))
                        
                        # Save the cropped image
                        img.save(file_path)
                        
                        db.update_profile_photo(u.get('id'), file_path)
                        st.success("Photo updated!")
                        st.rerun()
            
            with btn_col2:
                if profile_photo:
                    if st.button("🗑️ Remove", use_container_width=True, help="Remove current photo"):
                        db.remove_profile_photo(u.get('id'))
                        # Optionally delete file from disk too
                        if os.path.exists(profile_photo):
                            try: os.remove(profile_photo)
                            except: pass
                        st.success("Photo removed!")
                        st.rerun()

        with col2:
            st.subheader(name)
            st.write(f"**Username:** @{u.get('username', 'unknown')}")
            st.write(f"**Email:** {email}")
            st.write(f"**Role:** {u.get('role', 'user').title()}")
            st.caption(f"Joined: {join_date}")
            
        with col3:
            # Edit Profile details
            with st.popover("✏️ Edit Profile"):
                st.write("Update Information")
                new_name = st.text_input("Name", value=name)
                new_email = st.text_input("Email", value=email)
                if st.button("Save Changes", type="primary", use_container_width=True):
                    db.update_profile(u['id'], new_name, new_email)
                    st.success("Profile updated!")
                    st.rerun()

    st.divider()
    
    # 2. ACHIEVEMENTS & CREDENTIALS
    st.subheader("🏆 Credentials & Achievements")
    achievements = db.get_user_achievements(u['id'])
    
    if achievements:
        cols = st.columns(min(len(achievements), 4)) # Max 4 cols
        for i, ach in enumerate(achievements):
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"<h1 style='text-align:center;'>{ach['icon']}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center;'><b>{ach['title']}</b></div>", unsafe_allow_html=True)
                    st.caption(f"<div style='text-align:center;'>{ach['desc']}</div>", unsafe_allow_html=True)
    else:
        st.info("Start studying and practicing topics to earn credentials and badges!")
        
    st.write("")

    # 3. SECURITY & ACTIVITY
    col_pw, col_hist = st.columns(2)
    
    with col_pw:
        st.subheader("Security")
        with st.container(border=True):
            curr_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            if st.button("Change Password", use_container_width=True, type="primary"):
                # Verify current password
                conn = sqlite3.connect("cognix.db")
                cur = conn.cursor()
                cur.execute("SELECT password FROM users WHERE id = ?", (u['id'],))
                actual_pw = cur.fetchone()[0]
                conn.close()
                
                if curr_pw != actual_pw:
                    st.error("Incorrect current password")
                elif new_pw != confirm_pw:
                    st.error("New passwords do not match")
                elif not new_pw:
                    st.error("Password cannot be empty")
                else:
                    if db.change_password(u['id'], new_pw):
                        st.success("Password updated successfully!")
                    
        st.write("")
        st.subheader("Session")
        with st.container(border=True):
            st.write("Ready to leave?")
            if st.button("🚪 Sign Out of cogniX", use_container_width=True, type="secondary"):
                st.session_state.user = None
                st.rerun()
                    
    with col_hist:
        st.subheader("Recent Activity")
        with st.container(border=True):
            stats = db.get_dashboard_stats(u['id'])
            if stats['recently_studied']:
                for item in stats['recently_studied'][:4]:
                    st.write(f"📖 **{item['name']}**")
                    st.caption(f"Last accessed: {item['last_accessed']}")
                    st.divider()
            else:
                st.info("No recent activity found.")


# ══════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════
if st.session_state.get("reset_success"):
    st.success("✅ **System Reset Complete**: All academic progress has been wiped. You can now start fresh.")
    st.session_state.reset_success = False

render_topbar()

page = st.session_state.current_page

if page == "Dashboard":
    from ui.dashboard import render_dashboard
    render_dashboard()
elif page == "Chat":
    render_chat()
elif page == "Subjects":
    from ui.subjects_page import render_subjects_page
    render_subjects_page(sis)
elif page == "Admin Requests":
    if st.session_state.user['role'] == 'super_admin':
        from ui.admin_requests_page import render_admin_requests_page
        render_admin_requests_page()
    else:
        st.error("Access Denied.")
        st.session_state.current_page = "Dashboard"
        st.rerun()
elif page == "Study":
    from ui.study_page import render_study_page
    render_study_page()
elif page == "Practice":
    from ui.practice_page import render_practice_page
    render_practice_page()
elif page == "Upload":
    if st.session_state.user['role'] in ['admin', 'super_admin']:
        from upload.upload_page import render_upload_page
        render_upload_page()
    else:
        st.error("Access Denied.")
        st.session_state.current_page = "Dashboard"
        st.rerun()

elif page == "Profile":
    render_profile()
elif page == "Settings":
    render_settings()
else:
    st.warning(f"[{page} Module Offline]")
