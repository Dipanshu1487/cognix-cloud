import streamlit as st
import upload.db as db
from ui.styles import THEMES

def render_profile_page():
    u = st.session_state.user
    t = THEMES.get(st.session_state.theme, THEMES["light"])
    
    st.header("👤 User Profile")
    st.markdown(f"<p style='color:{t['muted']}; margin-top:-16px; margin-bottom:32px;'>Manage your account details and preferences.</p>", unsafe_allow_html=True)
    
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
            st.subheader("Account Information")
            st.markdown(f"**Full Name:** {u['name']}")
            st.markdown(f"**Email:** {u.get('email', 'No email set')}")
            st.markdown(f"**Username:** {u['username']}")
            st.markdown(f"**Account Role:** {u['role'].replace('_', ' ').title()}")
            
            st.divider()
            
            new_name = st.text_input("Update Name", value=u['name'])
            new_email = st.text_input("Update Email", value=u.get('email', ''))
            
            if st.button("Save Changes", type="primary"):
                try:
                    db.update_profile(u['id'], new_name, new_email)
                    st.session_state.user['name'] = new_name
                    st.session_state.user['email'] = new_email
                    st.success("Profile updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating profile: {e}")
