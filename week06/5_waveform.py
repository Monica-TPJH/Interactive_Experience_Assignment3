import threading
import pyaudio
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue

# Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
ROLLING_WINDOW = 2 * RATE  # 2 seconds rolling window

# Initialize PyAudio
p = pyaudio.PyAudio()
audio_queue = queue.Queue()
buffer = np.zeros(ROLLING_WINDOW, dtype=np.int16)
running = True

# Function to list audio devices and find a suitable input device
def find_input_device():
    print("Available audio devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"Device {i}: {info['name']} - Inputs: {info['maxInputChannels']}")
    
    # Find default input device or first device with input channels
    default_input = p.get_default_input_device_info()
    if default_input['maxInputChannels'] > 0:
        return default_input['index']
    
    # Fallback: find any device with input channels
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            return i
    return None

# Find appropriate input device
input_device_index = find_input_device()
print(f"Using input device: {input_device_index}")

# Callback function for input stream
def input_callback(in_data, frame_count, time_info, status):
    if not audio_queue.full():
        audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

# Open stream with error handling
try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=input_device_index,
                    stream_callback=input_callback)
except Exception as e:
    print(f"Error opening audio stream: {e}")
    # Try without specifying device
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=input_callback)

# Function to process audio data
def process_audio():
    global buffer, running
    print("Audio processing started. Press Ctrl+C to stop.")
    while running:
        try:
            if not audio_queue.empty():
                data = audio_queue.get_nowait()
                waveform = np.frombuffer(data, dtype=np.int16)
                # Roll buffer and add new data
                buffer = np.roll(buffer, -len(waveform))
                buffer[-len(waveform):] = waveform
            time.sleep(0.01)
        except queue.Empty:
            time.sleep(0.01)
        except Exception as e:
            print(f"Error processing audio: {e}")
            break

def update_plot():
    global buffer, running
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(0, ROLLING_WINDOW)
    line, = ax.plot(x, np.zeros(ROLLING_WINDOW))
    ax.set_ylabel('Amplitude')
    ax.set_xlabel('Samples')
    ax.set_title('Real-time Audio Waveform')
    ax.set_ylim(-32768, 32767)  # int16 range
    ax.grid(True, alpha=0.3)

    def update_frame(frame):
        global buffer
        line.set_ydata(buffer.copy())
        return line,

    # Start audio processing in background thread
    audio_thread = threading.Thread(target=process_audio, daemon=True)
    audio_thread.start()

    anim = animation.FuncAnimation(fig, update_frame, blit=False, interval=50, cache_frame_data=False)
    
    try:
        plt.show()
    except KeyboardInterrupt:
        running = False

# Main function
def main():
    global running
    try:
        # Start the stream
        stream.start_stream()
        print("Stream started. Close the plot window or press Ctrl+C to stop.")
        
        # Start plotting
        update_plot()
        
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        running = False
        # Stop and close streams
        if stream.is_active():
            stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio terminated.")

if __name__ == "__main__":
    main()