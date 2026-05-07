import os
import re

def scan_connections(directory):
    results = []
    # Regex for sqlite3.connect and the variable/string inside
    connect_re = re.compile(r'sqlite3\.connect\(([^)]+)\)')
    
    for root, dirs, files in os.walk(directory):
        if any(x in root for x in ['jarvis_env', '__pycache__', '.git', 'assets', 'scratch']):
            continue
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            match = connect_re.search(line)
                            if match:
                                db_ref = match.group(1).strip()
                                results.append({
                                    "file": path,
                                    "line": i + 1,
                                    "db_ref": db_ref,
                                    "method": "sqlite3.connect"
                                })
                except Exception as e:
                    pass
    return results

if __name__ == "__main__":
    connections = scan_connections('.')
    print(f"{'FILE PATH':<50} | {'LINE':<5} | {'DB REFERENCE':<20}")
    print("-" * 80)
    for c in connections:
        print(f"{c['file']:<50} | {c['line']:<5} | {c['db_ref']:<20}")
