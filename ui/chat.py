import streamlit as st
import requests
import time
import pandas as pd
import os

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from core.listener import listen
import core.voice as voice
from memory.student_intelligence import StudentIntelligenceSystem
import upload.db as db

@st.cache_resource
def get_sis(db_config):
    return StudentIntelligenceSystem(db_config)

def process_query(query_text):
    sis = get_sis(st.session_state.db_config)
    
    # Check for uploaded file context
    file_context = ""
    if st.session_state.get("pending_file_content"):
        file_context = st.session_state.pending_file_content
        
    active_topic_id = st.session_state.get("active_topic")
    topic_context = ""
    
    # Vague Follow-up Detection
    vague_followups = ["explain", "example", "why", "elaborate", "how", "more", "detail", "definition"]
    is_followup = len(query_text.split()) < 5 and any(f in query_text.lower() for f in vague_followups)
    
    # Classification (Simple check for now)
    is_general = False # Default to academic for better context
    
    # Topic Detection (Only for academic queries)
    detection = None
    if not is_general:
        detection = sis.process_chat_interaction(st.session_state.user['id'], query_text)
        if detection and isinstance(detection, dict):
            tid = detection.get('topic_id')
            if tid:
                topic_details = sis.get_topic_details(tid)
                if topic_details:
                    topic_context = f"\nFocused Topic: {topic_details.get('name')}\nTopic Details: {topic_details.get('description')}"
                    st.session_state.last_academic_topic = topic_details.get('name')
        elif active_topic_id:
            topic_details = sis.get_topic_details(active_topic_id)
            if topic_details:
                topic_context = f"\nCurrently Studying: {topic_details.get('name')}\nTopic Context: {topic_details.get('description')}"
                st.session_state.last_academic_topic = topic_details.get('name')

    if is_general:
        full_query = f"The user is asking a general knowledge question. Please answer normally.\n\nUser: {query_text}"
    elif is_followup and st.session_state.get("last_academic_topic"):
        last_topic = st.session_state.get("last_academic_topic")
        full_query = f"Previous topic: {last_topic}\nUser query: {query_text}\n\nSince this query is a follow-up, refer to the previous topic '{last_topic}' and provide a detailed academic response."
    else:
        full_query = f"You are an academic assistant. {topic_context}\n\nUser: {query_text}"
    
    if file_context:
        full_query = f"{file_context}\n\nBased on the document context above, please answer this query: {query_text}"

    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    display_text = query_text
    if file_context:
        # Don't show the massive text block in the UI bubble
        display_text = f"📄 [Analyzing attached file] {query_text}"

    st.session_state.messages.append({"role": "You", "content": display_text})
    st.session_state.is_thinking = True
    st.rerun()

