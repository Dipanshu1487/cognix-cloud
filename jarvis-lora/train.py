
import torch
import os
import json
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
# JARVIS GPU ENGINE CONFIGURATION (4-bit Balanced)
# =============================================================================
# Using 4-bit quantization to fit into 6GB VRAM
MODEL_NAME = r"E:\phi2_repo"
OUTPUT_DIR = r"E:\jarvis_lora_results"
DATASET_FILE = r"jarvis-lora\dataset.json"

# LoRA Configuration
lora_config = LoraConfig(
    r=32,
    lora_alpha=64,
    target_modules=["q_proj", "k_proj", "v_proj", "dense"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Quantization Configuration
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# 1. Load Tokenizer
print("--- LOADING TOKENIZER ---")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# 2. Load Model (GPU 4-bit Mode)
print("--- LOADING BASE MODEL TO GPU (4-bit) ---")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    trust_remote_code=True,
    device_map="auto",
    low_cpu_mem_usage=True
)

# 3. Prepare for Training
print("--- PREPARING FOR K-BIT TRAINING ---")
model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# 4. Prepare Dataset
print("--- PROCESSING DATASET ---")
with open(DATASET_FILE, "r") as f:
    raw_data = json.load(f)

def format_instruction(sample):
    return f"Instruction: {sample['instruction']}\nOutput: {sample['output']}"

class JarvisDataset(Dataset):
    def __init__(self, data, tokenizer, max_length=256):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text = format_instruction(self.data[idx])
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

train_dataset = JarvisDataset(raw_data, tokenizer)

# 5. Training Arguments (GPU Optimized)
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    learning_rate=2e-4,
    num_train_epochs=1,
    logging_steps=1,
    save_steps=50,
    fp16=True, # Enable mixed precision for GPU
    optim="paged_adamw_32bit", # Memory efficient optimizer
    remove_unused_columns=False,
    report_to="none"
)

# 6. Start Training
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

print("\n--- JARVIS ACADEMIC ENGINE: STARTING GPU TRAINING ---")
trainer.train()

# 7. Save Final Brain
trainer.model.save_pretrained(os.path.join(OUTPUT_DIR, "final_adapter"))
print("\n--- TRAINING COMPLETE: ACADEMIC BRAIN READY ---")
