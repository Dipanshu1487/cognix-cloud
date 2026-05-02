import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import traceback

BASE_MODEL_PATH = r"E:\phi2_repo"

def test_load():
    print(f"Checking Path: {BASE_MODEL_PATH}")
    if not os.path.exists(BASE_MODEL_PATH):
        print("Path does not exist!")
        return
        
    print("CUDA Available:", torch.cuda.is_available())
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    try:
        print("Attempting to load model on CPU...")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH,
            trust_remote_code=True,
            device_map={"": "cpu"},
            low_cpu_mem_usage=True
        )
        print("CPU Success!")
    except Exception as e:
        print("CPU ERROR DETECTED:")
        traceback.print_exc()

if __name__ == "__main__":
    test_load()
