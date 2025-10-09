#!/usr/bin/env python3
"""
Audio synthesis using PyAudio and NumPy
Alternative to pyo for generating sine waves and playing audio
"""

import pyaudio
import numpy as np
import time
import threading

class AudioSynthesizer:
    def __init__(self, sample_rate=44100, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.format = pyaudio.paFloat32
        self.channels = 1
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.playing = False
        
        # Audio generation parameters
        self.frequency = 440.0  # A4 note
        self.amplitude = 0.1
        self.phase = 0.0
        
    def generate_sine_wave(self, duration):
        """Generate a sine wave for the specified duration"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        wave = self.amplitude * np.sin(2 * np.pi * self.frequency * t)
        return wave.astype(np.float32)
    
    def generate_chunk(self):
        """Generate one chunk of audio data"""
        duration = self.chunk_size / self.sample_rate
        t = np.linspace(self.phase, self.phase + duration, self.chunk_size, False)
        chunk = self.amplitude * np.sin(2 * np.pi * self.frequency * t)
        self.phase += duration
        return chunk.astype(np.float32)
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for real-time audio generation"""
        if self.playing:
            data = self.generate_chunk()
        else:
            data = np.zeros(frame_count, dtype=np.float32)
        
        return (data.tobytes(), pyaudio.paContinue)
    
    def start_stream(self):
        """Start the audio output stream"""
        try:
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
            self.stream.start_stream()
            print(f"Audio stream started - Sample rate: {self.sample_rate} Hz")
            return True
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            return False
    
    def play_tone(self, frequency, duration, amplitude=0.1):
        """Play a single tone"""
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = 0.0
        
        if not self.stream or not self.stream.is_active():
            if not self.start_stream():
                return
        
        print(f"Playing {frequency} Hz for {duration} seconds...")
        self.playing = True
        time.sleep(duration)
        self.playing = False
    
    def play_wave_data(self, wave_data):
        """Play pre-generated wave data"""
        try:
            # Convert to bytes
            audio_data = wave_data.astype(np.float32).tobytes()
            
            # Create a simple blocking stream for playback
            stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True
            )
            
            # Play the audio in chunks
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size * 4):  # 4 bytes per float32
                chunk = audio_data[i:i + chunk_size * 4]
                stream.write(chunk)
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def stop(self):
        """Stop the audio stream and cleanup"""
        self.playing = False
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        print("Audio system stopped.")


def demo_sine_wave():
    """Demo function similar to the original pyo script"""
    print("Audio Synthesis Demo (PyAudio + NumPy)")
    print("=====================================")
    
    synth = AudioSynthesizer()
    
    try:
        # Method 1: Real-time streaming (similar to pyo)
        print("\n1. Real-time sine wave (440 Hz, 1 second)")
        synth.play_tone(frequency=440, duration=1.0, amplitude=0.1)
        
        time.sleep(0.5)  # Brief pause
        
        # Method 2: Pre-generated wave
        print("\n2. Pre-generated sine wave (880 Hz, 0.5 seconds)")
        wave = synth.generate_sine_wave(duration=0.5)
        synth.frequency = 880
        synth.amplitude = 0.1
        synth.play_wave_data(wave)
        
        print("\nDemo finished!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    finally:
        synth.stop()


def musical_scale_demo():
    """Play a simple musical scale"""
    print("\nMusical Scale Demo")
    print("==================")
    
    # Musical notes (frequencies in Hz)
    notes = {
        'C4': 261.63,
        'D4': 293.66,
        'E4': 329.63,
        'F4': 349.23,
        'G4': 392.00,
        'A4': 440.00,
        'B4': 493.88,
        'C5': 523.25
    }
    
    synth = AudioSynthesizer()
    
    try:
        for note_name, frequency in notes.items():
            print(f"Playing {note_name} ({frequency:.2f} Hz)")
            synth.play_tone(frequency=frequency, duration=0.5, amplitude=0.1)
            time.sleep(0.1)  # Brief pause between notes
            
    except KeyboardInterrupt:
        print("\nScale interrupted by user")
    finally:
        synth.stop()


def main():
    """Main function with multiple demo options"""
    print("Audio Synthesis Examples")
    print("========================")
    print("1. Basic sine wave demo (similar to original pyo script)")
    print("2. Musical scale demo")
    print("3. Custom frequency")
    
    choice = input("\nEnter your choice (1-3) or press Enter for basic demo: ").strip()
    
    if choice == "2":
        musical_scale_demo()
    elif choice == "3":
        try:
            freq = float(input("Enter frequency (Hz): "))
            duration = float(input("Enter duration (seconds): "))
            
            synth = AudioSynthesizer()
            synth.play_tone(frequency=freq, duration=duration, amplitude=0.1)
            synth.stop()
            
        except ValueError:
            print("Invalid input. Using default values.")
            demo_sine_wave()
        except KeyboardInterrupt:
            print("\nStopped by user")
    else:
        demo_sine_wave()


if __name__ == "__main__":
    main()