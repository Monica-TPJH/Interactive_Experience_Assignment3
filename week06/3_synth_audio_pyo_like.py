#!/usr/bin/env python3
"""
Pyo-like interface using PyAudio
Provides a similar API to make migration from pyo easier
"""

import pyaudio
import numpy as np
import time
import threading

class Server:
    """Audio server class similar to pyo.Server"""
    
    def __init__(self, sr=44100, nchnls=2, buffersize=1024):
        self.sr = sr
        self.nchnls = nchnls
        self.buffersize = buffersize
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.objects = []
        
    def boot(self):
        """Initialize the server"""
        print(f"Audio server booted: {self.sr} Hz, {self.nchnls} channels")
        return self
    
    def start(self):
        """Start the audio server"""
        if not self.running:
            self.running = True
            self._start_stream()
            print("Audio server started")
    
    def stop(self):
        """Stop the audio server"""
        self.running = False
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        print("Audio server stopped")
    
    def shutdown(self):
        """Shutdown the server completely"""
        self.stop()
        self.p.terminate()
        print("Audio server shutdown")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio callback function"""
        if self.running and self.objects:
            # Mix all active audio objects
            output = np.zeros(frame_count, dtype=np.float32)
            for obj in self.objects:
                if hasattr(obj, 'get_samples'):
                    samples = obj.get_samples(frame_count)
                    output += samples
            
            # Convert mono to stereo if needed
            if self.nchnls == 2:
                output = np.column_stack((output, output))
            
            return (output.tobytes(), pyaudio.paContinue)
        else:
            # Silence
            if self.nchnls == 2:
                silence = np.zeros((frame_count, 2), dtype=np.float32)
            else:
                silence = np.zeros(frame_count, dtype=np.float32)
            return (silence.tobytes(), pyaudio.paContinue)
    
    def _start_stream(self):
        """Start the PyAudio stream"""
        try:
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.nchnls,
                rate=self.sr,
                output=True,
                frames_per_buffer=self.buffersize,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
        except Exception as e:
            print(f"Error starting audio stream: {e}")
    
    def add_object(self, obj):
        """Add an audio object to the server"""
        if obj not in self.objects:
            self.objects.append(obj)
            obj.server = self
    
    def remove_object(self, obj):
        """Remove an audio object from the server"""
        if obj in self.objects:
            self.objects.remove(obj)


class Sine:
    """Sine wave generator similar to pyo.Sine"""
    
    def __init__(self, freq=440, phase=0, mul=1.0):
        self.freq = freq
        self.phase = phase
        self.mul = mul
        self.current_phase = 0.0
        self.server = None
        self.playing = False
    
    def get_samples(self, num_samples):
        """Generate audio samples"""
        if not self.playing:
            return np.zeros(num_samples, dtype=np.float32)
        
        sr = self.server.sr if self.server else 44100
        dt = 1.0 / sr
        
        samples = np.zeros(num_samples, dtype=np.float32)
        for i in range(num_samples):
            samples[i] = self.mul * np.sin(2 * np.pi * self.freq * self.current_phase + self.phase)
            self.current_phase += dt
        
        return samples
    
    def out(self, chnl=0):
        """Send to output (similar to pyo)"""
        if hasattr(self, 'server') and self.server:
            self.server.add_object(self)
        self.playing = True
        return self
    
    def stop(self):
        """Stop the sine wave"""
        self.playing = False
        if hasattr(self, 'server') and self.server:
            self.server.remove_object(self)


# Create a global server instance for convenience
_global_server = None

def get_server():
    """Get or create the global server instance"""
    global _global_server
    if _global_server is None:
        _global_server = Server()
    return _global_server


# Example usage that matches the original pyo script exactly
def pyo_compatible_demo():
    """Demo that uses the same syntax as the original pyo script"""
    print("Pyo-compatible audio synthesis demo")
    print("===================================")
    
    # Create server (equivalent to pyo)
    s = Server().boot()
    
    # Create sine wave (equivalent to pyo)
    a = Sine(440, 0, 0.1).out()
    
    # Start server and play
    s.start()
    time.sleep(1)
    s.stop()
    
    print("finished")


def extended_demo():
    """Extended demo showing more capabilities"""
    print("Extended audio synthesis demo")
    print("=============================")
    
    s = Server().boot()
    
    # Play a sequence of notes
    frequencies = [440, 523, 659, 784]  # A, C, E, G
    
    for freq in frequencies:
        print(f"Playing {freq} Hz...")
        a = Sine(freq, 0, 0.1).out()
        s.start()
        time.sleep(0.5)
        a.stop()
        s.stop()
        time.sleep(0.1)
    
    s.shutdown()
    print("Extended demo finished")


if __name__ == "__main__":
    print("Pyo-like Audio Synthesis")
    print("========================")
    print("1. Original pyo script equivalent")
    print("2. Extended demo with multiple notes")
    
    choice = input("Choose demo (1-2) or press Enter for original: ").strip()
    
    try:
        if choice == "2":
            extended_demo()
        else:
            pyo_compatible_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    except Exception as e:
        print(f"Error: {e}")