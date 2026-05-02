import math

class StudyPlanner:
    """
    Education specialized tool to generate balanced study sessions.
    Based on educational hour-distribution logic.
    """

    def generate_plan(self, subjects, total_hours):
        if not subjects or total_hours <= 0:
            return "Please provide subjects and the number of hours you have to study."

        # Proportional distribution (equal for now)
        hours_per_subject = total_hours / len(subjects)
        
        # Format the session list
        sessions = []
        for subject in subjects:
            # Round to one decimal (e.g., 1.5 hours)
            h = round(hours_per_subject, 1)
            sessions.append(f"{subject}: {h} hour(s)")
            
        timetable = "\n".join(sessions)
        return f"Here is your study plan for the next {total_hours} hours:\n{timetable}"

study_planner = StudyPlanner()
