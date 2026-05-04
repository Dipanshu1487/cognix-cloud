try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except (ImportError, OSError):
    HAS_SOUNDDEVICE = False

import scipy.io.wavfile as wav
import tempfile
from core.voice import speak
import core.voice
import os
import time
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        if not HAS_WHISPER:
            print("[Voice] Faster-Whisper not available in this environment.")
            return None
        _model = WhisperModel("base.en", device="cpu", compute_type="int8")
    return _model

# --- Hallucination filter ---------------------------------------------------
# Whisper hallucinates these phrases when given silence/noise, especially
# fragments of the initial_prompt or common Whisper ghost outputs.
HALLUCINATION_PHRASES = [
    "voice command",
    "smart personal assistant",
    "personal assistant",
    "examples",
    "play music",
    "open browser",
    "thank you for watching",
    "thanks for watching",
    "subscribe",
    "like and subscribe",
    "please subscribe",
    "thank you for listening",
    "thanks for listening",
    "the end",
    "i'm sorry",
    "amara.org",
    "subtitles",
    "subs by",
    "thank you.",
    "thanks.",
]


def _is_hallucination(text):
    """Return True if the text looks like a Whisper hallucination."""
    t = text.strip().lower()

    # If the whisper outputs just a single generic word, it's often a hallucinated blip
    import re
    clean_t = re.sub(r'[^\w\s]', '', t).strip()
    if clean_t in {"you", "so", "bye", "ok", "okay", "hmm", "yeah", "ah"}:
        return True

    # Check against known larger hallucination phrases
    for phrase in HALLUCINATION_PHRASES:
        if phrase in t:
            return True

    # Repeated text is a strong hallucination signal
    # e.g. "We have a voice command. We have a voice command."
    words = t.split()
    if len(words) >= 6:
        half = len(words) // 2
        first_half = " ".join(words[:half])
        second_half = " ".join(words[half:half * 2])
        if first_half == second_half:
            return True

    return False


def transcribe_audio(path):
    segments, info = get_model().transcribe(
        path,
        language="en",
        initial_prompt="Jarvis, stop, play, open, close, volume, search, remind, next, previous, pause, resume.",
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500,
            speech_pad_ms=200,
            threshold=0.5,  # Balanced VAD to handle users with noisy backgrounds
        ),
        temperature=0.0,
        condition_on_previous_text=False,
    )
    segments = list(segments)
    if not segments:
        return None

    # Filter out segments with high no-speech probability and high compression ratio
    real_segments = []
    for s in segments:
        if s.no_speech_prob > 0.6:  # Relaxed: allow speech mixed with background noise
            continue
        if s.compression_ratio > 1.6:  # High compression ratio = hallucination loop
            continue
        real_segments.append(s)

    if not real_segments:
        return None

    # Confidence check (reject very low confidence transcriptions)
    avg_conf = sum(s.avg_logprob for s in real_segments) / len(real_segments)
    if avg_conf < -0.75:
        return None

    text = "".join(s.text for s in real_segments).strip()

    # Hallucination check
    if _is_hallucination(text):
        print(f"[Filtered hallucination]: {text}")
        return None

    return text


def listen():
    """
    Dynamic Listening: Records until silence is detected or max timeout reached.
    Optimized for slightly noisy environments.
    """
    if not HAS_SOUNDDEVICE:
        print("[Voice] Microphone not available in this environment.")
        return ""
        
    print("Listening...")
    try:
        fs = 16000  # sample rate
        max_duration = 12  # absolute maximum
        silence_limit = 1.5  # stop after 1.5s of silence
        chunk_duration = 0.1  # check volume every 100ms
        chunk_samples = int(chunk_duration * fs)
        
        # Slightly noisy threshold (RMS)
        # 0.001 is very quiet, 0.005 is moderate, 0.01 is loud
        silence_threshold = 0.0008  
        
        # Hard mute gate: if Kelly is still speaking, only listen briefly for "stop"
        only_stop_mode = core.voice.is_speaking
        if only_stop_mode:
            max_duration = 1.5
            silence_limit = 0.5

        recorded_chunks = []
        silent_chunks = 0
        speech_started = False
        start_time = time.time()

        # Define the stream
        with sd.InputStream(samplerate=fs, channels=1, dtype='float32') as stream:
            while True:
                # Read a chunk
                chunk, overflowed = stream.read(chunk_samples)
                recorded_chunks.append(chunk)
                
                # Check volume (RMS)
                rms = np.sqrt(np.mean(chunk**2))
                
                elapsed = time.time() - start_time
                
                if rms > silence_threshold:
                    if not speech_started:
                        print("Speech detected...")
                        speech_started = True
                    silent_chunks = 0
                else:
                    if speech_started:
                        silent_chunks += 1
                
                # Exit conditions
                if speech_started and (silent_chunks * chunk_duration) >= silence_limit:
                    print("Silence detected, ending.")
                    break
                    
                if elapsed >= max_duration:
                    print("Maximum timeout reached.")
                    break
                
                # Small sleep to be CPU friendly if needed, but stream.read is blocking
        
        if not recorded_chunks:
            return ""

        recording = np.concatenate(recorded_chunks, axis=0)

        # Basic noise floor check to avoid transcribing blips
        rms_total = np.sqrt(np.mean(recording**2))
        if rms_total < 0.0004:
            return ""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = temp_file.name
            wav.write(temp_path, fs, recording)

        # Transcribe result once
        text = transcribe_audio(temp_path)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if not text:
            return ""

        print("You said:", text)
        
        text_l = text.lower()
        if any(w in text_l for w in ["stop", "shut up", "quiet"]):
            return "stop"
            
        if only_stop_mode:
            return ""

        return text.strip().lower()

    except Exception as e:
        print("Voice error:", e)
        return None