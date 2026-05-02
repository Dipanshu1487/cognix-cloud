import sys
import os

# Force UTF-8 output on Windows to avoid encoding crashes
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

# Add current directory to path
sys.path.append(os.path.abspath(os.curdir))

from core.router import route_command

def test(command):
    print(f"\n[USER] {command}")
    res = route_command(command)
    print(f"[JARVIS] {res}")

print("--- TESTING REMINDER INTENT ---")
test("remind me to call Dipanshu at 18:00")

print("\n--- TESTING SILENT FALLBACK (GEMINI -> PHI3) ---")
# This should fail Stage 2 (Quota) and fallback to Stage 1 (Phi3) silently
test_commands = [
        "remind me to call Dipanshu at 18:00",
        "Who is Elon Musk?",
        "Tell me a short joke about AI.",
        "Who created you?",
        "Go to sleep mode.",
        "What is (25 * 4) + 50?",
        "Solve the derivative of x squared.",
        "Plan 4 hours of study for Physics and History."
    ]
test("Who is Elon Musk?")
test("Tell me a short joke about AI.")

print("\n--- TESTING IDENTITY ---")
test("Who created you?")
