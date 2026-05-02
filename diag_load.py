
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import sys

MODEL_PATH = r"E:\phi2_repo"

print(f"--- DIAGNOSTIC: LOADING MODEL FROM {MODEL_PATH} ---")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    print("Tokenizer loaded.")
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        device_map={"": "cpu"},
        low_cpu_mem_usage=True
    )
    print("Model loaded.")
    print(f"Model Class: {type(model)}")
    print(f"Architecture: {model.config.architectures}")
    
    # Test a single forward pass
    inputs = tokenizer("Hello", return_tensors="pt")
    outputs = model(**inputs)
    print("Forward pass success!")
    
except Exception as e:
    print(f"\n!!! CRITICAL ERROR CAPTURED !!!\n{str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n--- DIAGNOSTIC COMPLETE: SYSTEM IS HEALTHY ---")
