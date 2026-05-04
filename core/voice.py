import asyncio
import edge_tts
import pygame
import hashlib
import os
import time
import uuid
import threading

VOICE = "en-GB-RyanNeural"
MAX_TTS_RETRIES = 2
CACHE_DIR = os.path.join(os.getcwd(), "cache", "audio")

# Create cache directory if it doesn't exist
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize pygame mixer once
HAS_MIXER = False
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    HAS_MIXER = True
except (pygame.error, Exception) as e:
    print(f"[Voice] Mixer initialization failed: {e}")
    HAS_MIXER = False

# Global state
is_speaking = False
speaking_thread = None

def get_cache_filename(text, voice):
    """Generate a unique deterministic filename for a given text and voice."""
    hash_input = f"{text}_{voice}".lower().strip()
    text_hash = hashlib.md5(hash_input.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"voice_{text_hash}.mp3")

async def _edge_tts_generate(text, filename):
    """Internal helper to generate TTS using edge-tts."""
    for attempt in range(1, MAX_TTS_RETRIES + 1):
        try:
            communicate = edge_tts.Communicate(text, VOICE)
            temp_filename = os.path.join(CACHE_DIR, f"temp_{uuid.uuid4().hex}.mp3")
            await communicate.save(temp_filename)
            
            if os.path.exists(temp_filename):
                import shutil
                shutil.move(temp_filename, filename)
                return True
        except Exception as e:
            print(f"[TTS] Generation attempt {attempt} failed: {e}")
            if attempt < MAX_TTS_RETRIES:
                await asyncio.sleep(1)
    return False

def play_audio(text):
    """
    Blocking function to generate and play audio.
    Follows the requirement to be blocking.
    """
    global is_speaking
    
    if not HAS_MIXER:
        return
    
    # Pre-processing
    safe_text = text.encode("ascii", "ignore").decode().strip()
    if not safe_text:
        return

    filename = get_cache_filename(safe_text, VOICE)
    
    # 1. Generate if not in cache
    if not os.path.exists(filename):
        success = asyncio.run(_edge_tts_generate(safe_text, filename))
        if not success:
            print("[TTS] Falling back to offline engine.")
            _offline_speak(safe_text)
            return

    # 2. Play using pygame
    try:
        if not os.path.exists(filename):
            return

        # Check if we were interrupted during generation
        if not is_speaking:
            return

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # 3. Wait until done or timeout (Safety requirement)
        start_time = time.time()
        timeout = 20  # 20s max speaking safety timeout
        
        while pygame.mixer.music.get_busy():
            if not is_speaking: # Interrupted by stop_speaking()
                pygame.mixer.music.stop()
                break
            if time.time() - start_time > timeout:
                print("[TTS] Safety timeout reached. Stopping.")
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
            
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"[TTS] Playback error: {e}")

def speak_async(text):
    """
    Asynchronous voice synthesis and playback.
    Starts a background thread and ensures only one thread runs.
    """
    global speaking_thread, is_speaking
    
    # If already speaking, stop it first
    if is_speaking:
        stop_speaking()
        # Brief wait to ensure previous thread cleanup
        time.sleep(0.2)

    def run():
        global is_speaking
        is_speaking = True
        try:
            play_audio(text)
        except Exception as e:
            print(f"[TTS] Background thread error: {e}")
        finally:
            is_speaking = False

    # Start detached background thread
    speaking_thread = threading.Thread(target=run, daemon=True)
    speaking_thread.start()

# Alias for backward compatibility
speak = speak_async

def stop_speaking():
    """Immediately stop audio playback and reset state."""
    global is_speaking
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except:
        pass
    is_speaking = False
    print("[TTS] Interrupted.")

def wait_until_done():
    """Block until the current TTS finishes playing."""
    global speaking_thread
    if speaking_thread and speaking_thread.is_alive():
        speaking_thread.join()

def _offline_speak(text):
    """Fallback to offline engine when internet drops."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            # Try to find a female/premium voice
            engine.setProperty('voice', voices[1].id)
            
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 15)
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS] Offline fallback failed: {e}")