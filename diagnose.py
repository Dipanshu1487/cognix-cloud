import os, sqlite3, sys, traceback
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("   cogniX FULL SYSTEM DIAGNOSTIC v2.0")
print("="*60)

PASS = "[  OK  ]"
WARN = "[ WARN ]"
FAIL = "[ FAIL ]"

# -- 1. PYTHON ENVIRONMENT
print("\n" + "-"*60)
print("[1] PYTHON ENVIRONMENT")
print("-"*60)
print(f"  Version   : {sys.version.split()[0]}")
print(f"  Executable: {sys.executable}")
env_312 = os.path.abspath("jarvis_env_312/Scripts/python.exe")
if os.path.exists(env_312):
    print(f"  {PASS} jarvis_env_312 found (GPU-ready environment)")
else:
    print(f"  {WARN} jarvis_env_312 NOT found - running in global env")

# -- 2. GPU / CUDA
print("\n" + "-"*60)
print("[2] GPU / CUDA STATUS")
print("-"*60)
try:
    import torch
    cuda = torch.cuda.is_available()
    torch_ver = torch.__version__
    if cuda:
        print(f"  {PASS} CUDA AVAILABLE: {torch.cuda.get_device_name(0)}")
        total = torch.cuda.get_device_properties(0).total_memory // 1024**2
        allocated = torch.cuda.memory_allocated(0) // 1024**2
        print(f"       VRAM Total : {total} MB")
        print(f"       VRAM Free  : {total - allocated} MB")
    else:
        print(f"  {FAIL} CUDA NOT AVAILABLE - LoRA Brain will be slow (CPU mode)")
    print(f"       Torch     : {torch_ver}")
    if "+cpu" in torch_ver:
        print(f"  {WARN} CPU-only PyTorch in current env! Activate jarvis_env_312 for GPU.")
except Exception as e:
    print(f"  {FAIL} PyTorch import error: {e}")

# -- 3. DATABASE
print("\n" + "-"*60)
print("[3] DATABASE")
print("-"*60)
for db in ['cognix.db', 'jarvis.db']:
    if os.path.exists(db):
        try:
            conn = sqlite3.connect(db)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            conn.close()
            print(f"  {PASS} {db} ({len(tables)} tables)")
        except Exception as e:
            print(f"  {FAIL} {db}: {e}")
    else:
        print(f"  {FAIL} {db}: NOT FOUND")

# -- 4. AI MODEL PATHS
print("\n" + "-"*60)
print("[4] AI MODEL PATHS")
print("-"*60)
paths = {
    "Base Model (phi2)": r"E:\phi2_repo",
    "LoRA Adapter"     : r"E:\jarvis_lora_results\final_adapter",
}
for name, path in paths.items():
    if os.path.exists(path):
        files = os.listdir(path)
        print(f"  {PASS} {name}: {path} ({len(files)} files)")
    else:
        print(f"  {FAIL} {name}: NOT FOUND at {path}")

# -- 5. CORE MODULE IMPORTS
print("\n" + "-"*60)
print("[5] CORE MODULE IMPORTS")
print("-"*60)
modules = [
    ("core.gemini_engine", "ask_gemini"),
    ("core.voice",         "speak"),
    ("core.listener",      "listen"),
    ("upload.db",          "init_db"),
    ("memory.student_intelligence", "StudentIntelligenceSystem"),
    ("ui.chat",            "render_chat"),
    ("ui.dashboard",       "render_dashboard"),
    ("ui.profile_page",    "render_profile_page"),
    ("ui.study_page",      "render_study_page"),
    ("ui.practice_page",   "render_practice_page"),
]
for mod, fn in modules:
    try:
        m = __import__(mod, fromlist=[fn])
        getattr(m, fn)
        print(f"  {PASS} {mod}.{fn}")
    except Exception as e:
        print(f"  {FAIL} {mod}.{fn} -> {e}")

# -- 6. BACKEND SERVER
print("\n" + "-"*60)
print("[6] BACKEND SERVER")
print("-"*60)
try:
    import requests
    r = requests.get("http://127.0.0.1:8000/health", timeout=2)
    data = r.json()
    print(f"  {PASS} Backend ONLINE")
    print(f"       Status  : {data.get('status')}")
    print(f"       Hardware: {data.get('hardware', 'N/A')}")
    print(f"       Python  : {data.get('environment', 'N/A')}")
except requests.exceptions.ConnectionError:
    print(f"  {FAIL} Backend OFFLINE - Run 'python run_all.py' to start")
except Exception as e:
    print(f"  {FAIL} Backend Error: {e}")

# -- 7. ENV / API KEYS
print("\n" + "-"*60)
print("[7] ENVIRONMENT KEYS (.env)")
print("-"*60)
from dotenv import load_dotenv
load_dotenv()
keys = {
    "GEMINI_API_KEY"      : os.getenv("GEMINI_API_KEY", ""),
    "GMAIL_USER"          : os.getenv("GMAIL_USER", ""),
    "GMAIL_PASS"          : os.getenv("GMAIL_PASS", ""),
    "PICOVOICE_ACCESS_KEY": os.getenv("PICOVOICE_ACCESS_KEY", ""),
}
for k, v in keys.items():
    if not v:
        print(f"  {FAIL} {k}: MISSING")
    elif "your_" in v:
        print(f"  {WARN} {k}: PLACEHOLDER - not configured")
    else:
        print(f"  {PASS} {k}: SET")

# -- 8. CRITICAL FILES
print("\n" + "-"*60)
print("[8] CRITICAL FILES CHECK")
print("-"*60)
files = ["app.py", "run_all.py", "requirements.txt", "runtime.txt",
         ".env", "api/server.py", "core/brain.py", "core/gemini_engine.py",
         "ui/chat.py", "ui/dashboard.py", "ui/profile_page.py"]
for f in files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"  {PASS} {f} ({size:,} bytes)")
    else:
        print(f"  {FAIL} {f}: MISSING")

print("\n" + "="*60)
print("   DIAGNOSTIC COMPLETE")
print("="*60 + "\n")
