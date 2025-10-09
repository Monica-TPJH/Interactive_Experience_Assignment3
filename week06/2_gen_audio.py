import sys
import traceback
import numpy as np

try:
    import torch
except Exception as e:
    print("Missing torch. Run: python -m pip install torch", file=sys.stderr)
    raise

# diffusers import may fail if versions mismatch
try:
    from diffusers import AudioLDM2Pipeline, DPMSolverMultistepScheduler
except Exception:
    print("Missing or incompatible diffusers. Run: python -m pip install 'diffusers[torch]' transformers accelerate", file=sys.stderr)
    raise

# optional audio backends
try:
    import pyaudio
except Exception:
    pyaudio = None

def choose_device_and_dtype():
    if torch.cuda.is_available():
        return "cuda", torch.float16
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", torch.float32
    return "cpu", torch.float32

device, torch_dtype = choose_device_and_dtype()
print(f"Using device={device}, torch_dtype={torch_dtype}")

# Load pipeline with robust error reporting
try:
    pipeline = AudioLDM2Pipeline.from_pretrained("cvssp/audioldm2-music", torch_dtype=torch_dtype)
except Exception as e:
    traceback.print_exc()
    print("Failed to load pipeline. Possible causes: missing HF tokens, network, or incompatible package versions.", file=sys.stderr)
    sys.exit(1)

# try to move to device, handle failures gracefully
try:
    pipeline.to(device)
except Exception:
    traceback.print_exc()
    print("Failed to move pipeline to device; falling back to CPU", file=sys.stderr)
    pipeline.to("cpu")
    device = "cpu"
    torch_dtype = torch.float32

# replace scheduler for faster inference
try:
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
    print("Using DPMSolverMultistepScheduler for faster generation")
except Exception as e:
    print(f"Could not set scheduler: {e}, using default")

# Enable memory efficient attention if available
try:
    pipeline.enable_attention_slicing()
    print("Enabled attention slicing for memory efficiency")
except Exception:
    pass

# Audio playback setup
SAMPLE_RATE = 16000  # AudioLDM2 default sample rate
audio_stream = None
p_audio = None

def setup_audio_playback():
    global audio_stream, p_audio
    if pyaudio is None:
        print("PyAudio not available. Audio will be saved to files instead.")
        return False
    
    try:
        p_audio = pyaudio.PyAudio()
        audio_stream = p_audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=SAMPLE_RATE,
            output=True,
            frames_per_buffer=1024
        )
        print("Audio playback initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize audio playback: {e}")
        if p_audio:
            p_audio.terminate()
        return False

def play_audio(audio_array):
    """Play audio array through speakers or save to file"""
    if audio_stream is not None:
        try:
            # Ensure audio is float32 and in correct range
            audio = np.array(audio_array, dtype=np.float32)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)  # Convert to mono
            
            # Normalize to [-1, 1] range
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.8
            
            audio_stream.write(audio.tobytes())
            print("✓ Audio played successfully")
        except Exception as e:
            print(f"Error playing audio: {e}")
            save_audio_to_file(audio_array)
    else:
        save_audio_to_file(audio_array)

def save_audio_to_file(audio_array, filename=None):
    """Save audio to WAV file"""
    try:
        import soundfile as sf
        if filename is None:
            import time
            filename = f"generated_audio_{int(time.time())}.wav"
        
        audio = np.array(audio_array, dtype=np.float32)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        
        sf.write(filename, audio, SAMPLE_RATE)
        print(f"✓ Audio saved to {filename}")
    except ImportError:
        print("soundfile not available. Install with: pip install soundfile")
    except Exception as e:
        print(f"Error saving audio: {e}")

# Initialize audio playback
audio_available = setup_audio_playback()

print(f"🎵 Audio generation ready! Device: {device}")
print("Enter your music description (or 'quit' to exit)")

try:
    while True:
        prompt = input("\n🎼 Describe the music you want: ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            break
        
        if not prompt:
            continue
        
        print(f"🎯 Generating audio for: '{prompt}'")
        print("⏳ This may take 30-60 seconds...")
        
        try:
            # Generate audio with reasonable parameters
            result = pipeline(
                prompt,
                num_inference_steps=50,  # Reduced for faster generation
                audio_length_in_s=10.0,  # 10 second clips
                guidance_scale=2.5,      # Moderate guidance
            )
            
            # Extract audio from result
            if hasattr(result, 'audios') and result.audios:
                audio = result.audios[0]
                print("🎉 Audio generated successfully!")
                play_audio(audio)
            else:
                print("❌ No audio generated")
                
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            traceback.print_exc()
            continue

except KeyboardInterrupt:
    print("\n👋 Stopped by user")

finally:
    # Cleanup audio resources
    try:
        if audio_stream:
            audio_stream.stop_stream()
            audio_stream.close()
        if p_audio:
            p_audio.terminate()
        print("🧹 Audio resources cleaned up")
    except Exception:
        pass
