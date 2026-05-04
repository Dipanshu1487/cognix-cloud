"""
cogniX OS — Production UI Engine (Optimized High Visibility)
Massive typography with balanced spacing. Fixed icon text leakage and overlapping.
"""

# ── Color System ────────────────────────────────────────────────────
THEMES = {
    "light": {
        "bg":           "#F8FAFC",
        "card":         "#FFFFFF",
        "text":         "#0F172A",
        "muted":        "#64748B",
        "border":       "#E5E7EB",
        "sidebar":      "#FFFFFF",
        "hover":        "#F1F5F9",
        "active_bg":    "#E0F2FE",
        "shadow":       "0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1)",
        "success":      "#22C55E",
        "warning":      "#F59E0B",
        "error":        "#EF4444",
        "accent":       "#3B82F6",
    },
    "dark": { # Modern Dark SaaS
        "bg":           "#0F172A",
        "card":         "#1E293B",
        "text":         "#F8FAFC",
        "muted":        "#94A3B8",
        "border":       "#334155",
        "sidebar":      "#0F172A",
        "hover":        "#334155",
        "active_bg":    "#1E3A8A",
        "shadow":       "0 4px 6px -1px rgba(0, 0, 0, 0.2)",
        "success":      "#10B981",
        "warning":      "#F59E0B",
        "error":        "#EF4444",
        "accent":       "#3B82F6",
    },
}

ACCENTS = {
    "blue":    "linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)",
    "violet":  "linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%)",
    "emerald": "linear-gradient(135deg, #10B981 0%, #34D399 100%)",
    "sunset":  "linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)",
    "rose":    "linear-gradient(135deg, #F43F5E 0%, #FB7185 100%)",
    
    # Solid mappings for non-gradient elements
    "blue_solid":    "#3B82F6",
    "violet_solid":  "#8B5CF6",
    "emerald_solid": "#10B981",
    "sunset_solid":  "#F59E0B",
    "rose_solid":    "#F43F5E",
}

SCALES = {
    "small":  {"fs": "20px", "mw": "1000px"},
    "medium": {"fs": "24px", "mw": "1200px"},
    "large":  {"fs": "28px", "mw": "1400px"},
}

def build_css(theme_key="light", accent_key="blue", scale_key="medium", **_):
    t = THEMES.get(theme_key, THEMES["light"])
    a_grad = ACCENTS.get(accent_key, ACCENTS["blue"])
    a_solid = ACCENTS.get(f"{accent_key}_solid", "#3B82F6")
    s = SCALES.get(scale_key, SCALES["medium"])

    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Typography System ─────────────────────────────────────────── */
/* TARGET ONLY TEXT-BEARING ELEMENTS TO PREVENT ICON CORRUPTION */
html, body, p, li, input, button, textarea, select, .stMarkdown, .stText, .stCaption {{
    font-family: 'Inter', -apple-system, sans-serif !important;
    font-size: {s['fs']} !important;
    color: {t['text']} !important;
    line-height: 1.6 !important;
}}

/* Handle spans specifically to avoid breaking Material Icons/Ligatures */
span:not([class*="material"]):not([data-testid*="stIconMaterial"]):not([data-testid*="stExpanderToggleIcon"]):not([class*="icon"]):not(svg) {{
    font-family: 'Inter', sans-serif !important;
    font-size: inherit;
}}

/* PROTECTION FOR MATERIAL ICONS */
.material-icons, [class*="material-icons"], [data-testid="stIconMaterial"], [data-testid="stExpanderToggleIcon"] {{
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    font-size: inherit !important;
    color: inherit !important;
}}

h1 {{
    font-size: 64px !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    margin-bottom: 24px !important;
}}

h2 {{
    font-size: 44px !important;
    font-weight: 700 !important;
    margin-bottom: 20px !important;
}}

h3 {{
    font-size: 34px !important;
    font-weight: 600 !important;
}}

/* ── Layout ──────────────────────────────────────────────────── */
.stApp {{ background: {t['bg']} !important; }}
.block-container {{
    max-width: {s['mw']} !important;
    padding: 3rem 2.5rem 4rem !important;
}}

/* ── Sidebar ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{ 
    width: 400px !important; 
    background-color: {t['sidebar']} !important;
    border-right: 1px solid {t['border']} !important;
}}

/* Sidebar Content Protection */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    background-color: transparent !important;
}}

/* Radio / Navigation */
[data-testid="stSidebar"] .stRadio label {{
    color: {t['text']} !important;
    font-weight: 500 !important;
}}

/* Radio Selection Dot Color */
div[data-testid="stRadio"] label div[data-testid="stWidgetLabel"] + div div div:nth-child(1) {{
    border-color: {a_solid} !important;
}}

div[data-testid="stRadio"] label div[data-testid="stWidgetLabel"] + div div div:nth-child(1) div {{
    background-color: {a_solid} !important;
}}

/* Sidebar Selectbox Label */
[data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stExpander summary {{
    color: {t['text']} !important;
    font-weight: 600 !important;
}}

/* ── Cards ─────────────────────────────────────────────────────── */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {{
    background: {t['card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 20px !important;
    padding: 32px !important;
}}

/* ── Buttons ───────────────────────────────────────────────────── */
.stButton>button {{
    border-radius: 16px !important;
    font-weight: 700 !important;
    font-size: 24px !important;
    padding: 1.2rem 2.5rem !important;
    background-color: {t['card']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['border']} !important;
    transition: all 0.2s ease !important;
}}

.stButton>button:hover {{
    background-color: {t['hover']} !important;
    border-color: {a_solid} !important;
    color: {a_solid} !important;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.2) !important;
}}

/* Primary Buttons */
.stButton>button[kind="primary"] {{
    background: {a_grad} !important;
    color: white !important;
    border: none !important;
}}

/* ── Progress Bars ─────────────────────────────────────────────── */
div[data-testid="stProgress"] > div > div > div > div {{
    background: {a_grad} !important;
}}

/* ── Metrics ───────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {{ font-size: 56px !important; font-weight: 800 !important; color: {t['text']} !important; }}

/* ── Tabs (Subjects) ───────────────────────────────────────────── */
div[data-baseweb="tab-list"] {{
    gap: 60px !important;
    margin-bottom: 40px !important;
}}

div[data-baseweb="tab"] {{
    padding: 16px 32px !important;
    margin-right: 20px !important;
    color: {t['muted']} !important;
}}

div[data-baseweb="tab"][aria-selected="true"] {{
    color: {a_solid} !important;
    border-bottom-color: {a_solid} !important;
}}

/* ── FIX FOR OVERLAPPING / ICON TEXT LEAKAGE ───────────────────── */
[data-testid="stExpander"] summary span,
[data-testid="stPopover"] button span,
[data-testid="stBaseButton-secondary"] span,
[data-testid="stBaseButton-primary"] span {{
    font-size: {s['fs']} !important;
    overflow: hidden !important;
    text-overflow: clip !important;
    white-space: nowrap !important;
}}

/* ── Header Gradient Fix ───────────────────────────────────────── */
h1#welcome-to-cognix {{
    background: {a_grad};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* Ensure all markdown text respects theme color */
.stMarkdown div p {{
    color: {t['text']} !important;
}}

</style>"""
