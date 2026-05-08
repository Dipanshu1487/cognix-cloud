
# Jarvis Intelligence Brain - Unified Logic with LoRA Primary Engine
import ollama
import time
import re
import json
import torch
import os
import sys
from difflib import get_close_matches
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from core.normalizer import normalize_query


# --- LoRA Engine Configuration ---
# Rules: Load ONLY once, move to GPU if available, 4-bit for efficiency
print("CUDA Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    DEVICE = "cuda"
else:
    print("[WARNING] CUDA not available! cogniX will run in CPU-Optimization mode. Performance may be slower.")
    DEVICE = "cpu"

BASE_MODEL_PATH = r"E:\phi2_repo"
ADAPTER_PATH = r"E:\jarvis_lora_results\final_adapter"

_lora_model = None
_lora_tokenizer = None

# Rule: Persistence Flags
lora_available = False
_lora_initialized = False

# Context Management
conversation_history = []

def build_context(query):
    """
    Formats the last 3 turns into a structured context for the LLM.
    Ensures all history items are strings.
    """
    history_items = []
    for item in conversation_history[-6:]:
        if isinstance(item, dict):
            history_items.append(f"User: {item.get('user', '')}\nAssistant: {item.get('cognix', '')}")
        else:
            history_items.append(str(item))
            
    history = "\n".join(history_items)
    
    # Enhanced System Prompt from Brain v2 spec
    academic_system_prompt = (
        "You are cogniX, an AI-powered academic assistant.\n\n"
        "Rules:\n"
        "- Use previous conversation if relevant\n"
        "- Answer ONLY what is asked\n"
        "- Do NOT change topic\n"
        "- Do NOT hallucinate\n"
        "- Solve step-by-step if math\n"
        "- Do NOT add unnecessary explanation\n"
        "- If unsure, say 'I don't know'"
    )

    return academic_system_prompt, f"### Conversation Memory:\n{history}\n\n### Current Query:\n{query}\n\n### Response:"

def get_contextual_prompt(query):
    """Missing utility to build a flat prompt string for models."""
    sys_prompt, user_prompt = build_context(query)
    return f"{sys_prompt}\n\n{user_prompt}"


# --- Retrieval Layer: Knowledge Base ---
KB_PATH = os.path.join("knowledge", "kb.json")
def load_kb():
    if os.path.exists(KB_PATH):
        try:
            with open(KB_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[KB] Error loading knowledge base: {e}")
    return {}

KNOWLEDGE_BASE = load_kb()

def retrieve_answer(query, kb):
    """
    Improved Retrieval Layer with Fuzzy Matching.
    """
    q = query.lower().strip()
    keys = list(kb.keys())

    # 1. Fuzzy Matching (cutoff 0.6)
    match = get_close_matches(q, keys, n=1, cutoff=0.6)
    if match:
        print(f"[Retrieval] Fuzzy match found: {match[0]}")
        return kb[match[0]]

    # 2. Keyword Inclusion fallback
    for key in keys:
        if key in q:
            print(f"[Retrieval] Keyword match found: {key}")
            return kb[key]

    return None



def update_history(user_query, cognix_response):
    """
    Maintains a rolling history of the last 5 interactions.
    """
    global conversation_history
    conversation_history.append({"user": user_query, "cognix": cognix_response})
    if len(conversation_history) > 5:
        conversation_history.pop(0)

def rewrite_vague_query(current_query):
    """
    Detects vague follow-ups and rewrites them into complete instructions using context.
    If no context exists, asks for clarification.
    """
    global conversation_history
    
    vague_patterns = [
        r"^explain (more|it more)$",
        r"^give me (its |an )?example$",
        r"^tell me more$",
        r"^why is it important\??$",
        r"^elaborate$",
        r"^what about$",
        r"^how (so|come)\??$"
    ]
    
    lquery = current_query.lower().strip()
    is_vague = any(re.match(pattern, lquery) for pattern in vague_patterns)
    
    if is_vague:
        if not conversation_history:
             # Rule: No guessing without context
             return "CLARIFICATION: Could you please specify the subject? I don't have enough context from our current session to understand your request."
             
        last_exchange = conversation_history[-1]
        last_user = last_exchange['user']
        
        # Heuristic extraction of subject from last query
        subject_match = re.search(r"(?:what is|define|explain|tell me about) (.*)", last_user.lower())
        subject = subject_match.group(1).strip("? ") if subject_match else last_user
        
        if "explain" in lquery:
            return f"Explain {subject} in greater detail"
        if "tell me more" in lquery or "elaborate" in lquery:
            return f"Tell me more about the concept of {subject}"
        if "why is it important" in lquery:
            return f"Why is {subject} considered important in its field?"
        if "example" in lquery:
            return f"Give me a clear example of {subject}"
            
        return f"{current_query} regarding {subject}"
        
    return current_query

def detect_intent(query):
    """
    Brain v2 Intent Detection (Routing).
    """
    q = query.lower()

    if any(w in q for w in ["open", "play", "close", "search", "maximize", "minimize", "volume"]):
        return "command"

    if any(w in q for w in ["calculate", "solve", "root", "^", "equation", "+", "-", "*", "/", "integral", "derivative"]):
        return "math"

    if any(w in q for w in ["what", "who", "define", "explain", "tell me about"]):
        return "knowledge"

    return "general"

def solve_math(query):
    """
    Math Handling Layer.
    Tries SymPy first, then falls back to LLM step-by-step solving.
    """
    # Clean query for math
    math_query = query.lower().replace("calculate", "").replace("solve", "").strip()
    
    try:
        import sympy as sp
        # Simple symbol detection
        x, y, z = sp.symbols('x y z')
        expr_str = math_query.replace("^", "**")
        
        # Try a direct evaluation for simple arithmetic or equations
        if "=" in expr_str:
            parts = expr_str.split("=")
            eq = sp.Eq(sp.sympify(parts[0]), sp.sympify(parts[1]))
            sol = sp.solve(eq)
            return f"The solution is: {sol}"
        else:
            res = sp.sympify(expr_str)
            return str(res)
    except Exception as e:
        print(f"[Math] SymPy failed or not installed: {e}. Falling back to LLM.")
        return None

def validate_response(query, response):
    """
    Improved Validation Layer (v2).
    """
    if not response:
        return False

    if len(response.split()) < 3:
        return False

    bad_patterns = [
        "thank you for watching",
        "subscribe",
        "the given statement asserts",
        "this answer addresses",
        "like and share",
        "as an ai",
        "i am a language model"
    ]

    for p in bad_patterns:
        if p in response.lower():
            return False

    return True

def clean_response(text):
    """
    Strips robotic phrases and enforces clean delivery.
    """
    if not text:
        return text

    BAD = [
        "the given statement asserts",
        "based on the provided information",
        "according to the text",
        "i don't have enough context but"
    ]

    for b in BAD:
        if b in text.lower():
            return "I don't know the answer to that yet."

    return text.strip()


def assign_quality_score(response, user_input):
    """
    Antigravity Quality Control Engine.
    Assigns a score: GOOD, WEAK, or BAD based on cogniX Framework standards.
    """
    if not response or len(str(response).strip()) == 0:
        return "BAD", "Empty response"

    resp = str(response).strip()
    lresp = resp.lower()
    linput = user_input.lower().strip()
    words = resp.split()

    # --- BAD CRITERIA ---
    
    # 1. Broken Code Syntax
    if any(k in resp for k in ["def ", "class ", "import ", "{", "}", "print("]):
        mismatched = (resp.count("(") != resp.count(")")) or \
                     (resp.count("{") != resp.count("}")) or \
                     (resp.count("[") != resp.count("]"))
        if mismatched or resp.strip().endswith(":") or \
           resp.split("\n")[-1].strip().startswith(("def", "class", "if", "for", "while")):
            return "BAD", "Broken code syntax or incomplete snippet"
            
    # 2. Grammar & Structure Violation
    if not resp[0].isupper():
         return "BAD", "Does not start with capital letter / broken grammar"
         
    sentences = [s for s in resp.split(".") if len(s.strip()) > 0]
    if len(sentences) < 1 and "Example:" not in resp:
         return "WEAK", "Shallow response / lacks structure"

    # 3. Meaningless / Fragmented / Drift
    if re.search(r'[^a-zA-Z0-9\s,.?!\n:()-]{5,}', resp):
        return "BAD", "Contains meaningless character sequences"
    
    # 4. Filter unrelated topics or appended questions
    hallucination_indicators = ["?", "how can i", "what else", "ask me", "let me know"]
    if any(ind in resp.lower().split(". ")[-1] for ind in hallucination_indicators if "?" in resp[-20:]):
        return "BAD", "Contains appended hallucinated questions"

    # 5. Code Check (Strict)
    is_code_requested = any(k in linput for k in ["code", "program", "script", "snippet", "write a"])
    if not is_code_requested and any(k in resp for k in ["def ", "class ", "import ", "{", "}"]):
        return "BAD", "Generated code when not requested"

    # 6. Input Repetition
    if linput in lresp and len(words) < len(linput.split()) + 5:
        return "BAD", "Repeating input without adding information"

    # --- QUALITY SCORING ---
    if len(words) >= 20 and any(p in resp for p in [".", "!", "?"]):
        # Additional Drift Protection: If history exists, ensure topic continuity (heuristic)
        if len(conversation_history) > 0:
            last_topic_keywords = set(conversation_history[-1]['user'].lower().split() + conversation_history[-1]['cognix'].lower().split())
            current_resp_keywords = set(resp.lower().split())
            intersection = last_topic_keywords.intersection(current_resp_keywords)
            # If no keyword overlap and it's a technical response, it might be drifting
            if not intersection and any(k in linput for k in ["explain", "deeply", "more", "it"]):
                return "BAD", "Potential topic drift / unrelated subject introduced"

        return "GOOD", "Structured and professional"
    
    return "WEAK", "Passable but requires fallback for depth"



def is_academic_query(command):
    """Determine if a query should be routed to the academic LoRA model."""
    ltext = command.lower()
    
    # General Knowledge / People / Events bypass LoRA
    gk_keywords = [
        "who is", "who was", "biography", "current affairs", 
        "news", "president", "prime minister", "actor", "movie"
    ]
    if any(k in ltext for k in gk_keywords):
        return False
        
    # Academic / Technical concepts use LoRA
    academic_keywords = [
        "what is", "how does", "explain", "define", "concept", "theory", "algorithm",
        "dsa", "os", "dbms", "ai", "machine learning", "data structure", "pointer",
        "stack", "queue", "database", "operating system", "code", "programming",
        "python", "c++", "java", "math", "physics", "chemistry", "biology"
    ]
    # Check for Vague Follow-ups if context exists
    vague_keywords = ["explain", "example", "more", "elaborate", "important", "why"]
    if conversation_history and any(k in ltext for k in vague_keywords) and len(ltext.split()) < 5:
        return True

    return False

def init_lora_engine():
    """Initializes the specialized Academic Brain once globally."""
    global _lora_model, _lora_tokenizer, lora_available, _lora_initialized
    
    if _lora_initialized:
        return True

    _lora_initialized = True
    print("\n--- INITIALIZING LORA ACADEMIC BRAIN ---")
    
    # Environment Safety Checks
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    executable = sys.executable.lower()
    is_correct_version = version in ["3.11", "3.12"]
    is_correct_env = "jarvis_env" in executable or "jarvis_env" in sys.prefix.lower() or os.getenv("STREAMLIT_RUNTIME_CHECK") == "true"
    
    if not is_correct_version:
        print(f"Wrong Python version detected: {version}")
        print("cogniX requires Python 3.11 or 3.12")
        lora_available = False
        return False
    
    print(f"Environment verified (Python {version})")

    try:
        # 1. Tokenizer
        _lora_tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH, trust_remote_code=True)
        _lora_tokenizer.pad_token = _lora_tokenizer.eos_token if _lora_tokenizer.eos_token else "<|endoftext|>"
        _lora_tokenizer.padding_side = "right"

        # 2. Config with CPU Offload Support
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            llm_int8_enable_fp32_cpu_offload=True # Support CPU offloading
        )

        # 3. Load Base Model (Memory-Optimized 4-bit)
        try:
            print(f"[LoRA] Loading base model from {BASE_MODEL_PATH}...")
            base_model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL_PATH,
                quantization_config=bnb_config,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            print("Running on device:", torch.cuda.get_device_name(0))
        except Exception as e:
            import traceback
            err_msg = str(e)
            print(f"\n[CRITICAL ERROR] Failed to load Academic Brain weights on GPU.")
            print(f"Error Detail: {err_msg}")
            
            # Specific hint for the 'weights not loading' issue
            if "memory" in err_msg.lower() or "paging" in err_msg.lower() or "allocate" in err_msg.lower():
                print("DIAGNOSIS: Out of Memory. Your 5GB available RAM is likely too low to stage the 5.5GB model weights.")
                print("FIX: Close background apps or increase your Windows Pagefile size to 16GB.")
            
            traceback.print_exc()
            lora_available = False
            return False

        # 4. Attach LoRA Adapter
        try:
            print(f"[LoRA] Attaching adapter from {ADAPTER_PATH}...")
            _lora_model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
            _lora_model.eval()
            lora_available = True
            print("LoRA Academic Brain loaded successfully!")
            return True
        except Exception as peft_err:
            print(f"[LoRA] Adapter Error: {peft_err}")
            traceback.print_exc()
            lora_available = False
            return False

    except Exception as global_err:
        import traceback
        print(f"[LoRA] System Error during initialization: {global_err}")
        traceback.print_exc()
        lora_available = False
        return False

