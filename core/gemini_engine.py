import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API key and model from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest")

# Initialize Gemini Client
client = genai.Client(api_key=API_KEY)

# History for conversational continuity
gemini_history = []

def ask_gemini(command, image_data=None):
    """
    Stage 2 Intelligence: Performs high-power conversational reasoning.
    Supports multimodal input (text + images).
    """
    global gemini_history
    
    try:
        contents = []
        if command:
            contents.append(command)
        
        if image_data:
            contents.append(types.Part.from_bytes(data=image_data, mime_type="image/jpeg"))

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )
        
        reply = response.text.strip()
        
        # Update history (optional)
        gemini_history.append({"user": str(command), "cognix": reply})
        if len(gemini_history) > 10:
            gemini_history.pop(0)
            
        return reply

    except Exception as e:
        print(f"Gemini Error: {e}")
        # Raise so Stage 1 fallback can trigger in the router
        raise RuntimeError(f"Stage 2 Failed: {str(e)}")
