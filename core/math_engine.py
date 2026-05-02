import re
import operator

class MathEngine:
    """
    A lightweight, safe utility for solving basic math expressions locally.
    Falls back to Cloud AI for symbolic or word-based math.
    """
    
    # Supported operators
    OPS = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '^': operator.pow,
        '**': operator.pow
    }

    @staticmethod
    def solve(problem):
        problem = problem.lower().replace("what is", "").replace("calculate", "").replace("solve", "").strip()
        
        # 1. Try simple arithmetic locally using a safe regex-based evaluator
        # Matches patterns like 12 + 4 * 3
        try:
            # Clean non-math chars except what's needed for basic arithmetic
            clean_p = re.sub(r'[^0-9+\-*/^().\s]', '', problem)
            if clean_p.strip():
                # For safety, we use eval but with extreme caution or a custom parser.
                # Since we want speed, we'll use a simple eval of the sanitized string.
                # Note: This is safe because of the regex filter above.
                result = eval(clean_p.replace('^', '**'))
                return f"The answer to {problem} is {result}."
        except:
            pass
            
        # 2. If it's complex (e.g., 'derivative of x^2', 'solve for x')
        # We return a specific instruction to route it to Gemini
        return "route_to_ai"

math_engine = MathEngine()
