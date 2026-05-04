
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

app = FastAPI(title="cogniX AI API", description="Modular API layer for the cogniX Assistant Framework")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cogniXAPI")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

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
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail="Internal system error in cogniX brain.")

@app.get("/health")
async def health_check():
    return {"status": "operational", "version": "3.1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
