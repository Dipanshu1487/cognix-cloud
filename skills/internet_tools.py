from duckduckgo_search import DDGS
from core.brain import ask_ai

def search_internet(query):

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)

            raw_data = ""

            for r in results:
                raw_data += r["body"] + " "

        # 🔥 Send raw data to AI for cleaning
        prompt = f"""
Clean and summarize this information into 1–2 simple spoken sentences:

{raw_data}
"""

        clean_answer = ask_ai(prompt)

        return clean_answer

    except Exception as e:
        print("Search error:", e)
        return "Sorry Dipanshu, I could not search the internet."