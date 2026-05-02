import json
import re

def clean_response_text(text):
    """
    Strips instruction leaks, filters unrelated paragraphs, and enforces brevity.
    """
    if not text or not isinstance(text, str):
        return text

    # Phrases commonly leaked from model instructions or formatting
    forbidden_phrases = [
        "Answer a", "Provide", "Explain how", "For example",
        "Instruction", "### Instruction", "### Response",
        "Based on the", "The user wants", "Help the user"
    ]

    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Check for forbidden phrases
        if any(phrase in line for phrase in forbidden_phrases):
            continue
        
        # Remove empty lines or artifacts like "..." or "---"
        clean_line = line.strip()
        if clean_line and not re.match(r'^[\.\-\_\*]{2,}$', clean_line):
            cleaned_lines.append(clean_line)

    # Heuristic: Keep the first coherent block of text
    # (Models sometimes generate follow-up examples or unrelated text after a break)
    if not cleaned_lines:
        return ""

    # Length Control: Limit to 5-6 lines for crisp assistant-style responses
    # Higher limit if technical (e.g. contains code blocks), but here we follow the request.
    final_output = "\n".join(cleaned_lines[:6])
    
    return final_output.strip()

def process_response(response):
    """
    Antigravity Response Control Engine - v3.
    Strictly follows Jarvis stability and formatting rules.
    """
    
    # Rule 1: Validate input existence
    if not response or (isinstance(response, str) and response.strip() == ""):
        return "I didn't understand that. Please try again."

    # Rule 2: Handle Dictionary Type Directly
    if isinstance(response, dict):
        # Extract information message as priority
        info = response.get("information", {})
        if isinstance(info, dict):
            msg = info.get("message", "")
            if msg:
                print("[Antigravity] Text response extracted from 'information'")
                return clean_response_text(str(msg))
        
        # Check for direct 'response' or 'action' fallback
        if "response" in response:
            return clean_response_text(str(response["response"]))
        
        # If it's a structural dictionary (like router action), 
        # return as string for JSON router to handle, but this shouldn't go to TTS.
        return str(response)

    # Rule 3: Handle Internal Signals
    stripped_res = str(response).strip()
    if stripped_res == "sleep":
        return "sleep"

    # Rule 4: Logic for STRING (check if it's JSON that needs parsing)
    if stripped_res.startswith("{") and stripped_res.endswith("}"):
        try:
            data = json.loads(stripped_res)
            
            # Rule: Action Parsing Logic
            raw_action = data.get("action", "")
            
            # Extract intent for analysis
            action_str = ""
            if isinstance(raw_action, dict):
                action_str = str(raw_action.get("intent", "")).lower()
            else:
                action_str = str(raw_action).lower()

            # Rule: Conversion Output (Priority: Information/Message)
            info = data.get("information", {})
            msg = info.get("message", "")
            
            # Only treat as action if it's NOT an 'inform' action
            if action_str == "inform" or msg:
                if msg:
                    print("[Antigravity] Text response returned")
                    return clean_response_text(str(msg))
            
            # Compatibility path: response["response"]
            if "response" in data:
                print("[Antigravity] Text response returned")
                return clean_response_text(str(data["response"]))

            # If it reached here, it's a REAL action intended for the router
            return stripped_res

        except Exception as e:
            print(f"Response parsing fallback used: {e}")
            # Rule: Return original response safely if parsing fails
            return stripped_res

    # Rule 5: Default to plain text
    print("[Antigravity] Text response returned")
    return clean_response_text(stripped_res)