def get_response(query_text):
    sis = get_sis(st.session_state.db_config)
    
    file_context = ""
    if st.session_state.get("pending_file_content"):
        file_context = st.session_state.pending_file_content
        st.session_state.pending_file_content = None # Clear it
        
    active_topic_id = st.session_state.get("active_topic")
    topic_context = ""
    
    # Vague Follow-up Detection
    vague_followups = ["explain", "example", "why", "elaborate", "how", "more", "detail", "definition"]
    is_followup = len(query_text.split()) < 5 and any(f in query_text.lower() for f in vague_followups)
    # Classification
    is_general = False
    
    detection = None
    if not is_general:
        detection = sis.process_chat_interaction(st.session_state.user['id'], query_text)
        if detection and isinstance(detection, dict):
            tid = detection.get('topic_id')
            if tid:
                topic_details = sis.get_topic_details(tid)
                if topic_details:
                    topic_context = f"\nFocused Topic: {topic_details.get('name')}\nTopic Details: {topic_details.get('description')}"
                    st.session_state.last_academic_topic = topic_details.get('name')
        elif active_topic_id:
            topic_details = sis.get_topic_details(active_topic_id)
            if topic_details:
                topic_context = f"\nCurrently Studying: {topic_details.get('name')}\nTopic Context: {topic_details.get('description')}"
                st.session_state.last_academic_topic = topic_details.get('name')

    if is_general:
        full_query = f"The user is asking a general knowledge question. Please answer normally.\n\nUser: {query_text}"
    elif is_followup and st.session_state.get("last_academic_topic"):
        last_topic = st.session_state.get("last_academic_topic")
        full_query = f"Previous topic: {last_topic}\nUser query: {query_text}\n\nSince this query is a follow-up, refer to the previous topic '{last_topic}' and provide a detailed academic response."
    else:
        full_query = f"You are an academic assistant. {topic_context}\n\nUser: {query_text}"
    
    if file_context:
        full_query = f"{file_context}\n\nBased on the document context above, please answer this query: {query_text}"
    
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json={"query": full_query}, timeout=30)
        jarvis_response = response.json().get("response", "No response received.") if response.status_code == 200 else f"Error: {response.status_code}"
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # FALLBACK TO GEMINI DIRECTLY
        from core.gemini_engine import ask_gemini
        try:
            jarvis_response = ask_gemini(full_query)
            # Add a small hint that we're using fallback
            jarvis_response = f"✨ [Gemini Fallback] {jarvis_response}"
        except Exception as e:
            jarvis_response = f"Backend Unreachable & Gemini Error: {e}"
    except Exception as e:
        jarvis_response = f"Error: {e}"

    tracking_data = {"logged": False}
    if detection and isinstance(detection, dict):
        tracking_data = {
            "logged": True,
            "topic_name": detection.get('name', 'Unknown'),
            "confidence": detection.get('confidence', 0),
            "method": detection.get('method', 'N/A')
        }

    st.session_state.messages.append({"role": "cogniX", "content": jarvis_response, "tracking": tracking_data})
    st.session_state.is_thinking = False
    
    if st.session_state.get("voice_enabled", False):
        voice.stop_speaking()
        voice.speak_async(jarvis_response)
    
    st.rerun()

def handle_mic():
    txt = listen()
    if txt:
        process_query(txt)

