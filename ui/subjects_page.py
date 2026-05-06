import streamlit as st
import upload.db as db
from ui.components import render_topic_card

def render_subjects_page(sis):
    st.markdown("<h1>📚 Study Subjects</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:24px; margin-top:-16px; margin-bottom:32px;'>Explore your academic units and sections.</p>", unsafe_allow_html=True)

    structure = sis.get_subject_structure()
    subjects = list(structure.keys())
    
    # PERFORMANCE: Bulk fetch all user progress once to avoid N+1 query problem in the loop
    user_id = st.session_state.user['id']
    user_progress_map = db.get_all_user_progress(user_id)
    
    if not subjects:
        st.warning("No academic subjects found in the database.")
        st.stop()

    tabs = st.tabs(subjects)

    for i, subject_name in enumerate(subjects):
        with tabs[i]:
            units = structure[subject_name]
            
            if not units:
                st.info(f"No units defined for {subject_name}.")
                continue

            for unit_name, sections in units.items():
                with st.expander(f"📁 {unit_name}", expanded=True):
                    for section_name, topics in sections.items():
                        st.markdown(f"<h3 style='margin-top:32px; border-bottom:2px solid rgba(0,0,0,0.05); padding-bottom:8px;'>📍 {section_name}</h3>", unsafe_allow_html=True)
                        
                        cols = st.columns(2)
                        for j, topic in enumerate(topics):
                            with cols[j % 2]:
                                # Use cached progress map instead of hitting DB per topic card
                                progress = user_progress_map.get(topic['name'])
                                
                                # Mastery = 50% (Notes) + 50% (Practice)
                                if progress:
                                    is_completed = progress.get('completed', 0)
                                    attempts = progress.get('attempts', 0)
                                    corr = progress.get('correct', 0)
                                    
                                    acc_raw = (corr / attempts) if attempts > 0 else 0.0
                                    
                                    completion_weight = 0.5 if is_completed else 0.0
                                    practice_weight = 0.5 * acc_raw
                                    accuracy = completion_weight + practice_weight
                                else:
                                    is_completed = 0
                                    attempts = 0
                                    accuracy = 0.0
                                
                                if is_completed:
                                    topic_status = "Completed"
                                    trend = "improving"
                                elif accuracy == 0 and attempts == 0:
                                    topic_status = "Not Started"
                                    trend = "new"
                                elif accuracy > 0.8:
                                    topic_status = "Mastered"
                                    trend = "improving"
                                else:
                                    topic_status = "Learning"
                                    trend = "stable"

                                render_topic_card(
                                    topic_name=topic['name'],
                                    accuracy=accuracy,
                                    trend=trend,
                                    status=topic_status,
                                    topic_id=topic['id'],
                                    chapter=unit_name,
                                    subject=subject_name
                                )
                    st.markdown("<br>", unsafe_allow_html=True)
