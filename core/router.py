
import json
import re
from browser_controller import open_youtube_and_play, pause_video, resume_video, play_next, volume_up, volume_down, play_previous, maximize_window, minimize_window, close_browser, close_video
from core.intent_engine import detect_intent
from skills.system_control import handle_system_commands
from skills.internet_tools import search_internet
from core.brain import ask_ai, ask_local_conversation
from core.gemini_engine import ask_gemini
from core.voice import stop_speaking
from memory.memory_manager import remember, recall
from automation.reminder_scheduler import set_reminder
from core.math_engine import MathEngine
from automation.study_planner import StudyPlanner
from core.response_engine import process_response

math_engine = MathEngine()
study_planner = StudyPlanner()

def route_command(command):
    """
    Main entry point for command routing.
    Rule: All outputs must pass through the Antigravity processing engine.
    """
    raw_response = _raw_route_command(command)
    return process_response(raw_response)

def _raw_route_command(command):
    """
    Internal routing logic for cogniX.
    """
    command = command.lower().strip()
    
    # 1. High-Priority Hardware/System Overrides (Fast)
    if "volume up" in command:
        volume_up()
        return "Volume increased"
    if "volume down" in command:
        volume_down()
        return "Volume decreased"
    if "maximize" in command:
        maximize_window()
        return "Window maximized"
    if "minimize" in command or "minimise" in command:
        minimize_window()
        return "Window minimized"
    if "stop" in command or "quiet" in command or "shut up" in command:
        stop_speaking()
        return "Stopping"

    # RECOVERY-DEBUG MODE: Bypass all complex routing and force fallback AI
    return ask_local_conversation(command)