def ask_lora_brain(user_input):
    """
    Primary Response Engine:specialized academic AI using fine-tuned LoRA.
    """
    global _lora_model, _lora_tokenizer, lora_available
    
    if not lora_available:
        return None

        if _lora_model is None or _lora_tokenizer is None:
            print("[LoRA] Model or Tokenizer is None even though lora_available is True.")
            return None

        # Build prompt with strict Conversation/Instruction separation
        prompt = get_contextual_prompt(user_input)
        prompt += "\n\n### Response:\n"
        
        inputs = _lora_tokenizer(prompt, return_tensors="pt").to(_lora_model.device)
        
        with torch.no_grad():
            outputs = _lora_model.generate(
                **inputs,
                max_new_tokens=200,
                pad_token_id=_lora_tokenizer.pad_token_id,
                eos_token_id=_lora_tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.6,
                top_p=0.9,
                repetition_penalty=1.2
            )

        full_output = _lora_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "### Response:" in full_output:
            response = full_output.split("### Response:")[-1].strip()
        else:
            response = full_output.replace(prompt, "").strip()

        # --- POST-GENERATION DISCIPLINE (ANTIGRAVITY UPDATES) ---
        
        # 1. Stop behavior: Cut generation when a new question starts (contains "?")
        if "?" in response:
            response = response.split("?")[0].strip()

        # 2. Add Stop Behavior for unrelated content / topic switching
        drift_markers = ["What about", "How can I", "Ask me", "Let me know", "Would you like", "I can also"]
        for marker in drift_markers:
            if marker in response:
                response = response.split(marker)[0].strip()

        # 3. Output Post-Processing: Keep only first relevant answer block
        # Split by paragraphs and take the first one if it's substantial, 
        # but for cogniX we want the most direct answer.
        # We also remove unrelated sentences (this is handled by the strict split above).
        response = response.split("### Instruction:")[0].strip()
        
        # 4. Final cleaning: Answer ONLY what user asked, NO trailing questions
        response = response.replace("\n\n", " [NEWLINE] ").replace("\n", " ").replace(" [NEWLINE] ", "\n\n").strip()
        
        # Quality Filter
        score, reason = assign_quality_score(response, user_input)
        
        if score == "GOOD":
            print(f"[LoRA] Response accepted ({reason})")
            return response
        else:
            print(f"[LoRA] {score} response rejected: {reason}. Triggering fallback.")
            return None

    except Exception as e:
        print(f"[LoRA] Inference Error: {e}")
        return None

