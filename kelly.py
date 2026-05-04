import os
import sys

# --- ENVIRONMENT GUARD (STRICT) --- #
# Must be at the very top to prevent any library initialization in wrong env
def _verify_environment():
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    executable = sys.executable.lower()
    
    is_correct_version = version in ["3.11", "3.12"]
    is_correct_env = "jarvis_env" in executable or "jarvis_env" in sys.prefix.lower() or os.getenv("STREAMLIT_RUNTIME_CHECK") == "true"
    
    if not is_correct_version:
        print(f"\n[BLOCK] Incorrect environment blocked")
        print(f"Error: cogniX requires Python 3.11 or 3.12 (Detected: {version}).")
        sys.exit(1)
    
    print(f"[Antigravity] Environment verified (Python {version})")

_verify_environment()
# --------------------------------- #

import warnings

# Suppress annoying console warnings before initializing libraries
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
warnings.filterwarnings("ignore", category=UserWarning)

from core.voice import speak, stop_speaking, wait_until_done
from core.listener import listen
from core.wake_word import detector
from core.router import route_command
from automation.reminder_scheduler import run_scheduler
import threading
# -------- STARTUP -------- #

speak("cogniX online. All systems operational.")

threading.Thread(target=run_scheduler, daemon=True).start()

import time

# -------- MAIN LOOP -------- #

active_mode = False
last_interaction = 0
last_topic = ""
consecutive_silence = 0  # track silent loops to avoid tight spin
MIC_BLEED_DELAY = 1.5   # seconds to wait after TTS ends before re-opening mic


while True:
    command = ""
    
    if not active_mode:
        # Runs in background thread, allowing system to stay responsive
        detector.start()
        detected_input = detector.wait_for_wake_word()
        detector.stop()  # Stop listening once detected to free resources for Whisper
        
        print("Session started")
        speak("Yes sir")
        active_mode = True
        last_interaction = time.time()
        time.sleep(1)
        
        # Check if the user said a command directly after the wake word
        if isinstance(detected_input, str):
            clean_cmd = detected_input.lower().replace("cognix", "").strip()
            # Remove punctuation from empty straggling trails
            for p in [".", ",", "!", "?"]:
                clean_cmd = clean_cmd.replace(p, "")
            clean_cmd = clean_cmd.strip()
            
            if len(clean_cmd) > 2:
                command = clean_cmd

    if not command:
        # Inactivity timeout (30 seconds)
        if time.time() - last_interaction > 30:
            print("Session ended. Waiting for wake word.")
            active_mode = False
            continue

        # Listen for command
        print("Active listening")
        command = listen()

    if not command:
        consecutive_silence += 1
        # Progressive back-off: 1s, then 2s after 3 consecutive silences
        time.sleep(1 if consecutive_silence < 3 else 2)
        continue

    consecutive_silence = 0  # reset on real speech

    command = command.strip().lower()

    # 1. Top-Priority Interrupt (Immediate)
    if any(x in command for x in ["stop", "shut up", "quiet", "go to sleep", "bye cognix"]):
        stop_speaking()
        print("Session ended. Waiting for wake word.")
        active_mode = False
        speak("Going to sleep.")
        continue

    # 2. Contextual Enrichment (Follow-ups using last_topic)
    if last_topic:
        if any(x in command for x in ["tell me more", "elaborate", "details", "life journey", "journey"]):
            command = f"tell me more about {last_topic}"
    
    # 3. Simple Topic Extraction
    if "tell me about" in command:
        last_topic = command.split("tell me about")[-1].strip()
    elif "who is" in command:
        last_topic = command.split("who is")[-1].strip()
    elif "what is" in command:
        last_topic = command.split("what is")[-1].strip()

    # Reset timer on valid speech
    last_interaction = time.time()

    # Exit commands (Fallback just in case it didn't trigger above)
    if command in ["sleep", "go to sleep", "stop listening", "bye cognix", "stop"]:
        print("Session ended. Waiting for wake word.")
        speak("Going to sleep.")
        active_mode = False
        continue

    # Noise filtering
    is_noise = command in {"you", "ok", "okay", "hmm", "yes"} or (
        len(command) < 4 and command not in {"play", "stop", "next", "back", "open", "close"}
    )
    if is_noise:
        continue

    # Execute and Route
    print("[DEBUG] Processing started")
    print("[DEBUG] AI call started")
    
    response = None
    import concurrent.futures
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(route_command, command)
            # Enforce 10s maximum wait block
            response = future.result(timeout=10)
            print("[DEBUG] AI response received")
    except concurrent.futures.TimeoutError:
        print("[DEBUG] Fallback triggered")
        response = "I am having trouble processing that. Please try again."
    except Exception as e:
        print(f"[DEBUG] System error during AI call: {e}")
        response = "I am having trouble processing that. Please try again."

    if response == "sleep":
        stop_speaking()
        speak("Going to sleep.")
        active_mode = False
        continue

    elif response:
        speak(response)
        # Wait for TTS to FULLY finish, then add mic-bleed buffer
        wait_until_done()
        time.sleep(MIC_BLEED_DELAY)
        # Reset timer after response
        last_interaction = time.time()