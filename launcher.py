import sys
import psutil
import getpass
import subprocess
import time
import os

# Set your secure password here
PASSWORD = os.getenv("LAUNCHER_PASS", "admin")
MAX_ATTEMPTS = 3

def clear_screen():
    """Clears the console screen for a clean UI."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Displays a clean and modern ASCII banner."""
    print("╔══════════════════════════════════════════════════╗")
    print("║                                                  ║")
    print("║             cogniX SECURITY SYSTEM               ║")
    print("║             v2.0 - SECURE LAUNCHER               ║")
    print("║                                                  ║")
    print("╚══════════════════════════════════════════════════╝")

def is_cognix_running():
    """
    Specifically detects whether kelly.py is running.
    Uses psutil to iterate processes and checks command lines.
    """
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.cmdline()
            # cmdline is typically a list of arguments
            if cmdline:
                cmd_str = ' '.join(cmdline).lower()
                # Check if it's a python process, running tightly bound to kelly.py
                if "python" in proc.info['name'].lower():
                    if "kelly.py" in cmd_str and "launcher.py" not in cmd_str:
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def main():
    clear_screen()
    print_banner()
    
    print("[SYSTEM] Initializing process diagnostics...")
    time.sleep(0.5)
    
    # Check if cogniX is already running; skip password if active.
    if is_cognix_running():
        print("\n[+] STATUS: cogniX ACTIVE")
        print("[+] Session verified. Bypassing authentication protocols...")
        sys.exit(0)
    
    print("\n[-] STATUS: SYSTEM LOCKED")
    print("[-] Authentication required to proceed.\n")

    # Ask for password; allow only 3 attempts
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        # Hide password while typing using getpass
        pwd = getpass.getpass(f"Enter Password (Attempt {attempts + 1}/{MAX_ATTEMPTS}): ")
        
        if pwd == PASSWORD:
            print("\n[✔] ACCESS GRANTED.")
            print("[*] Launching cogniX Core Systems (kelly.py)...\n")
            time.sleep(0.5)
            
            # Launch kelly.py safely
            try:
                subprocess.run([sys.executable, "kelly.py"])
            except KeyboardInterrupt:
                print("\n[!] System interrupted by user.")
            except Exception as e:
                print(f"\n[X] CRITICAL ERROR: Could not start kelly.py. Details: {e}")
            sys.exit(0)
        else:
            attempts += 1
            print("[X] ACCESS DENIED. Incorrect password.\n")
    
    # Deny access after failed attempts
    if attempts >= MAX_ATTEMPTS:
        print("[!] SECURITY ALERT: Maximum authentication attempts exceeded.")
        print("[!] Initiating lockdown module. Terminating launcher...")
        sys.exit(1)

if __name__ == "__main__":
    main()
