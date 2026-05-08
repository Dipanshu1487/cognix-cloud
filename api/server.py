
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import sys
import os

# Add the project root to sys.path to allow imports from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Environment Enforcement
def verify_environment():
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    executable = sys.executable.lower()
    is_correct_version = version in ["3.11", "3.12"]
    # Relax environment name check for cloud deployment
    is_correct_env = "jarvis_env" in executable or "jarvis_env" in sys.prefix.lower() or os.getenv("STREAMLIT_RUNTIME_CHECK") == "true"
    
    if not is_correct_version:
        print(f"\n[SECURITY] Wrong Python version detected: {version}")
        print("[SECURITY] cogniX requires Python 3.11 or 3.12\n")
        return False
    
    print(f"\n[SUCCESS] Environment verified (Python {version})")
    return True

# Initialize Brain/LoRA check (already handled in brain.py but we can verify here too)
env_stable = verify_environment()

from core.brain import process_query

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="cogniX AI API", description="Modular API layer for the cogniX Assistant Framework")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cogniXAPI")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.get("/health")
async def health_check():
    import torch
    hw = f"GPU: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU Mode"
    return {
        "status": "online", 
        "environment": sys.version.split()[0],
        "hardware": hw
    }

import traceback

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """
    Exposes cogniX intelligence as a service.
    Routes incoming queries through the brain and router pipeline.
    """
    logger.info(f"Incoming query: {request.query}")
    
    try:
        # Process the query using the existing unified pipeline
        answer = process_query(request.query)
        logger.info(f"Brain Result: {answer}")
        
        if not answer:
            logger.warning("Brain returned empty/None result.")
            return QueryResponse(response="I encountered an issue processing that request, sir.")
            
        return QueryResponse(response=str(answer))
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        logger.error(traceback.format_exc())
        # Return graceful message instead of crashing with 500 if possible, 
        # but the task asks to fix the 500 error and provide proper exception handling.
        raise HTTPException(status_code=500, detail=f"Internal system error: {str(e)}")

@app.get("/health")
async def health_check():
    import torch
    hw = f"GPU: {torch.cuda.get_device_name(0)}" if torch.cuda.is_available() else "CPU Mode"
    return {"status": "operational", "version": "3.1", "hardware": hw}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
