import numpy as np
def get_dummy_audio():
    sample_rate = 16000
    duration = 5
    dummy_audio = np.random.normal(0, 0.01, size=int(sample_rate * duration))
    return dummy_audio