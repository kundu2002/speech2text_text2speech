import sys
import numpy as np
from unittest.mock import MagicMock
mock_sd = MagicMock()
def mock_rec(frames, samplerate=44100, channels=1, dtype='float32'):
    duration = frames / samplerate
    print(f"MOCK: Recording {duration} seconds of audio...")
    return np.zeros((frames, channels), dtype=dtype)
def mock_wait():
    print("MOCK: Waiting for recording to complete...")
    return None
mock_sd.rec = mock_rec
mock_sd.wait = mock_wait
try:
    import sounddevice as real_sd
    devices = real_sd.query_devices()
    print("Real audio devices found. Using actual sounddevice module.")
except Exception as e:
    print(f"No audio devices found or error accessing them: {e}")
    print("Using mock sounddevice module for cloud compatibility.")
    sys.modules['sounddevice'] = mock_sd