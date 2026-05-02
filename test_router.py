
import json
import sys
import os

# Add current dir to path to import core
sys.path.append(os.getcwd())

from core.router import route_command
from core.response_engine import process_response

def test_router_logic():
    print("--- Jarvis Router & Response Engine Integration Tests ---")

    # Mocking the brain is hard because it uses Ollama/Transformers. 
    # But we can test _raw_route_command indirectly if we can inject responses.
    # For now, let's verify that process_response no longer crashes and returns the expected string.

    print("\n1. Testing process_response with nested JSON (No crash expected):")
    nested_json = '{"action": {"intent": "ExplainAI", "entities": [], "parameters": []}}'
    res = process_response(nested_json)
    print(f"Result: {res}")
    
    print("\n2. Testing process_response with 'inform' action:")
    inform_json = '{"action": "inform", "information": {"message": "AI stands for Artificial Intelligence."}}'
    res = process_response(inform_json)
    print(f"Result: {res}")

    print("\n3. Testing process_response with dictionary action + message:")
    nested_msg = '{"action": {"intent": "ExplainAI"}, "information": {"message": "Nested but has message."}}'
    res = process_response(nested_msg)
    print(f"Result: {res}")

if __name__ == "__main__":
    test_router_logic()
