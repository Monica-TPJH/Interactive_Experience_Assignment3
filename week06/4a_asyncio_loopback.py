import asyncio
import pyaudio
import queue

# Parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

# Thread-safe queues (use queue.Queue for cross-thread safety)
output_queue = queue.Queue()
input_queue = queue.Queue()

# Callback function for input stream
def input_callback(in_data, frame_count, time_info, status):
    try:
        input_queue.put_nowait(in_data)
    except queue.Full:
        pass
    return (None, pyaudio.paContinue)

# Callback function for output stream
def output_callback(in_data, frame_count, time_info, status):
    try:
        data = output_queue.get_nowait()
    except queue.Empty:
        # silence sized for CHUNK, FORMAT=paInt16 => 2 bytes per sample
        data = b'\x00' * CHUNK * CHANNELS * 2
    return (data, pyaudio.paContinue)

# Open input stream (remove hardcoded device index if unknown)
input_stream = p.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      input=True,
                      # input_device_index=1,  # comment out if index invalid
                      frames_per_buffer=CHUNK,
                      stream_callback=input_callback)

# Open output stream
output_stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       output=True,
                       frames_per_buffer=CHUNK,
                       stream_callback=output_callback)

async def process_audio():
    print("Loopback started. Press Ctrl+C to stop.")
    try:
        while True:
            try:
                data = input_queue.get_nowait()
                output_queue.put_nowait(data)
            except queue.Empty:
                await asyncio.sleep(0.01)
    except asyncio.CancelledError:
        print("Loopback stopped.")

# Start streams
input_stream.start_stream()
output_stream.start_stream()

# Run the event loop
try:
    asyncio.run(process_audio())
except KeyboardInterrupt:
    pass
finally:
    # Stop and close streams
    input_stream.stop_stream()
    input_stream.close()
    output_stream.stop_stream()
    output_stream.close()

    # Terminate PyAudio
    p.terminate()
