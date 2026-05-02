import sys
sys.path.append("c:/Users/LENOVO/OneDrive/Desktop/jarvis")
from core.router import route_command

print("Testing route_command with 'play a funny video on youtube'")
res = route_command("play a funny video on youtube")
print("Result:", res)