def ask_ai(command):
    """
    Intent Classifier Bridge.
    Handles decision between ACTION and INFORMATION/Academic Query.
    """
    global conversation_history

    system_prompt = f"""
You are cogniX Core Controller.
Convert input to ACTION (JSON) or INFORMATION (return 'conversation').
User: {command}
cogniX:
"""

    for attempt in range(2):
        try:
            contextual_input = get_contextual_prompt(command)
            response = ollama.chat(
                model="phi3",
                messages=[
                    {"role": "system", "content": "You are a cogniX intent classifier. Actions whitelist: open, close, execute, search. For questions, explanations, or chat, output ONLY 'conversation'."},
                    {"role": "user", "content": f"Context: {contextual_input}\nIdentify intent."}
                ]
            )

            reply = response["message"]["content"].strip()
            # Basic sanity check/cleaning
            json_match = re.search(r'\{.*\}', reply, re.DOTALL)
            if json_match:
                return json_match.group(0)

            return "conversation"

        except Exception as e:
            print("Intent API error:", e)
            time.sleep(1)

    return "conversation"

def ask_local_conversation(command):
    """
    Brain v2 Main Pipeline: Intent -> Retrieval/Math -> Model -> Validation
    """
    global conversation_history
    raw_query = command.strip()
    query = normalize_query(raw_query)
    print("USER (Raw):", raw_query)
    print("USER (Normalized):", query)

    try:
        # 1. INTENT DETECTION
        intent = detect_intent(query)
        print(f"[Brain] Intent detected: {intent}")

        # 2. SPECIALIZED HANDLERS
        if intent == "math":
            math_result = solve_math(query)
            if math_result:
                print("SOURCE: MATH")
                print("FINAL:", math_result)
                conversation_history.append(f"User: {query}")
                conversation_history.append(f"Jarvis: {math_result}")
                return math_result
        
        # 3. RETRIEVAL LAYER (Fuzzy)
        kb_answer = retrieve_answer(query, KNOWLEDGE_BASE)
        if kb_answer:
            print("SOURCE: KB")
            print("FINAL:", kb_answer)
            conversation_history.append(f"User: {query}")
            conversation_history.append(f"Jarvis: {kb_answer}")
            return kb_answer

        # 4. GENERATION LAYER (Context-Aware)
        print("SOURCE: MODEL")
        system_prompt, contextual_query = build_context(query)
        
        safe_fallback = "I don't know the answer to that yet."
        generated_raw = None

        # Try Academic LoRA first ONLY if it's a technical academic query
        if (intent in ["knowledge", "general"]) and lora_available and is_academic_query(query):
            # LoRA engine expects specific format, adapting contextual_query
            generated_raw = ask_lora_brain(query) 
            if generated_raw:
                 print("MODEL RAW (LoRA):", generated_raw)

        if not generated_raw:
            # Fallback to Ollama (phi3) with full context
            try:
                response = ollama.chat(
                    model="phi3",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": contextual_query}
                    ],
                    options={
                        "num_predict": 250,
                        "temperature": 0.3,
                        "top_p": 0.9,
                    }
                )
                generated_raw = response["message"]["content"].strip()
                print("MODEL RAW (Ollama):", generated_raw)
            except Exception as e:
                print(f"[Brain] Generation Error: {e}")
                generated_raw = ""

        # 5. VALIDATION & CLEANING
        if not generated_raw:
            return safe_fallback
            
        if not validate_response(query, generated_raw):
            print(f"VALIDATION FAILED")
            # If it's a short response that failed validation, it might still be okay if it's simple
            if len(generated_raw.split()) > 1:
                return clean_response(generated_raw)
            return safe_fallback

        final_answer = clean_response(generated_raw)
        
        # Final strip of any lingering markers
        if "### Response:" in final_answer:
            final_answer = final_answer.split("### Response:")[-1].strip()

        print("FINAL:", final_answer)
        
        # Maintain History (last 3 turns = 6 items)
        conversation_history.append(f"User: {query}")
        conversation_history.append(f"Jarvis: {final_answer}")
        if len(conversation_history) > 6:
            conversation_history = conversation_history[-6:]

        return final_answer
    except Exception as e:
        import traceback
        print(f"[Brain] CRITICAL ERROR in pipeline: {e}")
        traceback.print_exc()
        return "I apologize, but my cognitive processor encountered an error. Please try rephrasing your query."




# Note: The LoRA engine is initialized globally upon module load for single-load capability.
init_lora_engine()

def process_query(query):
    """Entry point for API and external services."""
    from core.router import route_command
    return route_command(query)