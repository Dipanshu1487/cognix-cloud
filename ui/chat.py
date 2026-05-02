import streamlit as st
import requests
import time
import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from core.listener import listen
import core.voice as voice
from memory.student_intelligence import StudentIntelligenceSystem

@st.cache_resource
def get_sis(db_config):
    return StudentIntelligenceSystem(db_config)

st.set_page_config(page_title="cogniX OS", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

state_defaults = {
    "db_config": {"dbname": "cognix_db", "user": "postgres", "password": "yourpassword", "host": "localhost"},
    "messages": [],
    "theme": "light",
    "accent": "blue",
    "scale": "medium",
    "chat_style": "comfortable",
    "voice_enabled": True,
    "auto_send": False,
    "selected_topic": None,
    "selected_subject": None,
    "selected_chapter": None,
}

for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

sis = get_sis(st.session_state.db_config)

theme_map = {
    "dark": {"bg": "#020617", "card": "#0f172a", "text": "#f8fafc", "muted": "#94a3b8", "border": "#1e293b", "sidebar": "#020617"},
    "grey": {"bg": "#1f2937", "card": "#374151", "text": "#f3f4f6", "muted": "#9ca3af", "border": "#4b5563", "sidebar": "#111827"},
    "light": {"bg": "#ffffff", "card": "#f8fafc", "text": "#0f172a", "muted": "#64748b", "border": "#e2e8f0", "sidebar": "#f1f5f9"}
}
accent_map = {
    "blue": "#3b82f6", "purple": "#a855f7", "green": "#22c55e"
}
scale_map = {
    "small": {"fs": "14px", "pad": "10px", "mw": "800px", "bubble_fs": "0.9em"},
    "medium": {"fs": "16px", "pad": "20px", "mw": "1100px", "bubble_fs": "1em"},
    "large": {"fs": "18px", "pad": "30px", "mw": "1400px", "bubble_fs": "1.1em"}
}
chat_style_map = {
    "compact": {"bubble_p": "8px 12px", "gap": "8px"},
    "comfortable": {"bubble_p": "16px 24px", "gap": "20px"}
}

t = theme_map[st.session_state.theme]
a = accent_map[st.session_state.accent]
s = scale_map[st.session_state.scale]
cs = chat_style_map[st.session_state.chat_style]

css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {t['text']} !important;
    font-size: {s['fs']} !important;
}}
.stApp {{
    background-color: {t['bg']};
}}
[data-testid="stSidebar"] {{
    background-color: {t['sidebar']} !important;
    border-right: 1px solid {t['border']} !important;
}}
.block-container {{
    max-width: {s['mw']} !important;
    margin: 0 auto !important;
    padding-top: 1rem !important;
    padding-right: 1.5rem !important;
    padding-left: 1.5rem !important;
    padding-bottom: 2rem !important;
}}
.os-card {{
    background-color: {t['card']};
    border-radius: 12px;
    padding: {s['pad']};
    border: 1px solid {t['border']};
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.os-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}}
.txt-main {{ color: {t['text']}; font-weight: 700; }}
.txt-muted {{ color: {t['muted']}; font-weight: 500; font-size: 0.9em; }}
.txt-accent {{ color: {a}; font-weight: 700; }}
.stChatMessage {{ background-color: transparent !important; border: none !important; margin-bottom: {cs['gap']} !important; padding: 0 !important; }}
.chat-row {{ display: flex; width: 100%; }}
.chat-row.user {{ justify-content: flex-end; }}
.chat-row.assistant {{ justify-content: flex-start; }}
.chat-bubble {{
    padding: {cs['bubble_p']};
    border-radius: 12px;
    max-width: 80%;
    font-size: {s['bubble_fs']};
    line-height: 1.6;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}}
