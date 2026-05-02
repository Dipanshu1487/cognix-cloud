
import subprocess
import time
import sys
import signal
import os

def main():
    """
    Unified cogniX Launcher - Antigravity Edition.
    Starts both Backend and Frontend in parallel using the local virtual environment.
    """
    processes = []

    print("\n" + "="*40)
    print("   cogniX FRAMEWORK UNIFIED LAUNCHER   ")
    print("="*40 + "\n")

    # Environment Path Setup
    # Force use of jarvis_env_312 to prevent "command not found" errors
    python_exe = os.path.abspath("jarvis_env_312/Scripts/python.exe")
    
    if not os.path.exists(python_exe):
        print(f"[ERROR] Virtual environment not found at {python_exe}")
        print("Please ensure jarvis_env_312 exists in the project root.")
        return

    try:
        # Step 1: Start FastAPI backend
        print("[SYSTEM] Starting cogniX Backend...")
        # Use absolute python path to run uvicorn as a module
        backend_cmd = f'"{python_exe}" -m uvicorn api.server:app --host 127.0.0.1 --port 8000 --reload'
        backend_proc = subprocess.Popen(backend_cmd, shell=True)
        processes.append(backend_proc)
        print("[SYSTEM] Backend initializing...")

        # Step 2: Wait 7-10 seconds for LoRA/Model stabilization
        # Heavy models like Phi-2 with LoRA adapters need more time to load into VRAM
        print("[SYSTEM] Loading Academic Brain (LoRA)... please hold...")
        time.sleep(8)

        # Step 3: Start Streamlit UI
        print("\n[SYSTEM] Launching Chat UI...")
        ui_cmd = f'"{python_exe}" -m streamlit run ui/app.py'
        ui_proc = subprocess.Popen(ui_cmd, shell=True)
        processes.append(ui_proc)
        print("[SYSTEM] UI running on http://localhost:8501")

        # Monitor Processes
        while True:
            # Check backend
            if backend_proc.poll() is not None:
                print(f"[ERROR] cogniX Backend crashed! Exit Code: {backend_proc.returncode}")
                break
                
            # Check UI
            if ui_proc.poll() is not None:
                print(f"[ERROR] Chat UI crashed! Exit Code: {ui_proc.returncode}")
                break
                
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[SYSTEM] Interrupted by user. Shutting down...")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
    finally:
        # Graceful Termination
        print("[SYSTEM] Terminating services...")
        for proc in processes:
            if proc.poll() is None: # Still running
                # On Windows, taskkill is sometimes cleaner for shell=True processes
                if os.name == 'nt':
                    subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
                else:
                    proc.terminate()
        
        print("[SYSTEM] Shutdown complete. All processes stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
