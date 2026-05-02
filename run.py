"""
cogniX - UNIFIED BACKEND RUNNER
Single file to start everything

Usage:
    python run.py              - Normal launch (with auth)
    python run.py --no-auth    - Skip password prompt
    python run.py --status     - Check if cogniX is running
    python run.py --kill       - Kill any running cogniX process
"""

import sys
import os
import warnings

# Suppress noisy warnings before any library loads
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Force UTF-8 output on Windows to avoid encoding crashes
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

import time
import getpass
import subprocess
import importlib
import argparse

# --- Configuration -----------------------------------------------------------

PASSWORD = os.getenv("LAUNCHER_PASS", "admin")
MAX_ATTEMPTS = 3
KELLY_SCRIPT = "kelly.py"

# All required packages: (import_name, pip_name)
REQUIRED_PACKAGES = [
    ("psutil",              "psutil"),
    ("faster_whisper",      "faster-whisper"),
    ("sounddevice",         "sounddevice"),
    ("scipy",               "scipy"),
    ("numpy",               "numpy"),
    ("pvporcupine",         "pvporcupine"),
    ("pyaudio",             "PyAudio"),
    ("edge_tts",            "edge-tts"),
    ("pygame",              "pygame"),
    ("ollama",              "ollama"),
    ("selenium",            "selenium"),
    ("webdriver_manager",   "webdriver-manager"),
    ("pycaw",               "pycaw"),
    ("comtypes",            "comtypes"),
    ("schedule",            "schedule"),
    ("duckduckgo_search",   "duckduckgo-search"),
    ("transformers",        "transformers"),
    ("peft",                "peft"),
    ("accelerate",          "accelerate"),
    ("bitsandbytes",        "bitsandbytes"),
    ("google.genai",        "google-genai"),
    ("dotenv",              "python-dotenv"),
]

# --- Utilities ---------------------------------------------------------------

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print()
    print("  +====================================================+")
    print("  |                                                      |")
    print("  |       ___  ___  ____  _  _  ____  ____               |")
    print(r"  |      (_  )(   )(  _ \( \/ )(_  _)/ ___)              |")
    print(r"  |       / /  ) (  )   / \  /  _)(_ \___ \              |")
    print(r"  |      (_/  (___)(_)\_)  \/  (____)(____/              |")
    print("  |                                                      |")
    print("  |            UNIFIED BACKEND RUNNER v3.1 (cogniX)  |")
    print("  |                                                      |")
    print("  +====================================================+")
    print()

def log(icon, msg):
    print(f"  [{icon}] {msg}")

def check_dependencies(python_exe):
    """Verify all required packages are installed in the target environment."""
    log("~", "Checking environment dependencies... (Please wait)")
    
    # Run a single fast subprocess to test all imports at once
    import_names = [imp for imp, _ in REQUIRED_PACKAGES]
    pip_map = {imp: pip for imp, pip in REQUIRED_PACKAGES}
    missing = []
    
    checker_script = """
import sys
import importlib.util

missing = []
for pkg in sys.argv[1:]:
    spec = importlib.util.find_spec(pkg)
    if spec is None:
        missing.append(pkg)
if missing:
    print(','.join(missing))
"""
    try:
        cmd = [python_exe, "-c", checker_script] + import_names
        result = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        missing_imports = result.strip().split(',') if result.strip() else []
        for imp in missing_imports:
            missing.append((imp, pip_map[imp]))
    except Exception as e:
        log("X", "Failed to run dependency check script.")
        # Fallback check
        for import_name, pip_name in REQUIRED_PACKAGES:
            try:
                fb_cmd = f"import importlib.util; import sys; sys.exit(0 if importlib.util.find_spec('{import_name}') else 1)"
                subprocess.check_call([python_exe, "-c", fb_cmd], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                missing.append((import_name, pip_name))

    if not missing:
        log("+", "All dependencies satisfied.")
        return True

    log("!", f"Missing {len(missing)} package(s) in environment.")
    for imp, pip in missing:
        print(f"       - {pip}")
    print()

    # Rule: Never attempt to auto-fix environment
    log("X", "Auto-installation disabled. Please manually install missing requirements.")
    return False

# --- Process Management ------------------------------------------------------

def get_cognix_processes():
    """Return list of (pid, cmdline) for running kelly.py processes."""
    try:
        import psutil
    except ImportError:
        # If psutil isn't in the global env, we can't easily check from here 
        # unless we use the venv python, but for now we fallback gracefully.
        return []
        
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.cmdline()
            if cmdline:
                cmd_str = ' '.join(cmdline).lower()
                if "python" in proc.info['name'].lower():
                    if "kelly.py" in cmd_str and "run.py" not in cmd_str:
                        processes.append((proc.pid, ' '.join(cmdline)))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def is_cognix_running():
    return len(get_cognix_processes()) > 0

def kill_cognix():
    """Terminate all running Jarvis (kelly.py) processes."""
    try:
        import psutil
    except ImportError:
        log("X", "Cannot kill: psutil not installed in caller environment.")
        return
        
    procs = get_cognix_processes()
    if not procs:
        log("-", "No Jarvis process found.")
        return
    for pid, cmd in procs:
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=5)
            log("+", f"Terminated PID {pid}")
        except Exception as e:
            log("X", f"Failed to kill PID {pid}: {e}")

