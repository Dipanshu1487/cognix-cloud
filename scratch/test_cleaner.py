
import json
import re

def clean_dataset_test(raw_dataset):
    cleaned = []
    code_indicators = [r"\{", r"\}", r";", r"def ", r"class ", r"import ", r"int ", r"float ", r"\("]
    
    for entry in raw_dataset:
        instruction = entry.get("instruction", "").strip()
        output = entry.get("output", "").strip()
        
        if not instruction or not output:
             continue
             
        # Broken Sentence / Minimum 2 sentences
        sentences = re.split(r'[.!?]+', output)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 2:
            continue
            
        # Random Tokens / Symbols Check
        if re.search(r'[^a-zA-Z0-9\s,.?!]{4,}', output):
            continue
            
        # Code Check
        is_code_requested = any(k in instruction.lower() for k in ["code", "program", "script", "snippet", "write a"])
        has_code = any(re.search(ind, output) for ind in code_indicators)
        if has_code and not is_code_requested:
            continue
            
        # Length check
        if len(output.split()) < 10: # Lowered for test visibility
            continue

        cleaned.append({
            "instruction": instruction,
            "output": output
        })
    return cleaned

# Simulate some bad data
test_data = [
    {"instruction": "What is 1NF?", "output": "1NF ensures cells contain atomic values."}, # Only 1 sentence
    {"instruction": "Explain Python", "output": "Python is a language. def my_func(): print('hello');"}, # Contains code but not asked
    {"instruction": "Write a python function", "output": "def my_func():\n    return 'hello'"}, # Code asked, but only 1 sentence? Wait, code usually doesn't have 2 sentences.
    {"instruction": "What is OS?", "output": "Operating System is software. It manages hardware and allows apps to run."}, # GOOD
    {"instruction": "Garbage test", "output": "Check this @@@@@ ##### $$$$$ symbols."}, # Random symbols
]

results = clean_dataset_test(test_data)
print(f"Original: {len(test_data)}, Cleaned: {len(results)}")
for r in results:
    print(f"PROCESSED: {r['instruction']} -> {r['output'][:50]}...")
