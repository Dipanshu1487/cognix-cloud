import sys
import os
import traceback
from unittest.mock import MagicMock

# Mock heavy or missing dependencies before imports
sys.modules['selenium'] = MagicMock()
sys.modules['webdriver_manager'] = MagicMock()
sys.modules['webdriver_manager.chrome'] = MagicMock()
sys.modules['selenium.webdriver'] = MagicMock()
sys.modules['selenium.webdriver.chrome'] = MagicMock()
sys.modules['selenium.webdriver.chrome.service'] = MagicMock()
sys.modules['selenium.webdriver.chrome.options'] = MagicMock()
sys.modules['selenium.webdriver.common'] = MagicMock()
sys.modules['selenium.webdriver.common.by'] = MagicMock()
sys.modules['selenium.webdriver.common.keys'] = MagicMock()
sys.modules['selenium.webdriver.support'] = MagicMock()
sys.modules['selenium.webdriver.support.ui'] = MagicMock()
sys.modules['keyboard'] = MagicMock()
sys.modules['pycaw'] = MagicMock()
sys.modules['pycaw.pycaw'] = MagicMock()
sys.modules['comtypes'] = MagicMock()
sys.modules['ollama'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['peft'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

# Add current dir to path to import core
sys.path.append(os.getcwd())

import core.router
from core.router import route_command

# Mock side effects to prevent system disruption during automated testing
def mock_open_youtube(query): print(f"Mock: Opening youtube for {query}")
def mock_handle_sys(cmd): print(f"Mock: System command {cmd}")
def mock_search(query): return f"Mock: Search results for {query}"
def mock_maximize(): print("Mock: maximize")
def mock_minimize(): print("Mock: minimize")
def mock_vol_up(): print("Mock: vol up")
def mock_vol_down(): print("Mock: vol down")

core.router.open_youtube_and_play = mock_open_youtube
core.router.handle_system_commands = mock_handle_sys
core.router.search_internet = mock_search
core.router.maximize_window = mock_maximize
core.router.minimize_window = mock_minimize
core.router.volume_up = mock_vol_up
core.router.volume_down = mock_vol_down
from core.voice import stop_speaking
import core.voice
core.voice.stop_speaking = lambda: print("Mock: stop speaking")

def run_extreme_tests():
    errors = []
    
    test_cases = [
        # Normal questions
        "What is artificial intelligence?",
        "Who was the first president of the United States?",
        
        # System commands
        "open notepad",
        "maximize",
        "volume up",
        "stop",
        
        # Math & Logic (Testing math engine limits)
        "calculate 10 divided by 0",
        "solve 2x + 5 = 15",
        "what is the square root of negative one",
        
        # Study Planner
        "plan my study for math and physics for 5 hours",
        "plan my study for nothing for -10 hours",
        "plan my study for English for alphabet hours",
        
        # Extreme / Edge cases
        "", # Empty string
        "   ", # Whitespace
        "a" * 1000, # Very long string
        "!@#$%^&*()", # Special characters
        "json format: {\"action\": \"inform\"}", # Text containing partial json
        '{"action": {"intent": "ExplainAI"}, "information": {"message": "AI is coming."}}', # Valid JSON via router
        '{"malformed": "json"', # Broken JSON
        "conversation", # Reserved keyword
        "sleep", # Built-in command
        "{\"action\": \"open_app\", \"parameters\": {\"app\": \"calc\"}}" # Valid action JSON directly
    ]

    print(f"--- Running {len(test_cases)} Extreme Tests ---")
    
    for i, test in enumerate(test_cases):
        print(f"\n========================================")
        print(f"[Test {i+1}] Input: {test[:50] + '...' if len(test)>50 else test}")
        try:
            res = route_command(test)
            if res is None:
                print("Result: <None>")
            else:
                print(f"Result (first 100 chars): {str(res)[:100]}")
        except Exception as e:
            err_msg = traceback.format_exc()
            print(f"FAILED: {e}")
            errors.append((test, err_msg))
            
    print("\n========================================")
    print("--- Summary ---")
    if not errors:
        print("ALL TESTS PASSED: No system crashes detected.")
    else:
        print(f"SYSTEM CRASH DETECTED: {len(errors)} tests failed.")
        for t, e in errors:
            print(f"\nFailed Input: {t}")
            print(f"Error Traceback:\n{e}")

if __name__ == "__main__":
    run_extreme_tests()
