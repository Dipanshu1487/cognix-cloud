import streamlit as st
import upload.db as db

def render_practice_page():
    u = st.session_state.user
    st.title("📝 Practice Progress")
    st.caption("Review topics you have practiced and your performance.")
    st.write("")

    topics = db.get_practice_topics(u['id'])

    if not topics:
        st.info("You haven't practiced any topics yet. Go to Subjects and start a Study session!")
        return

    st.subheader("Practiced Topics")
    st.write("")

    for topic in topics:
        with st.container(border=True):
            cols = st.columns([2, 1, 1, 1])
            
            # Accuracy and Strength logic
            acc_val = (topic['correct'] / topic['attempts'] * 100) if topic['attempts'] > 0 else 0
            if acc_val >= 70:
                strength = "🟢 Strong"
            elif acc_val >= 40:
                strength = "🟡 Medium"
            else:
                strength = "🔴 Weak"
                
            with cols[0]:
                st.markdown(f"**{topic['topic_name']}**")
                st.write(strength)
            with cols[1]:
                st.metric("Attempts", topic['attempts'])
            with cols[2]:
                st.metric("Accuracy", f"{acc_val:.1f}%")
            with cols[3]:
                st.write("") # Spacing
                if st.button("Practice Again", key=f"prac_{topic['topic_id']}", use_container_width=True):
                    st.session_state["selected_topic"] = topic['topic_id']
                    st.session_state["current_page"] = "Study"
                    st.rerun()
        st.write("") # Spacing between topics
