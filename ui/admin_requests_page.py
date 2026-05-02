import streamlit as st
import upload.db as db

def render_admin_requests_page():
    st.markdown("<h1 style='text-align: center; color: #1E293B;'>📋 Admin Access Requests</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 20px;'>Manage incoming admin registration requests.</p>", unsafe_allow_html=True)
    st.divider()

    requests = db.get_pending_admin_requests()

    if not requests:
        st.info("No pending admin requests found.")
        return

    # Display requests in a card-like table layout
    for req in requests:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**👤 Name:** {req['name']}")
                st.markdown(f"**🆔 Username:** {req['username']}")
            
            with col2:
                st.markdown(f"**📧 Email:** {req['email']}")
                st.markdown(f"**⏰ Requested:** {req['created_at']}")
            
            with col3:
                st.write("") # Spacing
                btn_app = st.button("✅ Approve", key=f"app_{req['id']}", use_container_width=True, type="primary")
                btn_rej = st.button("❌ Reject", key=f"rej_{req['id']}", use_container_width=True)
                
                if btn_app:
                    if db.approve_admin_request(req['id']):
                        st.toast(f"Admin approved: {req['username']}", icon="✅")
                        st.rerun()
                    else:
                        st.error("Failed to approve request.")
                
                if btn_rej:
                    if db.reject_admin_request(req['id']):
                        st.toast(f"Request rejected: {req['username']}", icon="🗑️")
                        st.rerun()
                    else:
                        st.error("Failed to reject request.")

    st.markdown("---")
    st.caption("Only Super Admins can manage these requests.")
