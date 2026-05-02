import os
import subprocess
from datetime import datetime
from core.voice import speak

def handle_system_commands(command):

    if "time" in command:
        current = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current}")
        return True

    if "open chrome" in command:
        speak("Opening Chrome")
        os.system("start chrome")
        return True

    if "close chrome" in command or "close the chrome" in command:
        speak("Closing Chrome")
        subprocess.run(
            ["taskkill", "/f", "/im", "chrome.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True

    if "open vscode" in command:
        speak("Opening Visual Studio Code")
        os.system("code")
        return True

    if "open youtube" in command:
        speak("Opening YouTube")
        os.system("start https://youtube.com")
        return True

    if "sleep" in command or "stop listening" in command:
        return "sleep"

    return False