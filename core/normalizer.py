
import ollama

def normalize_query(user_input):
    """
    Antigravity Query Normalization Engine.
    Corrects typos, grammar, and standardizes academic queries.
    """
    normalization_prompt = f"""
You are a query normalization and correction engine for an AI academic assistant.

---

# 🎯 OBJECTIVE
Convert user input into a clean, corrected, and standardized query that preserves the original intent.

---

# 🔧 INSTRUCTIONS
1. Correct all spelling mistakes
2. Fix grammar if necessary
3. Normalize names (people, places, concepts)
4. Expand abbreviations if needed
5. Resolve obvious typos into most likely correct form
6. Maintain the original meaning of the query
7. Do NOT change the intent of the question
8. Do NOT answer the question
9. Do NOT add explanations

---

# ⚠️ RULES
* Output ONLY the corrected query
* No extra text, no explanation
* If unsure, return the closest reasonable correction

---

# 🧪 EXAMPLES
Input: who is nepolean gonapat
Output: who is Napoleon Bonaparte

Input: wat is deravative of sinx
Output: what is the derivative of sin x

Input: einstein reltivity explain
Output: explain Einstein's theory of relativity

---

# 🚀 TASK
Normalize the following query:

{user_input}
"""
    try:
        response = ollama.chat(
            model="phi3",
            messages=[{"role": "user", "content": normalization_prompt}],
            options={"temperature": 0.0, "num_predict": 50}
        )
        normalized = response["message"]["content"].strip()
        # Remove "Output: " prefix if the model adds it
        if normalized.lower().startswith("output:"):
            normalized = normalized[7:].strip()
        return normalized
    except Exception as e:
        print(f"[Normalizer] Error: {e}")
        return user_input
