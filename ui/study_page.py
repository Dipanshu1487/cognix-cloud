import streamlit as st
import upload.db as db
import os
from core.gemini_engine import ask_gemini

def resolve_path(path):
    """
    Tries to resolve a path. 
    If absolute Windows path, attempts to convert to relative 'uploads/...'
    """
    if not path: return None
    # If file exists as is, return it
    if os.path.exists(path): return path
    
    # Handle absolute Windows paths (e.g. C:\...\uploads\file.jpg)
    if "uploads" in path:
        relative_part = path.split("uploads")[-1].lstrip("\\").lstrip("/")
        new_path = os.path.join("uploads", relative_part)
        if os.path.exists(new_path): return new_path
        
    return None

def build_context(topic_id, details):
    notes = db.get_notes(topic_id)
    questions = db.get_questions(topic_id)
    
    # Context now includes full hierarchy to avoid ambiguity
    context = f"""Subject: {details.get('subject')}
Unit: {details.get('unit')}
Section: {details.get('section')}
Topic: {details.get('topic')}

Content:
"""
    
    if notes:
        context += "\nStudy Notes:\n"
        for note in notes:
            if note['content']:
                context += f"- {note['content']}\n"
    
    if questions and "q_idx" in st.session_state:
        q = questions[st.session_state.q_idx]
        context += f"\nRelevant Question:\n{q['question_text']}\n"
        
    return context

def explain_topic(topic_id, details):
    context = build_context(topic_id, details)
    if not context.strip().split("\n\n")[1:]: 
        st.warning("No content available for explanation.")
        return

    with st.spinner("cogniX is analyzing..."):
        prompt = f"""You are an expert teacher.

Explain the following topic clearly and accurately.

Context:
{context}

Important:
* Stay strictly within this subject domain
* Do NOT assume other meanings (e.g., if it's DSA, don't explain using Geometry)
* Use examples relevant to this topic only
* Keep explanation simple and structured step-by-step."""
        
        try:
            response = ask_gemini(prompt)
            st.session_state[f"ai_explanation_{topic_id}"] = response
        except Exception as e:
            st.error(f"Error getting explanation: {e}")

def render_study_page():
    topic_id = st.session_state.get("selected_topic")
    if not topic_id:
        st.warning("⚠️ No topic selected. Please choose a topic from the Subjects page.")
        if st.button("Go to Subjects"):
            st.session_state["current_page"] = "Subjects"
            st.rerun()
        st.stop()


    details = db.get_topic_details(topic_id)
    if not details:
        st.error("Topic not found.")
        st.stop()

    # 1. Header
    st.markdown(f"<h1>📖 {details['topic']}</h1>", unsafe_allow_html=True)
    hierarchy = [x for x in [details.get('subject'), details.get('unit'), details.get('section'), details.get('topic')] if x]
    st.markdown(f"<p style='font-size:20px; color:#64748B; margin-top:-16px; margin-bottom:24px;'>{' → '.join(hierarchy)}</p>", unsafe_allow_html=True)
    
    col_back, col_ai, col_done = st.columns([1, 1, 1])
    with col_back:
        if st.button("⬅ Back to Subjects", use_container_width=True):
            st.session_state["current_page"] = "Subjects"
            st.rerun()
    with col_ai:
        if st.button("🤖 Ask AI about this topic", use_container_width=True, type="primary"):
            explain_topic(topic_id, details)
            st.rerun()
    with col_done:
        # Check if already completed
        progress_data = db.get_progress(st.session_state.user['id'], topic_id)
        is_completed = progress_data.get('completed') if progress_data else False
        
        if is_completed:
            st.button("✅ Completed", use_container_width=True, disabled=True)
        else:
            if st.button("🏁 Mark as Completed", use_container_width=True, help="Mark this topic as fully understood"):
                db.mark_topic_completed(st.session_state.user['id'], topic_id)
                st.toast("Topic Completed!", icon="🎯")
                st.rerun()

    # Show explanation if it exists
    if f"ai_explanation_{topic_id}" in st.session_state:
        with st.expander("🤖 cogniX AI Analysis", expanded=True):
            st.markdown(f"<div style='font-size:24px; line-height:1.6;'>{st.session_state[f'ai_explanation_{topic_id}']}</div>", unsafe_allow_html=True)
            if st.button("Clear Explanation"):
                del st.session_state[f'ai_explanation_{topic_id}']
                st.rerun()

    st.divider()

    # 2. Tabs for content
    tab1, tab2 = st.tabs(["📝 Notes", "🎯 Practice Questions"])

    with tab1:
        notes = db.get_notes(topic_id)
        if not notes:
            st.info("No notes available for this topic.")
        else:
            for note in notes:
                with st.container(border=True):
                    if note['content']:
                        st.markdown(f"<div style='font-size:24px;'>{note['content']}</div>", unsafe_allow_html=True)
                    
                    res_path = resolve_path(note['file_path'])
                    if res_path:
                        ext = os.path.splitext(res_path)[1].lower()
                        if ext in ['.jpg', '.jpeg', '.png']:
                            st.image(res_path, use_container_width=True)
                        elif ext == '.pdf':
                            try:
                                with open(res_path, "rb") as f:
                                    st.download_button(
                                        label="Open PDF Document",
                                        data=f,
                                        file_name=os.path.basename(res_path),
                                        mime="application/pdf",
                                        key=f"pdf_note_{note['id']}",
                                        use_container_width=True
                                    )
                            except Exception as e:
                                st.warning(f"Could not open PDF: {e}")
                        else:
                            st.markdown(f"[📁 Download File]({res_path})")
                    elif note['file_path']:
                        st.warning(f"File not found: {os.path.basename(note['file_path'])}")
                    st.caption(f"Uploaded: {note['created_at']}")

    with tab2:
        questions = db.get_questions(topic_id)
        if not questions:
            st.info("No practice questions available for this topic.")
        else:
            if "q_idx" not in st.session_state:
                st.session_state.q_idx = 0
            
            # Reset index if it exceeds list (e.g. after deletion or change)
            if st.session_state.q_idx >= len(questions):
                st.session_state.q_idx = 0

            q = questions[st.session_state.q_idx]
            
            st.markdown(f"<h3>Question {st.session_state.q_idx + 1} of {len(questions)}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:18px; color:#64748B;'>Difficulty: <b>{q['difficulty'].upper()}</b></p>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown(f"<div style='font-size:28px; font-weight:500; margin-bottom:24px;'>{q['question_text']}</div>", unsafe_allow_html=True)
                res_q_path = resolve_path(q['file_path'])
                if res_q_path:
                    ext = os.path.splitext(res_q_path)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png']:
                        st.image(res_q_path)
                elif q['file_path']:
                    st.warning("Question image not found.")
                
                user_ans = st.text_area("Your Answer", key=f"ans_{q['id']}")
                
                if st.button("Submit Answer", type="primary"):
                    st.session_state[f"show_ans_{q['id']}"] = True
                    is_correct = user_ans.strip().lower() == q['answer'].strip().lower()
                    user_id = st.session_state.user['id']
                    db.update_practice(user_id, topic_id, is_correct)

                if st.session_state.get(f"show_ans_{q['id']}"):
                    st.success(f"**Correct Answer:**\n{q['answer']}")
                    st.info(f"**Explanation:**\n{q['explanation']}")

            # Navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅ Previous") and st.session_state.q_idx > 0:
                    st.session_state.q_idx -= 1
                    st.rerun()
            with col3:
                if st.button("Next ➡") and st.session_state.q_idx < len(questions) - 1:
                    st.session_state.q_idx += 1
                    st.rerun()
