
import json
import re
import os
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    Trainer, 
    TrainingArguments,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import Dataset

# =============================================================================
# ANTIGRAVITY LORA PIPELINE CONFIGURATION
# =============================================================================
DATASET_PATH = "knowledge/btech_academic_dataset_1000.json"
SUPPLEMENTAL_DATASET = "knowledge/disambiguation_dataset.json"
BASE_MODEL_PATH = r"E:\phi2_repo"
OUTPUT_DIR = "jarvis-lora/final_clean_model"

# Training Hyperparameters
BATCH_SIZE = 1
GRADIENT_ACCUMULATION = 16
EPOCHS = 5 # Increased for complex intelligence mapping
LEARNING_RATE = 1e-4

# 1. DATASET CLEANING & FORMATTING
# =============================================================================
def clean_dataset(raw_dataset):
    print("--- [SYSTEM] Cleaning academic dataset with intelligence upgrade...")
    cleaned = []
    
    code_indicators = [r"\{", r"\}", r";", r"def ", r"class ", r"import ", r"int ", r"float ", r"\("]
    
    for entry in raw_dataset:
        instruction = entry.get("instruction", "").strip()
        output = entry.get("output", "").strip()
        
        # 1. Basic length filter
        if not instruction or not output:
             continue
             
        # 2. Grammar & Structured Format Check
        # Rule: Min 2 sentences, clear structure
        sentences = re.split(r'[.!?]+', output)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 2:
            continue
            
        # 3. Noise / Random Tokens
        if re.search(r'[^a-zA-Z0-9\s,.?!\n:()-]{5,}', output):
            continue
            
        # 4. Filter unrelated questions/drift & Meta-Instruction leakage
        meta_instructions = [
            "to provide an answer", "if the user asks", "respond in a concise", 
            "here is a structured", "to answer clearly", "you should respond",
            "the following response", "as an ai", "to provide a clear"
        ]
        
        lower_output = output.lower()
        if any(phrase in lower_output for phrase in meta_instructions):
            continue

        if any(phrase in lower_output for phrase in ["how can i help", "anything else", "let me know"]):
            continue

        # 5. Code Check (Strict)
        is_code_requested = any(k in instruction.lower() for k in ["code", "program", "script", "snippet", "write a"])
        has_code = any(re.search(ind, output) for ind in code_indicators)
        if has_code and not is_code_requested:
            continue
        if is_code_requested and "```" not in output and len(output) < 50:
            continue # Reject incomplete code snippets
            
        # 6. Structured Response Enforcement (Definition + [Example] + [Explanation])
        # We ensure it doesn't just jump into code or random lists
        if not output[0].isupper():
            continue

        cleaned.append({
            "instruction": instruction,
            "output": output
        })
        
    print(f"--- [SYSTEM] Pipeline optimized. Output size: {len(cleaned)} high-quality pairs.")
    return cleaned

# 2. PROMPT TEMPLATE (STRICT)
def format_prompt(sample):
    return f"### Instruction:\n{sample['instruction']}\n\n### Response:\n{sample['output']}"

# 3. CUSTOM DATASET CLASS
# =============================================================================
class CleanAcademicDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = format_prompt(self.data[idx])
        encodings = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encodings["input_ids"].squeeze(),
            "attention_mask": encodings["attention_mask"].squeeze(),
            "labels": encodings["input_ids"].squeeze()
        }

# 4. MAIN PIPELINE
# =============================================================================
def run_pipeline():
    # step 1: Load and Clean Data
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset not found at {DATASET_PATH}")
        return

    full_data = []
    
    # Load Main Dataset
    with open(DATASET_PATH, "r") as f:
        full_data.extend(json.load(f))
        
    # Load Supplemental Disambiguation Dataset
    if os.path.exists(SUPPLEMENTAL_DATASET):
        with open(SUPPLEMENTAL_DATASET, "r") as f:
            full_data.extend(json.load(f))
        print(f"--- [SYSTEM] Supplemented dataset with disambiguation examples.")

    clean_data = clean_dataset(full_data)
    
    # Step 2: Initialize Tokenizer and Model
    print("--- [SYSTEM] Initializing Phi-2 Core Training...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_PATH,
        quantization_config=bnb_config,
        trust_remote_code=True,
        device_map="auto",
        low_cpu_mem_usage=True
    )

    # Step 3: Configure LoRA (PEFT)
    lora_config = LoraConfig(
        r=32,
        lora_alpha=64,
        target_modules=["q_proj", "k_proj", "v_proj", "dense"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Step 4: Prepare Dataset Objects
    train_dataset = CleanAcademicDataset(clean_data, tokenizer)

    # Step 5: Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION,
        learning_rate=LEARNING_RATE,
        num_train_epochs=EPOCHS,
        logging_steps=10,
        save_steps=100,
        fp16=True,
        optim="paged_adamw_32bit",
        remove_unused_columns=False,
        report_to="none"
    )

    # Step 6: Trigger Training
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )

    print("\n--- [SYSTEM] Starting LoRA Academic Fine-Tuning ---")
    # Note: Training is triggered here but may require high GPU memory
    try:
        trainer.train()
    except Exception as e:
        print(f"[CRITICAL ERROR] Training failed: {e}")
        return

    # Step 7: Save Clean Model
    print(f"--- [SYSTEM] Saving final clean model to {OUTPUT_DIR}...")
    trainer.model.save_pretrained(OUTPUT_DIR)
    print("\n--- [SUCCESS] Academic assistant model is ready for deployment. ---")

if __name__ == "__main__":
    run_pipeline()
