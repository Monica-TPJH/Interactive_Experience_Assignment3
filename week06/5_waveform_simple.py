#!/usr/bin/env python3
"""
Simple real-time audio waveform visualization
A simplified version that's easier to understand and debug
"""

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import queue
import time

class AudioVisualizer:
    def __init__(self, rate=44100, chunk=1024, channels=1):
        self.rate = rate
        self.chunk = chunk
        self.channels = channels
        self.format = pyaudio.paInt16
        
        # Buffer to store 2 seconds of audio
        self.buffer_size = 2 * rate
        self.buffer = np.zeros(self.buffer_size, dtype=np.int16)
        
        # Queue for audio data
        self.audio_queue = queue.Queue(maxsize=100)
        self.running = False
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        # Find and print available devices
        self.find_input_device()
    
    def find_input_device(self):
        """Find and display available audio input devices"""
        print("Available audio input devices:")
        input_devices = []
        
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info['name']))
                print(f"  Device {i}: {info['name']}")
        
        if not input_devices:
            print("No input devices found!")
            return None
        
        # Use default input device
        try:
            default_device = self.p.get_default_input_device_info()
            self.input_device = default_device['index']
            print(f"Using device {self.input_device}: {default_device['name']}")
        except:
            # Fallback to first available input device
            self.input_device = input_devices[0][0]
            print(f"Using fallback device {self.input_device}: {input_devices[0][1]}")
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream"""
        try:
            self.audio_queue.put_nowait(in_data)
        except queue.Full:
            pass  # Drop audio if queue is full
        return (None, pyaudio.paContinue)
    
    def process_audio(self):
        """Process audio data in separate thread"""
        print("Audio processing started...")
        while self.running:
            try:
                if not self.audio_queue.empty():
                    data = self.audio_queue.get_nowait()
                    # Convert bytes to numpy array
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Update buffer (shift old data left, add new data on right)
                    shift_amount = len(audio_data)
                    self.buffer[:-shift_amount] = self.buffer[shift_amount:]
                    self.buffer[-shift_amount:] = audio_data
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
                
            except queue.Empty:
                time.sleep(0.01)
            except Exception as e:
                print(f"Error in audio processing: {e}")
                break
    
    def start_audio_stream(self):
        """Start the audio input stream"""
        try:
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                input_device_index=self.input_device,
                stream_callback=self.audio_callback
            )
            self.stream.start_stream()
            print("Audio stream started successfully")
            return True
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            try:
                # Try without specifying device
                self.stream = self.p.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk,
                    stream_callback=self.audio_callback
                )
                self.stream.start_stream()
                print("Audio stream started with default device")
                return True
            except Exception as e2:
                print(f"Failed to start audio stream: {e2}")
                return False
    
    def start_visualization(self):
        """Start the real-time visualization"""
        if not self.start_audio_stream():
            return
        
        self.running = True
        
        # Start audio processing thread
        audio_thread = threading.Thread(target=self.process_audio, daemon=True)
        audio_thread.start()
        
        # Set up the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Time axis (in seconds)
        time_axis = np.linspace(-2, 0, self.buffer_size)
        
        line, = ax.plot(time_axis, np.zeros(self.buffer_size), 'b-', linewidth=0.5)
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Amplitude')
        ax.set_title('Real-time Audio Waveform')
        ax.set_ylim(-32768, 32767)  # Range for 16-bit audio
        ax.grid(True, alpha=0.3)
        
        def update_plot(frame):
            """Update the plot with new audio data"""
            line.set_ydata(self.buffer.copy())
            return line,
        
        # Create animation
        anim = animation.FuncAnimation(
            fig, update_plot, interval=50, blit=True, cache_frame_data=False
        )
        
        print("Visualization started. Close the window or press Ctrl+C to stop.")
        
        try:
            plt.show()
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the audio stream and cleanup"""
        print("Stopping audio visualization...")
        self.running = False
        
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        
        self.p.terminate()
        print("Audio system terminated.")


def main():
    """Main function"""
    print("Real-time Audio Waveform Visualizer")
    print("====================================")
    
    try:
        visualizer = AudioVisualizer()
        visualizer.start_visualization()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()