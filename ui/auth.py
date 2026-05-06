import streamlit as st
import random
import re
import smtplib
from email.mime.text import MIMEText
import bcrypt
import os
from ui.components import render_logo
import upload.db as db
from psycopg2.extras import RealDictCursor

def send_otp(receiver_email, otp):
    EMAIL = os.getenv("GMAIL_USER")
    PASSWORD = os.getenv("GMAIL_PASS")

    # 2. STRICT DEBUGGING
    print(f"[OTP DEBUG] EMAIL LOADED: {EMAIL is not None}")
    print(f"[OTP DEBUG] PASSWORD LENGTH: {len(PASSWORD) if PASSWORD else 0}")

    body = f"Your cogniX verification code is: {otp}"
    msg = MIMEText(body)
    msg["Subject"] = f"{otp} is your cogniX verification code"
    msg["From"] = f"cogniX <{EMAIL}>"
    msg["To"] = receiver_email

    try:
        # 3. FORCE SMTP_SSL (Port 465)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        
        print(f"[OTP DEBUG] Success: Sent to {receiver_email}")
        return True, "OTP sent successfully"
        
    except smtplib.SMTPAuthenticationError as e:
        err = f"SMTP Auth Failed: Check if App Password is correct. {e}"
        print(f"[OTP DEBUG] {err}")
        return False, err
    except Exception as e:
        err = f"SMTP ERROR: {type(e).__name__} - {str(e)}"
        print(f"[OTP DEBUG] {err}")
        return False, err

