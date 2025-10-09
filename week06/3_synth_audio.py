# Alternative audio synthesis using PyAudio and NumPy
# Replacement for pyo library

import pyaudio
import numpy as np
import time

# Audio parameters
SAMPLE_RATE = 44100
CHUNK_SIZE = 1024

def generate_sine_wave(frequency, duration, amplitude=0.1, sample_rate=44100):
    """Generate a sine wave"""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave.astype(np.float32)

def play_audio(audio_data, sample_rate=44100):
    """Play audio data using PyAudio"""
    p = pyaudio.PyAudio()
    
    try:
        # Open stream
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=sample_rate,
            output=True
        )
        
        # Convert to bytes and play
        audio_bytes = audio_data.tobytes()
        stream.write(audio_bytes)
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        p.terminate()

# Equivalent to the original pyo script
print("Starting audio synthesis...")

# Generate a 440 Hz sine wave for 1 second (equivalent to pyo Sine(440, 0, 0.1))
audio_wave = generate_sine_wave(frequency=440, duration=1.0, amplitude=0.1)

# Play the audio (equivalent to .out() and s.start())
play_audio(audio_wave, SAMPLE_RATE)

print("finished")