def render_chat():
    sis = get_sis(st.session_state.db_config)
    from ui.styles import THEMES, ACCENTS
    
    t = THEMES.get(st.session_state.theme, THEMES["light"])
    a = ACCENTS.get(st.session_state.accent, "#3b82f6")
    
    # Custom Chat Styles (Injecting locally to avoid conflicts)
    chat_css = f"""
    <style>
    .chat-bubble {{
        padding: 12px 18px;
        border-radius: 12px;
        max-width: 85%;
        margin-bottom: 10px;
        line-height: 1.5;
    }}
    .chat-bubble.user {{
        background-color: {a};
        color: {'white' if st.session_state.theme == 'dark' else '#0b1220'};
        margin-left: auto;
        border-bottom-right-radius: 2px;
        box-shadow: 0 4px 15px {a}33;
        font-weight: 500;
    }}
    .chat-bubble.assistant {{
        background-color: {t['hover']};
        color: {t['text']};
        margin-right: auto;
        border: 1px solid {t['border']};
        border-bottom-left-radius: 2px;
    }}
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .chat-row {{
        display: flex;
        width: 100%;
    }}
    .chat-row.user {{
        justify-content: flex-end;
    }}
    .chat-row.assistant {{
        justify-content: flex-start;
    }}
    .typing-dot {{
        height: 8px;
        width: 8px;
        background-color: {a};
        border-radius: 50%;
        display: inline-block;
        margin-right: 3px;
        animation: typing 1s infinite ease-in-out;
    }}
    @keyframes typing {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-5px); }}
    }}
    </style>
    """
    st.markdown(chat_css, unsafe_allow_html=True)

    # Top Header and Menu
    h_col1, h_col2 = st.columns([0.9, 0.1])
    with h_col1:
        st.header("🤖 cogniX Intelligent Chat")
    with h_col2:
        with st.popover("⋮", help="Chat Settings"):
            st.markdown("### Chat Settings")
            st.session_state.voice_enabled = st.toggle("Voice Response", value=st.session_state.get("voice_enabled", False))
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
    
    active_topic_id = st.session_state.get("active_topic")
    if active_topic_id:
        topic_name = sis.get_topic_name(active_topic_id)
        st.info(f"🎯 Currently Focused on: **{topic_name}**")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat Container
    chat_container = st.container(height=500, border=True)
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if not st.session_state.messages:
            st.info("Ask anything about your studies or current topic.")
        for msg in st.session_state.messages:
            if msg["role"] == "You":
                st.markdown(f'<div class="chat-row user"><div class="chat-bubble user">{msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                track = msg.get("tracking", {})
                track_html = ""
                if track.get("logged"):
                    track_html = f"""
                    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid {t['border']}; font-size: 0.8em; color: {t['muted']};">
                        📍 Auto-detected Topic: {track['topic_name']}
                    </div>
                    """
                st.markdown(f'<div class="chat-row assistant"><div class="chat-bubble assistant">{msg["content"]}{track_html}</div></div>', unsafe_allow_html=True)
        
        if st.session_state.get("is_thinking"):
            st.markdown(f'<div class="chat-row assistant"><div class="chat-bubble assistant"><div class="typing-dot"></div><div class="typing-dot" style="animation-delay:0.2s"></div><div class="typing-dot" style="animation-delay:0.4s"></div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Trigger response if thinking
    if st.session_state.get("is_thinking") and st.session_state.messages:
        last_msg = st.session_state.messages[-1]
        if last_msg["role"] == "You":
            get_response(last_msg["content"])
    c1, c2, c3 = st.columns([0.8, 0.1, 0.1])
    with c1:
        prompt = st.chat_input("How can I help you study today?")
        if prompt:
            process_query(prompt)
    
    with c2:
        if st.button("🎤", use_container_width=True, help="Voice Input"):
            with st.spinner("Listening..."):
                handle_mic()
    
    with c3:
        with st.popover("📎", help="Attach File/Photo"):
            att_file = st.file_uploader("Upload Image or Doc", type=["jpg", "png", "jpeg", "pdf", "txt"])
            if att_file:
                st.info(f"Attached: {att_file.name}")
                if st.button("Analyze Attachment", use_container_width=True):
                    content_text = ""
                    file_type = att_file.type
                    
                    try:
                        if "text/plain" in file_type:
                            content_text = att_file.read().decode()
                        elif "pdf" in file_type:
                            import pdfplumber
                            with pdfplumber.open(att_file) as pdf:
                                content_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                        elif "image" in file_type:
                            img_data = att_file.read()
                            from core.gemini_engine import ask_gemini
                            with st.spinner("Analyzing image with Gemini..."):
                                response = ask_gemini("Analyze this image for academic content and explain it.", image_data=img_data)
                                st.session_state.messages.append({"role": "You", "content": f"[Image Uploaded: {att_file.name}]"})
                                st.session_state.messages.append({"role": "cogniX", "content": response})
                                st.rerun()

                        if content_text:
                            # Send extracted text to the brain
                            st.session_state.messages.append({"role": "You", "content": f"[File Uploaded: {att_file.name}]"})
                            st.session_state.is_thinking = True
                            # Inject content into the next processing cycle
                            st.session_state.pending_file_content = f"CONTEXT FROM UPLOADED FILE '{att_file.name}':\n\n{content_text[:2000]}"
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"Error analyzing file: {e}")

if __name__ == "__main__":
    # If run standalone for testing
    st.set_page_config(page_title="cogniX Chat Test")
    if "db_config" not in st.session_state:
        st.session_state.db_config = {"dbname": "postgres", "user": "postgres", "password": "", "host": "localhost", "use_sqlite": False}
    render_chat()