def show_status():
    """Display current Jarvis process status."""
    procs = get_cognix_processes()
    if procs:
        log("+", "cogniX IS RUNNING")
        for pid, cmd in procs:
            print(f"       PID {pid}: {cmd}")
    else:
        log("-", "Jarvis is NOT running.")

# --- Authentication ----------------------------------------------------------

def authenticate():
    """Prompt for password. Returns True if authenticated."""
    if is_cognix_running():
        log("+", "cogniX already running -- session verified, skipping auth.")
        return True

    log("LOCKED", "System locked. Authentication required.\n")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            pwd = getpass.getpass(f"  Enter Password ({attempt}/{MAX_ATTEMPTS}): ")
            if pwd == PASSWORD:
                print()
                log("+", "ACCESS GRANTED")
                return True
            else:
                log("X", "Incorrect password.\n")
        except EOFError:
            return False

    log("!!", "Maximum attempts exceeded. Access denied.")
    return False

# --- Launch ------------------------------------------------------------------

def launch_kelly(python_exe):
    """Launch kelly.py as the main cogniX process."""
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), KELLY_SCRIPT)

    if not os.path.exists(script):
        log("X", f"Cannot find {KELLY_SCRIPT} at: {script}")
        return

    if is_jarvis_running():
        log("!", "Jarvis is already running. Use --kill first to restart.")
        return

    log("*", f"Launching cogniX via: {python_exe}")
    print("  " + "-" * 50)
    print()

    try:
        # Run kelly.py in the project directory so relative imports work
        project_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(
            [python_exe, script],
            cwd=project_dir,
        )
    except KeyboardInterrupt:
        print("\n")
        log("!", "Interrupted by user. Jarvis shutting down.")
    except Exception as e:
        log("X", f"CRITICAL ERROR: {e}")

# --- CLI ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Jarvis Unified Backend Runner")
    parser.add_argument("--no-auth", action="store_true", help="Skip password authentication")
    parser.add_argument("--status", action="store_true", help="Check if Jarvis is running")
    parser.add_argument("--kill", action="store_true", help="Kill running Jarvis processes")
    args = parser.parse_args()

    clear()
    banner()

    # -- Venv detection (STRICT: jarvis_env_312) --
    venv_python = os.path.join(os.getcwd(), "jarvis_env_312", "Scripts", "python.exe")
    
    if os.path.exists(venv_python):
        # 1. Verify Version (Python 3.12)
        try:
            version_check = subprocess.check_output([venv_python, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], text=True).strip()
            if version_check == "3.12":
                python_exe = venv_python
                log("VENV", "Correct environment detected (jarvis_env_312)")
            else:
                log("BLOCK", f"Incorrect environment blocked: {version_check} (Expected 3.12)")
                print(f"\n  Error: Incorrect environment detected. Please activate 'jarvis_env_312' (Python 3.12).")
                sys.exit(1)
        except Exception as e:
            log("X", f"Failed to verify environment: {e}")
            sys.exit(1)
    else:
        log("BLOCK", "Incorrect environment blocked: 'jarvis_env_312' not found")
        print(f"\n  Error: Incorrect environment detected. Please activate 'jarvis_env_312' (Python 3.12).")
        sys.exit(1)

    # 1. ALWAYS check dependencies first
    if not check_dependencies(python_exe):
        sys.exit(1)
    print()

    # -- Status check mode --
    if args.status:
        show_status()
        return

    # -- Kill mode --
    if args.kill:
        kill_jarvis()
        return

    # -- Normal launch flow --
    log("~", "Running pre-flight checks...")
    time.sleep(0.3)

    # 2. Authenticate (unless --no-auth)
    if not args.no_auth:
        if not authenticate():
            sys.exit(1)
    else:
        log("!", "Authentication skipped (--no-auth flag)")
    print()

    # 3. Launch
    launch_kelly(python_exe)

if __name__ == "__main__":
    main()
