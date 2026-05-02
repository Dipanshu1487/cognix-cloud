import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/system_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_error(error, context=""):
    """Log the error to a file and print to console."""
    message = f"[{context}] {str(error)}"
    logging.error(message)
    print(f"[ERROR] {message}")
