import pvporcupine
import pyaudio
import struct
import time
import threading
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "r2EDEcL3thsmBCUVT8CtKO8kythWo9BLrL30AR5aomQZYhlCL+eIEA==")

class WakeWordDetector:
    """
    Stabilized cogniX Wake Word System.
    Provides non-blocking, reliable detection with lightweight fallback.
    """
    def __init__(self):
        self._pa = pyaudio.PyAudio()
        self._porcupine = None
        self._audio_stream = None
        self._is_running = False
        self._detected_event = threading.Event()
        self._detected_command = True
        self._porcupine_disabled = False
        self._thread = None
        
        # Validation constants
        self._energy_threshold = 1000  # RMS threshold for fallback trigger
        self._mic_retries = 1
        
    def _validate_porcupine(self):
        """One-time validation of Porcupine engine."""
        if self._porcupine_disabled:
            return False
            
        try:
            # Check key length/format sanity (simple check)
            if not ACCESS_KEY or ACCESS_KEY == "r2EDEcL3thsmBCUVT8CtKO8kythWo9BLrL30AR5aomQZYhlCL+eIEA==" or len(ACCESS_KEY) < 20:
                print("Porcupine disabled (invalid or missing key)")
                self._porcupine_disabled = True
                return False
                
            self._porcupine = pvporcupine.create(
                access_key=ACCESS_KEY,
                keywords=["jarvis"]
            )
            return True
        except Exception as e:
            print("Porcupine disabled (invalid or missing key)")
            self._porcupine_disabled = True
            return False

    def _open_stream(self, rate, frame_length):
        """Open audio stream with single-retry logic."""
        for attempt in range(self._mic_retries + 1):
            try:
                stream = self._pa.open(
                    rate=rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=frame_length,
                )
                return stream
            except Exception as e:
                print(f"[Wake Word] Mic error (attempt {attempt+1}/{self._mic_retries+1}): {e}")
                if attempt < self._mic_retries:
                    time.sleep(1)
        return None

    def start(self):
        """Start non-blocking detection in a background thread."""
        if self._is_running:
            return
            
        self._is_running = True
        self._detected_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("Wake word listening started")

    def stop(self):
        """Stop detection and clean up resources."""
        self._is_running = False
        if self._thread:
            self._thread.join(timeout=2)
        self._cleanup()

    def _cleanup(self):
        """Safe cleanup of all audio resources."""
        try:
            if self._audio_stream:
                self._audio_stream.stop_stream()
                self._audio_stream.close()
                self._audio_stream = None
        except: pass
        
        try:
            if self._porcupine:
                self._porcupine.delete()
                self._porcupine = None
        except: pass
        
        # Note: We don't terminate PyAudio here to allow reuse in next start()
        # but we could do it in a final destructor.

    def wait_for_wake_word(self):
        """Block the calling thread until wake word is detected."""
        self._detected_event.wait()
        self._detected_event.clear()
        cmd = self._detected_command
        self._detected_command = True  # reset to default
        return cmd

    def _run_loop(self):
        """Main detection loop (threaded)."""
        # 1. Try Porcupine first
        mode_porcupine = self._validate_porcupine()
        
        if mode_porcupine:
            rate = self._porcupine.sample_rate
            frame_length = self._porcupine.frame_length
        else:
            print("[Wake Word] Fallback active")
            rate = 16000
            frame_length = 512  # Standard chunk for energy detection

        # 2. Open Stream
        self._audio_stream = self._open_stream(rate, frame_length)
        if not self._audio_stream:
            print("[Wake Word] CRITICAL: Failed to initialize microphone. Exiting system.")
            self._is_running = False
            return

        while self._is_running:
            try:
                # CPU Stability Delay
                time.sleep(0.01)
                
                pcm_data = self._audio_stream.read(frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * frame_length, pcm_data)

                if mode_porcupine:
                    # High-performance Porcupine check
                    keyword_index = self._porcupine.process(pcm)
                    if keyword_index >= 0:
                        print("Wake word detected")
                        self._detected_command = True
                        self._detected_event.set()
                        # Pause internal loop while detected (main thread handles interaction)
                        while self._detected_event.is_set() and self._is_running:
                            time.sleep(0.1)
                else:
                    # Lightweight Energy-based Fallback
                    energy = np.sqrt(np.mean(np.array(pcm)**2))
                    if energy > self._energy_threshold:
                        print("Wake word required")
                        # Peak detected, perform a quick transcription check
                        # We use the main listener here to avoid duplicate Whisper instances
                        from core.listener import listen
                        # Small buffer to let the user finish saying "Jarvis" if they just started
                        time.sleep(0.2) 
                        text = listen()
                        if text and "cognix" in text.lower():
                            print("Wake word detected")
                            self._detected_command = text
                            self._detected_event.set()
                            while self._detected_event.is_set() and self._is_running:
                                time.sleep(0.1)


            except Exception as e:
                print(f"[Wake Word] Loop error: {e}")
                time.sleep(1)

        self._cleanup()

    def __del__(self):
        try:
            self._pa.terminate()
        except: pass

# Global singleton for easy import
detector = WakeWordDetector()

def detect_wake_word():
    """Legacy compatibility wrapper."""
    detector.start()
    detector.wait_for_wake_word()
    detector.stop()