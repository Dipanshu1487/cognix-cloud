import difflib
import re

class AnswerEvaluator:
    @staticmethod
    def evaluate(student_answer, correct_answer, question_type='text'):
        if not student_answer or not correct_answer:
            return 0.0

        student_answer = str(student_answer).strip().lower()
        correct_answer = str(correct_answer).strip().lower()

        if question_type == 'mcq':
            return 1.0 if student_answer == correct_answer else 0.0

        if question_type == 'numeric':
            try:
                s_num = float(re.findall(r"[-+]?\d*\.\d+|\d+", student_answer)[0])
                c_num = float(re.findall(r"[-+]?\d*\.\d+|\d+", correct_answer)[0])
                return 1.0 if abs(s_num - c_num) < 0.001 else 0.0
            except (ValueError, IndexError):
                return 0.0

        similarity = difflib.SequenceMatcher(None, student_answer, correct_answer).ratio()
        
        if similarity > 0.85:
            return 1.0
        elif similarity < 0.3:
            return 0.0
        
        return round(similarity, 2)
