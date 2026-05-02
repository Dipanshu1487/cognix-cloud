import streamlit as st
import upload.db as db
from ui.styles import THEMES
import random
import os
import smtplib
from email.mime.text import MIMEText
import bcrypt

def send_otp(receiver_email, otp):
    EMAIL = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
    PASSWORD = st.secrets.get("GMAIL_PASS") or os.getenv("GMAIL_PASS")
    if not EMAIL or not PASSWORD: return False
    msg = MIMEText(f"Your verification code is: {otp}")
    msg['Subject'] = "cogniX Verification"
    msg['From'] = EMAIL
    msg['To'] = receiver_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        return True
    except: return False

def render_profile_page():
    u = st.session_state.user
    t = THEMES.get(st.session_state.theme, THEMES["light"])
    
    st.header("👤 Profile Management")
    
    if 'prof_otp_sent' not in st.session_state: st.session_state.prof_otp_sent = False
    if 'prof_verified' not in st.session_state: st.session_state.prof_verified = False

    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            initial = u['name'][0].upper() if u['name'] else "?"
            st.markdown(f"<div style='background:{t['accent']}; color:white; width:120px; height:120px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:48px; font-weight:800;'>{initial}</div>", unsafe_allow_html=True)
        
        with c2:
            st.subheader("Edit Account Info")
            new_name = st.text_input("Name", value=u['name'], key="prof_name_input")
            new_email = st.text_input("Email", value=u.get('email', ''), key="prof_email_input")
            
            email_changed = (new_email != u.get('email', ''))
            
            if email_changed and not st.session_state.prof_verified:
                # Email changed - Must verify
                if not st.session_state.prof_otp_sent:
                    if st.button("Send OTP to Verify Email", type="primary", use_container_width=True):
                        otp = str(random.randint(1000, 9999))
                        st.session_state.prof_otp = otp
                        if send_otp(new_email, otp):
                            st.session_state.prof_otp_sent = True
                            st.success(f"OTP sent to {new_email}")
                            st.rerun()
                        else: st.error("Failed to send OTP.")
                else:
                    st.info(f"OTP sent to {new_email}")
                    entered_otp = st.text_input("Enter 4-Digit OTP", key="prof_otp_val")
                    if st.button("Verify OTP", type="primary", use_container_width=True):
                        if entered_otp == st.session_state.prof_otp:
                            st.session_state.prof_verified = True
                            st.success("Email Verified! Now you can save.")
                            st.rerun()
                        else: st.error("Incorrect OTP.")
                    if st.button("Resend OTP"):
                        st.session_state.prof_otp_sent = False
                        st.rerun()
            else:
                # No email change or already verified
                if st.button("Save Changes", type="primary", use_container_width=True):
                    try:
                        db.update_profile(u['id'], new_name, new_email)
                        st.session_state.user = db.get_user_by_id(u['id'])
                        st.session_state.prof_verified = False
                        st.session_state.prof_otp_sent = False
                        st.success("Profile Updated Successfully!")
                        st.rerun()
                    except Exception as e: st.error(f"Update failed: {e}")

    st.write("")
    with st.expander("🔐 Change Password"):
        p1 = st.text_input("New Password", type="password", key="prof_pw1")
        p2 = st.text_input("Confirm Password", type="password", key="prof_pw2")
        if st.button("Update Password", use_container_width=True):
            if p1 == p2 and len(p1) >= 6:
                hashed = bcrypt.hashpw(p1.encode('utf-8'), bcrypt.gensalt())
                db.change_password(u['id'], hashed)
                st.success("Password Updated!")
            else: st.error("Passwords must match and be 6+ characters.")