.chat-bubble.user {{
    background-color: {a};
    color: #0b1220;
    border-bottom-right-radius: 2px;
    font-weight: 500;
}}
.chat-bubble.assistant {{
    background-color: {t['card']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-bottom-left-radius: 2px;
}}
div[data-testid="stChatInput"] {{
    background-color: {t['card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2) !important;
}}
div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div {{
    background-color: {t['card']} !important;
    border-color: {t['border']} !important;
    color: {t['text']} !important;
}}
.stButton>button {{
    background-color: {t['card']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s ease;
}}
.stButton>button:hover {{
    border-color: {a};
    color: {a};
}}
.focus-bar {{
    background-color: {t['card']};
    border-radius: 16px;
    padding: 15px 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 6px solid {a};
    margin-bottom: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}}
.topic-card {{
    background-color: {t['card']};
    border-radius: 16px;
    padding: 24px;
    border: 1px solid {t['border']};
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}}
.topic-card:hover {{
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 25px -5px rgba(0,0,0,0.2);
    border-color: {a}88;
}}
.topic-card.active {{
    border: 2px solid {a} !important;
    box-shadow: 0 0 25px {a}44 !important;
}}
.badge {{
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.75em;
    font-weight: 700;
    text-transform: uppercase;
}}
.badge-weak {{ background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef444433; }}
.badge-intermediate {{ background: rgba(234, 179, 8, 0.1); color: #eab308; border: 1px solid #eab30833; }}
.badge-strong {{ background: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid #22c55e33; }}
.stop-btn>button {{
    background-color: rgba(239, 68, 68, 0.1) !important;
    color: #ef4444 !important;
    border: 1px solid #ef4444 !important;
}}
.stop-btn>button:hover {{ background-color: #ef4444 !important; color: white !important; }}
.status-dot {{ width: 8px; height: 8px; background-color: #4ade80; border-radius: 50%; display: inline-block; margin-right: 6px; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

tb1, tb2, tb3 = st.columns([1.5, 2, 1.5])
with tb1:
    st.markdown(f'<div style="font-size: 1.4em; font-weight: 700; display:flex; align-items:center;">🤖 <span style="color:{a}; margin-left:8px;">cogniX OS</span></div>', unsafe_allow_html=True)
with tb3:
    st.markdown(f'<div style="text-align: right; margin-top: 5px; font-weight: 500; font-size: 0.9em; color:{t["muted"]};"><div class="status-dot"></div>System Online</div>', unsafe_allow_html=True)

st.markdown(f"<hr style='border: 1px solid {t['border']}; margin: 15px 0 25px 0;'>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f'<div style="color: {t["muted"]}; font-weight: 600; font-size: 0.85em; letter-spacing: 0.05em; margin-bottom: 20px; text-transform:uppercase;">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("", ["Dashboard", "Chat", "Subjects", "Practice", "Analytics"], label_visibility="collapsed", key="page_nav")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("⚙️ System Settings", expanded=False):
        st.session_state.theme = st.selectbox("UI Theme", ["dark", "grey", "light"], index=["dark", "grey", "light"].index(st.session_state.theme))
        st.session_state.accent = st.selectbox("Accent Color", ["blue", "purple", "green"], index=["blue", "purple", "green"].index(st.session_state.accent))
        st.session_state.scale = st.selectbox("Interface Scale", ["small", "medium", "large"], index=["small", "medium", "large"].index(st.session_state.scale))
        st.session_state.chat_style = st.selectbox("Chat Style", ["compact", "comfortable"], index=["compact", "comfortable"].index(st.session_state.chat_style))
        
        st.markdown(f"<hr style='border: 1px solid {t['border']}; margin: 15px 0;'>", unsafe_allow_html=True)
        
        st.session_state.voice_enabled = st.toggle("Voice Output", value=st.session_state.voice_enabled)
        st.session_state.auto_send = st.toggle("Auto Send Voice", value=st.session_state.auto_send)

def process_query(query_text):
    active_topic_id = st.session_state.get("active_topic")
    topic_context = ""
    
    # Topic Detection
    detection = sis.process_chat_interaction(query_text)
    if detection:
        topic_details = sis.get_topic_details(detection['topic_id'])
        topic_context = f"\nTopic: {topic_details['name']}\nContext: {topic_details['description']}"
    elif active_topic_id:
        topic_details = sis.get_topic_details(active_topic_id)
        topic_context = f"\nTopic: {topic_details['name']}\nContext: {topic_details['description']}"

    full_query = f"You are an academic assistant. {topic_context}\n\nUser: {query_text}"

    st.session_state.messages.append({"role": "You", "content": query_text})
    
    try:
        response = requests.post("http://127.0.0.1:8000/chat", json={"query": full_query}, timeout=30)
        jarvis_response = response.json().get("response", "No response received.") if response.status_code == 200 else f"Error: {response.status_code}"
    except:
        jarvis_response = "Error connecting to backend."

    tracking_data = {"logged": False}
    if detection:
        tracking_data = {
            "logged": True,
            "topic_name": topic_details['name'],
            "confidence": detection['confidence'],
            "method": detection['method']
        }

    st.session_state.messages.append({"role": "cogniX", "content": jarvis_response, "tracking": tracking_data})
    
    if st.session_state.voice_enabled:
        voice.stop_speaking()
        voice.speak_async(jarvis_response)
    
    st.rerun()

def handle_mic():
    txt = listen()
    if txt:
        process_query(txt)

def render_chat():
    active_topic_id = st.session_state.get("active_topic")
    if active_topic_id:
        topic_name = sis.get_topic_name(active_topic_id)
        st.info(f"🎯 Currently Studying: {topic_name}")
    
    st.markdown('<h2 class="txt-main" style="margin-bottom: 20px;">Chat Interface</h2>', unsafe_allow_html=True)
    
    chat_container = st.container(height=500, border=False)
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "You":
                st.markdown(f'<div class="chat-row user"><div class="chat-bubble user">{msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                track = msg.get("tracking", {})
                track_html = ""
                if track.get("logged"):
                    track_html = f"""
                    <div style="margin-top: 10px; padding: 5px; border-left: 2px solid {a}; font-size: 0.8em; color: {t['muted']};">
                        Detected: {track['topic_name']} ({track['method']} | {track['confidence']})
                    </div>
                    """
                st.markdown(f'<div class="chat-row assistant"><div class="chat-bubble assistant">{msg["content"]}{track_html}</div></div>', unsafe_allow_html=True)

    ctrl1, ctrl2, _ = st.columns([0.15, 0.15, 0.70])
    with ctrl1:
        if st.button("🎤 Speak", use_container_width=True):
            with st.spinner("Listening..."):
                handle_mic()
    
    with ctrl2:
        if voice.is_speaking:
            if st.button("🔴 Stop", use_container_width=True):
                voice.stop_speaking()
                st.rerun()

    prompt = st.chat_input("Ask a question about your syllabus...")
    if prompt:
        process_query(prompt)

def render_dashboard():
    st.markdown(f'<h1 class="txt-main" style="margin-bottom:0; font-size: 2.2em;">Welcome back</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="txt-muted" style="margin-bottom:30px; font-size:1.05em;">System operational. Your neural pathway optimization is standing by.</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, title, val, emj in zip([c1,c2,c3,c4], ["Topics", "Accuracy", "Weak", "Study Time"], ["-", "-", "-", "-"], ["📚", "🎯", "⚠️", "⏱️"]):
        with col:
            st.markdown(f'<div class="os-card"><span style="margin-right:8px;">{emj}</span><span class="txt-muted">{title}</span><div style="font-size:2em; font-weight:700; color:{t["text"]}; margin-top:8px;">{val}</div></div>', unsafe_allow_html=True)

from ui.subjects import render_subjects as render_subjects_module

def render_subjects():
    render_subjects_module(sis)

if page == "Dashboard": render_dashboard()
elif page == "Chat": render_chat()
elif page == "Subjects": render_subjects()
else: st.markdown(f'<h2 class="txt-muted" style="text-align:center; margin-top:100px;">[{page} Module Offline]</h2>', unsafe_allow_html=True)