def render_login_signup():
    # Inject Optimized High-Visibility CSS
    st.markdown("""
        <style>
        .stButton button { height: 90px !important; font-size: 2.2rem !important; border-radius: 20px !important; font-weight: 700 !important; }
        .stTabs [data-baseweb="tab"] { font-size: 2.2rem !important; height: 90px !important; }
        div[data-baseweb="input"] input { font-size: 1.5rem !important; padding: 16px !important; }
        div[data-testid="stWidgetLabel"] p { font-size: 2rem !important; font-weight: 600 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([0.1, 3.8, 0.1])
    
    with c2:
        with st.container(border=True):
            if st.session_state.auth_selection is None:
                st.markdown("<div style='padding: 40px 20px;'>", unsafe_allow_html=True)
                render_logo(size="xlarge", align="center")
                st.markdown("<h1 style='text-align: center; font-size: 4.5rem;'>Welcome to cogniX</h1>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.8rem;'>Your AI-powered academic learning system</p>", unsafe_allow_html=True)
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
            
            else:
                sel = st.session_state.auth_selection
                st.markdown(f"<h1 style='text-align: center; font-size: 3.5rem;'>{sel.title()} Access</h1>", unsafe_allow_html=True)
                
                if st.button("← Change Mode", use_container_width=True):
                    st.session_state.auth_selection = None
                    st.rerun()
                
                tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
                
                with tab_login:
                    l_user = st.text_input("Username", key="l_user")
                    l_pass = st.text_input("Password", type="password", key="l_pass")
                    if st.button("Login", use_container_width=True, type="primary"):
                        conn = db.get_connection()
                        cur = conn.cursor(cursor_factory=RealDictCursor)
                        cur.execute("SELECT * FROM users WHERE username = %s", (l_user,))
                        user_row = cur.fetchone()
                        
                        print("[AUTH DEBUG] USER FETCHED:", user_row)
                        print("[AUTH DEBUG] Available DB columns:", list(user_row.keys()) if user_row else "None")

                        valid = False
                        if not user_row:
                            print("[AUTH DEBUG] No user found for username:", l_user)
                        else:
                            print("[AUTH DEBUG] Username from DB:", user_row.get("username"))
                            
                            stored_hash = user_row.get("password")
                            
                            if not stored_hash:
                                print("[AUTH DEBUG] Password field is empty/None")
                            else:
                                print("[AUTH DEBUG] Hash type:", type(stored_hash))

                                try:
                                    # Convert memoryview to bytes if needed
                                    if isinstance(stored_hash, memoryview):
                                        stored_hash = bytes(stored_hash)
                                        print("[AUTH DEBUG] Converted memoryview to bytes")
                                    elif isinstance(stored_hash, str):
                                        stored_hash = stored_hash.encode('utf-8')
                                        print("[AUTH DEBUG] Converted string to bytes")
                                    
                                    print("[AUTH DEBUG] Final hash type:", type(stored_hash))

                                    # Check password - bcrypt.checkpw expects bytes for both params
                                    password_match = bcrypt.checkpw(
                                        l_pass.encode("utf-8"),
                                        stored_hash
                                    )

                                    print("[AUTH DEBUG] Password Match Result:", password_match)

                                    if password_match:
                                        print("[AUTH DEBUG] PASSWORD VERIFIED SUCCESSFULLY")
                                        
                                        # Get role - default to 'user' if role column doesn't exist
                                        user_role = user_row.get("role", "user")
                                        print("[AUTH DEBUG] User role:", user_role)
                                        
                                        # Check role match
                                        if sel == 'admin':
                                            if user_role in ['admin', 'super_admin']:
                                                valid = True
                                                print("[AUTH DEBUG] Admin role verified")
                                            else:
                                                print(f"[AUTH DEBUG] User role is {user_role}, not admin - only admins can access admin block")
                                        else:
                                            # For student/user access - allow any user
                                            valid = True
                                            print("[AUTH DEBUG] User role verified for student access")
                                    else:
                                        print("[AUTH DEBUG] PASSWORD VERIFICATION FAILED")
                                        
                                except Exception as e:
                                    print(f"[AUTH DEBUG] Bcrypt error: {type(e).__name__} - {e}")
                                    import traceback
                                    traceback.print_exc()
                        
                        if valid:
                            print(f"[AUTH DEBUG] Login success for {l_user}")
                            st.session_state.user = {
                                "id": user_row.get('id'),
                                "name": user_row.get('name', 'User'),
                                "username": user_row.get('username'),
                                "email": user_row.get('email'),
                                "role": user_row.get('role', 'user')
                            }
                            cur.close()
                            conn.close()
                            st.rerun()
                        else:
                            print(f"[AUTH DEBUG] Login failed for {l_user}")
                            st.error("Invalid credentials.")
                        cur.close()
                        conn.close()

                    if st.button("Forgot Password?", type="secondary", use_container_width=True):
                        st.session_state.forgot_password_mode = True
                        st.rerun()

                if st.session_state.get('forgot_password_mode'):
                    st.subheader("Reset Password")
                    reset_email = st.text_input("Enter Registered Email")
                    
                    if not st.session_state.otp_sent:
                        if st.button("Send Reset OTP"):
                            conn = db.get_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT id FROM users WHERE email = %s", (reset_email,))
                            user_data = cur.fetchone()
                            cur.close()
                            conn.close()
                            
                            if user_data:
                                otp = str(random.randint(1000, 9999))
                                st.session_state.signup_otp = otp
                                st.session_state.reset_user = user_data[0]
                                success, msg = send_otp(reset_email, otp)
                                if success:
                                    st.session_state.otp_sent = True
                                    st.success("OTP sent to your email")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to send email: {msg}")
                            else:
                                st.error("Account not found")
                    else:
                        entered_otp = st.text_input("Enter OTP")
                        new_pass = st.text_input("New Password", type="password")
                        if st.button("Reset Password"):
                            if entered_otp == st.session_state.signup_otp:
                                hashed_new = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
                                db.change_password(st.session_state.reset_user, hashed_new.decode('utf-8'))
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
                            print(f"[DB DEBUG] Checking username: {s_user}")
                            conn = db.get_connection()
                            cur = conn.cursor()
                            cur.execute("SELECT id FROM users WHERE username = %s", (s_user,))
                            if cur.fetchone():
                                print(f"[DB DEBUG] Username {s_user} already taken")
                                st.error("❌ Already taken.")
                            else:
                                print(f"[DB DEBUG] Username {s_user} available")
                                st.success("✅ Available")
                                user_valid = True
                            cur.close()
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

                    if not st.session_state.get('email_verified'):
                        if not st.session_state.get('otp_sent'):
                            if st.button("Send Verification Code", disabled=not (user_valid and email_valid)):
                                st.session_state.signup_otp = str(random.randint(1000, 9999))
                                st.session_state.signup_email = s_email
                                success, msg = send_otp(s_email, st.session_state.signup_otp)
                                if success:
                                    st.session_state.otp_sent = True
                                    st.success("Verification code sent to your email")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to send email: {msg}")
                        else:
                            st.info(f"OTP sent to {st.session_state.signup_email}")
                            entered_otp = st.text_input("Enter Verification Code", key="entered_otp")
                            if st.button("Verify OTP", type="primary", use_container_width=True):
                                if entered_otp == st.session_state.signup_otp:
                                    st.session_state.email_verified = True
                                    st.rerun()
                                else:
                                    st.error("❌ Incorrect OTP")
                    else:
                        st.success("✅ Email Verified")
                        if st.button("Sign Up", use_container_width=True, type="primary", disabled=not (s_name and user_valid and pass_valid and st.session_state.email_verified)):
                            hashed_pw = bcrypt.hashpw(s_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            conn = db.get_connection()
                            cur = conn.cursor()
                            if sel == 'admin':
                                cur.execute("INSERT INTO admin_requests (name, username, email, password) VALUES (%s, %s, %s, %s)", (s_name, s_user, s_email, hashed_pw))
                                print(f"[DB DEBUG] Admin request created for {s_user}")
                                msg = "✅ Request Sent! Wait for Super Admin approval."
                            else:
                                cur.execute("INSERT INTO users (name, username, email, password, role) VALUES (%s, %s, %s, %s, %s)", (s_name, s_user, s_email, hashed_pw, sel))
                                print(f"[DB DEBUG] Signup insert success for {s_user}")
                                msg = "✅ Created! Now Login."
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            st.session_state.signup_otp = None
                            st.session_state.email_verified = False
                            st.session_state.otp_sent = False
                            st.session_state.signup_email = None
                            st.success(msg)

