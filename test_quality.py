
# Standalone Quality Filter Test

def is_response_weak(text):
    if not text:
        return True
    clean_text = str(text).strip()
    if len(clean_text) < 8:
        return True
    generic_phrases = [
        "i have processed your request",
        "i am ready to assist",
        "ok",
        "okay",
        "done",
        "processed"
    ]
    if clean_text.lower() in generic_phrases:
        return True
    return False

def run_tests():
    test_cases = [
        ("Hi", True),
        ("OK", True),
        ("I have processed your request", True),
        ("I am ready to assist", True),
        ("Artificial Intelligence is fascinating.", False),
        ("The memory error has been resolved.", False),
        ("Done", True),
        ("Processing complete, sir.", False)
    ]
    
    print("--- Jarvis Quality Filter Tests ---")
    for text, expected in test_cases:
        result = is_response_weak(text)
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] Input: '{text}' | Is Weak: {result}")

if __name__ == "__main__":
    run_tests()
