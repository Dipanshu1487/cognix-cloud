import streamlit as st
import upload.db as db
import upload.file_handler as file_handler

def render_upload_page():
    db.init_db()
    st.title("📤 Upload Content")
    st.caption("Expand the academic library by adding notes and practice questions.")
    st.write("")

    subjects = db.fetch_subjects()
    if not subjects:
        st.warning("No subjects found.")
        st.stop()

    subject_dict = {s['name']: s['id'] for s in subjects}
    selected_subject = st.selectbox("Select Subject", options=[""] + list(subject_dict.keys()))

    if selected_subject:
        units = db.fetch_units(subject_dict[selected_subject])
        unit_dict = {u['name']: u['id'] for u in units}
        selected_unit = st.selectbox("Select Unit", options=[""] + list(unit_dict.keys()))

        if selected_unit:
            sections = db.fetch_sections(unit_dict[selected_unit])
            section_dict = {s['name']: s['id'] for s in sections}
            selected_section = st.selectbox("Select Section", options=[""] + list(section_dict.keys()))

            if selected_section:
                topics = db.fetch_topics(section_dict[selected_section])
                topic_dict = {t['name']: t['id'] for t in topics}
                selected_topic = st.selectbox("Select Topic", options=[""] + list(topic_dict.keys()))

                if selected_topic:
                    topic_id = topic_dict[selected_topic]
                    
                    st.divider()
                    # Debug prints
                    st.sidebar.write(f"**DEBUG:**")
                    st.sidebar.write(f"Subject: {selected_subject}")
                    st.sidebar.write(f"Unit: {selected_unit}")
                    st.sidebar.write(f"Section: {selected_section}")
                    st.sidebar.write(f"Topic: {selected_topic}")
                    st.sidebar.write(f"Topics Fetched: {len(topics)}")

                    content_type = st.radio("Content Type", options=["Notes", "Question"], horizontal=True)

                    if content_type == "Notes":
                        content = st.text_area("Content")
                        uploaded_files = st.file_uploader("Upload Files (Max 15)", type=["pdf", "png", "jpg"], accept_multiple_files=True)
                        if st.button("Upload"):
                            if not content and not uploaded_files:
                                st.error("Please provide content or at least one file.")
                            elif len(uploaded_files) > 15:
                                st.error("Maximum 15 files allowed.")
                            else:
                                if uploaded_files:
                                    for f in uploaded_files:
                                        file_path = file_handler.save_file(f)
                                        # For multiple files, we attach the same content to each or just the file?
                                        # Let's attach content to all if provided, or only to the first one?
                                        # User usually wants to upload a batch of files.
                                        db.insert_note(topic_id, content if f == uploaded_files[0] else "", file_path)
                                    st.success(f"Successfully uploaded {len(uploaded_files)} files!")
                                else:
                                    db.insert_note(topic_id, content, None)
                                    st.success("Note uploaded successfully!")

                    elif content_type == "Question":
                        question_text = st.text_area("Question")
                        difficulty = st.selectbox("Difficulty", options=["easy", "medium", "hard"])
                        answer = st.text_area("Answer")
                        explanation = st.text_area("Explanation")
                        uploaded_files = st.file_uploader("Upload Files (Max 15)", type=["pdf", "png", "jpg"], accept_multiple_files=True)
                        if st.button("Upload"):
                            if not question_text and not uploaded_files:
                                st.error("Please provide a question or at least one file.")
                            elif len(uploaded_files) > 15:
                                st.error("Maximum 15 files allowed.")
                            else:
                                if uploaded_files:
                                    for f in uploaded_files:
                                        file_path = file_handler.save_file(f)
                                        # Attach details to the first file entry, others just the file? 
                                        # Or repeat? Usually questions are 1 per file or 1 per text.
                                        # If multiple files, they might be images for one question or multiple questions.
                                        # We'll treat each file as a separate entry for simplicity.
                                        db.insert_question(topic_id, question_text if f == uploaded_files[0] else "", difficulty, answer, explanation, file_path)
                                    st.success(f"Successfully uploaded {len(uploaded_files)} files!")
                                else:
                                    db.insert_question(topic_id, question_text, difficulty, answer, explanation, None)
                                    st.success("Question uploaded successfully!")
