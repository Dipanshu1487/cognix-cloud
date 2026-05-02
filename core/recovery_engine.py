import time
from core.error_handler import handle_error
from core.error_logger import log_error

def recover(error_type, action_func, restart_func=None, init_func=None, max_retries=2):
    """
    Attempts to recover from an error by retrying the action or restarting the driver.
    """
    print(f"[RECOVERY] Attempting recovery for error type: {error_type}")
    
    for attempt in range(max_retries):
        if error_type == "DRIVER_DISCONNECTED":
            print("[RECOVERY] Restarting driver...")
            if restart_func:
                restart_func()
            if init_func:
                init_func()
        else:
            print(f"[RECOVERY] Retrying action (Attempt {attempt + 1}/{max_retries})...")
            time.sleep(2)
            
        try:
            return action_func()
        except Exception as e:
            log_error(e, context=f"recovery_attempt_{attempt + 1}")
            error_type = handle_error(e)
            
    print("[RECOVERY] Recovery failed after max retries.")
    return False
