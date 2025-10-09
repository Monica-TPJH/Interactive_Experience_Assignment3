#!/usr/bin/env python3
"""
Audio synthesis with file output
Generate audio and save to WAV files using soundfile
"""

import numpy as np
import soundfile as sf
import time

def generate_sine_wave(frequency, duration, amplitude=0.1, sample_rate=44100):
    """Generate a sine wave"""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def generate_complex_wave(frequencies, duration, amplitude=0.1, sample_rate=44100):
    """Generate a complex wave with multiple frequencies"""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    
    wave = np.zeros(samples)
    for freq in frequencies:
        wave += amplitude * np.sin(2 * np.pi * freq * t) / len(frequencies)
    
    return wave

def save_audio(audio_data, filename, sample_rate=44100):
    """Save audio data to a WAV file"""
    try:
        sf.write(filename, audio_data, sample_rate)
        print(f"Audio saved to: {filename}")
    except Exception as e:
        print(f"Error saving audio: {e}")

def main():
    """Generate various audio examples and save them"""
    print("Audio Synthesis with File Output")
    print("=================================")
    
    sample_rate = 44100
    
    # 1. Simple sine wave (equivalent to original pyo script)
    print("1. Generating 440 Hz sine wave (1 second)...")
    sine_wave = generate_sine_wave(440, 1.0, 0.1, sample_rate)
    save_audio(sine_wave, "sine_440hz.wav", sample_rate)
    
    # 2. Musical chord (C major triad)
    print("2. Generating C major chord (261 + 329 + 392 Hz)...")
    chord_frequencies = [261.63, 329.63, 392.00]  # C, E, G
    chord_wave = generate_complex_wave(chord_frequencies, 2.0, 0.05, sample_rate)
    save_audio(chord_wave, "c_major_chord.wav", sample_rate)
    
    # 3. Simple melody
    print("3. Generating simple melody...")
    notes = [
        (261.63, 0.5),  # C
        (293.66, 0.5),  # D
        (329.63, 0.5),  # E
        (349.23, 0.5),  # F
        (392.00, 1.0),  # G (longer)
    ]
    
    melody = np.array([])
    for freq, duration in notes:
        note = generate_sine_wave(freq, duration, 0.1, sample_rate)
        melody = np.concatenate([melody, note])
    
    save_audio(melody, "simple_melody.wav", sample_rate)
    
    # 4. Frequency sweep
    print("4. Generating frequency sweep (100-1000 Hz)...")
    duration = 3.0
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, False)
    
    # Linear frequency sweep from 100 to 1000 Hz
    freq_start = 100
    freq_end = 1000
    freq_sweep = freq_start + (freq_end - freq_start) * t / duration
    phase = 2 * np.pi * np.cumsum(freq_sweep) / sample_rate
    sweep_wave = 0.1 * np.sin(phase)
    
    save_audio(sweep_wave, "frequency_sweep.wav", sample_rate)
    
    print("\nAudio generation complete!")
    print("Generated files:")
    print("- sine_440hz.wav (simple sine wave)")
    print("- c_major_chord.wav (musical chord)")
    print("- simple_melody.wav (note sequence)")
    print("- frequency_sweep.wav (frequency sweep)")

if __name__ == "__main__":
    main()