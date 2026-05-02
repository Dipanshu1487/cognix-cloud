def handle_error(error):
    """Classify the error based on its message."""
    error_msg = str(error).lower()
    
    if "timeout" in error_msg:
        return "TIMEOUT"
    elif "nosuchelement" in error_msg or "not found" in error_msg:
        return "ELEMENT_NOT_FOUND"
    elif "disconnected" in error_msg or "refused" in error_msg or "unreachable" in error_msg:
        return "DRIVER_DISCONNECTED"
    elif "stale" in error_msg:
        return "STALE_ELEMENT"
        
    return "UNKNOWN"
