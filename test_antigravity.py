
from core.response_engine import process_response

def test_antigravity_v2():
    print("--- Running Antigravity v2 Unit Tests ---")
    
    # Test 1: Action 'inform' with 'message'
    print("\nTest 1 (Action Inform):")
    json_input = '{"action": "inform", "information": {"message": "The weather is sunny today."}}'
    res1 = process_response(json_input)
    print(f"Output: {res1}")
    
    # Test 2: Normal Response key
    print("\nTest 2 (Normal Key):")
    json_input2 = '{"response": "Direct answer here."}'
    res2 = process_response(json_input2)
    print(f"Output: {res2}")
    
    # Test 8: Weak Response (Length < 8)
    print("\nTest 8 (Too Short):")
    from core.brain import is_response_weak
    short_input = "Hi"
    is_weak = is_response_weak(short_input)
    print(f"Input: '{short_input}', Is Weak: {is_weak}")

    # Test 9: Generic Phrase (Robotic)
    print("\nTest 9 (Generic Phrase):")
    generic_input = "I have processed your request"
    is_weak = is_response_weak(generic_input)
    print(f"Input: '{generic_input}', Is Weak: {is_weak}")

    # Test 10: Valid Long Response
    print("\nTest 10 (Valid Response):")
    valid_input = "The artificial intelligence system is now fully operational and ready for tasking."
    is_weak = is_response_weak(valid_input)
    print(f"Input: '{valid_input}', Is Weak: {is_weak}")

if __name__ == "__main__":
    test_antigravity_v2()
