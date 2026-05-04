
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
    # Flexible search for the environment - prioritizing CUDA-ready 3.12 env
    python_exe = sys.executable # Default fallback
    env_paths = ["jarvis_env_312/Scripts/python.exe", "jarvis_env/Scripts/python.exe", "venv/Scripts/python.exe"]
    
    selected_env = "Global"
    for p in env_paths:
        abs_p = os.path.abspath(p)
        if os.path.exists(abs_p):
            python_exe = abs_p
            selected_env = p
            break
    
    print(f"[SYSTEM] Using environment: {selected_env}")
    
    # Verify CUDA in selected environment
    try:
        import torch
        if torch.cuda.is_available():
            print(f"[GPU] SUCCESS: CUDA is enabled. Using {torch.cuda.get_device_name(0)}")
        else:
            print("[GPU] WARNING: Running on CPU. Performance will be slow.")
    except:
        pass

    try:
        # Step 1: Start FastAPI backend
        print("[SYSTEM] Starting cogniX Backend...")
        backend_cmd = f'"{python_exe}" -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload'
        backend_proc = subprocess.Popen(backend_cmd, shell=True)
        processes.append(backend_proc)
        print("[SYSTEM] Backend initializing...")

        # Step 2: Smart Wait for Backend (Polling /health)
        print("[SYSTEM] Initializing Academic Brain (LoRA)...")
        import requests
        max_retries = 30 # 30 retries * 2s = 60 seconds max wait
        backend_online = False
        
        for i in range(max_retries):
            try:
                res = requests.get("http://127.0.0.1:8000/health", timeout=1)
                if res.status_code == 200:
                    print(f"\n[SYSTEM] Brain Online! (Verified in {i*2}s)")
                    backend_online = True
                    break
            except:
                pass
            
            print(".", end="", flush=True) # Progress dots
            time.sleep(2)
            
        if not backend_online:
            print("\n[ERROR] Brain failed to initialize in time. UI will start in restricted mode.")

        # Step 3: Start Streamlit UI
        print("\n[SYSTEM] Launching Chat UI with Hot-Reloading...")
        ui_cmd = f'"{python_exe}" -m streamlit run app.py --server.runOnSave true'
        ui_proc = subprocess.Popen(ui_cmd, shell=True)
        processes.append(ui_proc)
        print("[SYSTEM] UI running on http://localhost:8501")
        print("[SYSTEM] HOT-RELOADING ACTIVE: Any code changes will reflect instantly!")

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
