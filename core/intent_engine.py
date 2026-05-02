from core.brain import ask_ai
import json

def detect_intent(command):
    """
    Uses the Brain to detect intent.
    Returns the JSON string from the Brain if it's an action, 
    otherwise returns 'AI' to signal a conversation.
    """
    response = ask_ai(command)
    
    # Check if response is a JSON action
    if response.strip().startswith("{") and "intent" in response:
        try:
            # We return the raw JSON string (or we could return the dict)
            # For compatibility with the new router, we'll return the JSON string.
            return response
        except:
            pass
            
    # Default to AI conversation
    return "AI"
