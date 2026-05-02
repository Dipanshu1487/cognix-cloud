import streamlit as st
import upload.db as db
from ui.styles import THEMES
import random
import os
import smtplib
from email.mime.text import MIMEText

def send_otp(receiver_email, otp):
    # Try getting from Streamlit Secrets first (for Cloud), then OS env
    EMAIL = st.secrets.get("GMAIL_USER") or os.getenv("GMAIL_USER")
    PASSWORD = st.secrets.get("GMAIL_PASS") or os.getenv("GMAIL_PASS")

    if not EMAIL or not PASSWORD:
        return False

    msg = MIMEText(f"Your cogniX verification code is: {otp}")
    msg['Subject'] = "cogniX Verification Code"
    msg['From'] = EMAIL
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def render_profile_page():
    u = st.session_state.user
    t = THEMES.get(st.session_state.theme, THEMES["light"])
    
    st.header("👤 Account Credentials")
    st.markdown(f"<p style='color:{t['muted']}; margin-top:-16px; margin-bottom:32px;'>Securely update your personal information and credentials.</p>", unsafe_allow_html=True)
    
    # Initialize state for email verification
    if 'profile_otp_sent' not in st.session_state:
        st.session_state.profile_otp_sent = False
    if 'profile_email_verified' not in st.session_state:
        st.session_state.profile_email_verified = False

    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        
        with c1:
            initial = u['name'][0].upper() if u['name'] else "?"
            st.markdown(f"""
                <div style='background:{t['accent']}; color:white; width:150px; height:150px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:64px; font-weight:800; box-shadow: {t['shadow']};'>
                    {initial}
                </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("Change Photo", use_container_width=True):
                st.info("Profile photo upload coming soon!")
                
        with c2:
            st.subheader("Account Details")
            st.markdown(f"**Username:** `{u['username']}`")
            st.markdown(f"**Role:** {u['role'].replace('_', ' ').title()}")
            st.divider()

            # --- FORM START ---
            with st.form("profile_update_form"):
                new_name = st.text_input("Full Name", value=u['name'])
                new_email = st.text_input("Email Address", value=u.get('email', ''))
                
                email_changed = (new_email != u.get('email', ''))
                
                st.write("")
                if st.form_submit_button("Update Credentials", type="primary", use_container_width=True):
                    email_changed = (new_email != u.get('email', ''))
                    if email_changed and not st.session_state.profile_email_verified:
                        # Send OTP logic
                        otp = str(random.randint(1000, 9999))
                        st.session_state.profile_otp = otp
                        st.session_state.profile_temp_email = new_email
                        st.session_state.profile_temp_name = new_name
                        
                        if send_otp(new_email, otp):
                            st.session_state.profile_otp_sent = True
                            st.success(f"OTP sent to {new_email}")
                            st.rerun()
                        else:
                            st.error("Failed to send OTP. Check system configuration.")
                    else:
                        # Direct update (either name change only or email already verified)
                        try:
                            db.update_profile(u['id'], new_name, new_email)
                            st.session_state.user['name'] = new_name
                            st.session_state.user['email'] = new_email
                            st.session_state.profile_email_verified = False # Reset for next time
                            st.success("Credentials updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")

            # --- OTP VERIFICATION SECTION (Outside form to handle focus) ---
            if st.session_state.profile_otp_sent and not st.session_state.profile_email_verified:
                with st.container(border=True):
                    st.info(f"Please enter the code sent to {st.session_state.profile_temp_email}")
                    entered_otp = st.text_input("Enter 4-digit OTP", max_chars=4)
                    if st.button("Verify & Update", type="primary", use_container_width=True):
                        if entered_otp == st.session_state.profile_otp:
                            # Correct OTP - Perform Update
                            try:
                                db.update_profile(u['id'], st.session_state.profile_temp_name, st.session_state.profile_temp_email)
                                st.session_state.user['name'] = st.session_state.profile_temp_name
                                st.session_state.user['email'] = st.session_state.profile_temp_email
                                st.session_state.profile_otp_sent = False
                                st.session_state.profile_email_verified = False
                                st.success("Email verified and profile updated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Verification successful but update failed: {e}")
                        else:
                            st.error("Incorrect OTP. Please try again.")
                    
                    if st.button("Cancel Verification"):
                        st.session_state.profile_otp_sent = False
                        st.rerun()

            st.divider()
            st.subheader("🔐 Security")
            with st.form("password_update_form"):
                new_pass = st.text_input("New Password", type="password")
                conf_pass = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Change Password", type="secondary", use_container_width=True):
                    if new_pass != conf_pass:
                        st.error("Passwords do not match!")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        try:
                            import bcrypt
                            hashed_pw = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
                            db.change_password(u['id'], hashed_pw)
                            st.success("Password updated successfully!")
                        except Exception as e:
                            st.error(f"Password update failed: {e}")
