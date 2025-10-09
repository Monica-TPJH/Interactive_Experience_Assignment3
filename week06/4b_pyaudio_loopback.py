import pyaudio
import sys
import time

# Parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

def choose_input_device(pa):
    try:
        info = pa.get_default_input_device_info()
        return int(info["index"])
    except Exception:
        # find first device with input channels
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if int(info.get("maxInputChannels", 0)) > 0:
                return i
    return None

input_idx = choose_input_device(p)
if input_idx is None:
    print("No input device found. Run the device listing snippet to inspect devices.")
    p.terminate()
    sys.exit(1)

print(f"Using input device index: {input_idx}")

try:
    input_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=input_idx,
        frames_per_buffer=CHUNK
    )
except Exception as e:
    print("Failed to open input stream:", e)
    p.terminate()
    sys.exit(1)

try:
    output_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK
    )
except Exception as e:
    print("Failed to open output stream:", e)
    input_stream.close()
    p.terminate()
    sys.exit(1)

print("Loopback started. Press Ctrl+C to stop.")
try:
    while True:
        try:
            # set exception_on_overflow=False to avoid IOError on overflow
            data = input_stream.read(CHUNK, exception_on_overflow=False)
            output_stream.write(data)
        except IOError as e:
            # handle occasional overflow/underflow
            print("IOError during read/write:", e)
            time.sleep(0.01)
        except KeyboardInterrupt:
            break
except KeyboardInterrupt:
    pass
finally:
    print("Stopping streams...")
    try:
        input_stream.stop_stream()
        input_stream.close()
    except Exception:
        pass
    try:
        output_stream.stop_stream()
        output_stream.close()
    except Exception:
        pass
    p.terminate()
    print("Terminated.")