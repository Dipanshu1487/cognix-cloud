import asyncio
import os
import sys

# Add project root to path so we can import core.voice
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.voice import speak, wait_until_done

PHRASES = [
    "cogniX online. All systems operational.",
    "Yes sir",
    "On it",
    "I'm on it",
    "Going to sleep.",
    "Session timed out. Going to sleep.",
    "Stopping.",
    "I am having trouble processing that. Please try again.",
    "I didn't understand that. Please try again.",
    "Ready for your command.",
    "How can I help you, sir?",
    "Awaiting instructions."
]

async def warm_cache():
    print("--- cogniX Cache Warmer ---")
    print(f"Pre-generating {len(PHRASES)} common phrases...")
    print("This requires an active internet connection.")
    print()
    
    for phrase in PHRASES:
        print(f"Generating: {phrase}")
        speak(phrase)
        wait_until_done()
    
    print()
    print("Cache warming complete! These phrases will now work perfectly offline.")

if __name__ == "__main__":
    try:
        asyncio.run(warm_cache())
    except KeyboardInterrupt:
        print("\nStopping...")
