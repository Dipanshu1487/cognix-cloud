import os
import sqlite3

# Method 1: Relative (ui/auth.py style)
rel_path = os.path.abspath("cognix.db")

# Method 2: Absolute (upload/db.py style)
def get_upload_db_path():
    # Simulate being in e:\Ai\jarvis\upload\db.py
    simulated_file = os.path.abspath("upload/db.py")
    return os.path.join(os.path.dirname(os.path.dirname(simulated_file)), 'cognix.db')

abs_path = get_upload_db_path()

print(f"Relative Path (Current CWD): {rel_path}")
print(f"Absolute Path (File based): {abs_path}")
print(f"CWD: {os.getcwd()}")
print(f"Match: {rel_path == abs_path}")

# Check if they exist
print(f"Rel Exists: {os.path.exists(rel_path)}")
print(f"Abs Exists: {os.path.exists(abs_path)}")
