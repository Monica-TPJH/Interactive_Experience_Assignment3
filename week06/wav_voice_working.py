#!/usr/bin/env python3
"""
Text-to-Speech (TTS) Script
Generate audio files from text using different TTS engines
"""

import pyttsx3
import os
from gtts import gTTS
import subprocess

def create_tts_with_pyttsx3():
    """Create TTS using pyttsx3 (offline, cross-platform)"""
    print("🎤 Using pyttsx3 for offline TTS...")
    
    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Get available voices
    voices = engine.getProperty('voices')
    print(f"Available voices: {len(voices)}")
    for i, voice in enumerate(voices[:3]):  # Show first 3 voices
        print(f"  {i}: {voice.name} ({voice.languages})")
    
    # Configure voice settings
    engine.setProperty('rate', 200)    # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
    
    # Set voice (try to use a different voice if available)
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)  # Use second voice
    
    # English text
    english_text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
    print(f"Generating English audio: '{english_text[:50]}...'")
    engine.save_to_file(english_text, 'test-english-pyttsx3.wav')
    
    # Chinese text (if supported)
    chinese_text = "你好，今天天气真不错，希望你有一个愉快的周末。"
    print(f"Generating Chinese audio: '{chinese_text}'")
    engine.save_to_file(chinese_text, 'test-chinese-pyttsx3.wav')
    
    # Process the queue and generate files
    engine.runAndWait()
    print("✅ pyttsx3 audio files generated!")

def create_tts_with_gtts():
    """Create TTS using Google Text-to-Speech (online, high quality)"""
    print("\n🌐 Using Google TTS for online high-quality speech...")
    
    try:
        # English text
        english_text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
        print(f"Generating English audio: '{english_text[:50]}...'")
        
        tts_en = gTTS(text=english_text, lang='en', slow=False)
        tts_en.save("test-english-gtts.mp3")
        
        # Chinese text
        chinese_text = "你好，今天天气真不错，希望你有一个愉快的周末。"
        print(f"Generating Chinese audio: '{chinese_text}'")
        
        tts_zh = gTTS(text=chinese_text, lang='zh', slow=False)
        tts_zh.save("test-chinese-gtts.mp3")
        
        print("✅ Google TTS audio files generated!")
        
        # Convert MP3 to WAV if needed (requires ffmpeg)
        print("\n🔄 Converting MP3 to WAV format...")
        try:
            subprocess.run(['ffmpeg', '-i', 'test-english-gtts.mp3', 'test-english-gtts.wav', '-y'], 
                         check=True, capture_output=True)
            subprocess.run(['ffmpeg', '-i', 'test-chinese-gtts.mp3', 'test-chinese-gtts.wav', '-y'], 
                         check=True, capture_output=True)
            print("✅ WAV files created!")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ ffmpeg not available, keeping MP3 format")
            
    except Exception as e:
        print(f"❌ Google TTS error: {e}")
        print("   (This requires internet connection)")

def create_simple_tts():
    """Create a simple TTS function that works reliably"""
    print("\n🎵 Creating simple TTS with system defaults...")
    
    engine = pyttsx3.init()
    
    # Simple configuration
    engine.setProperty('rate', 180)
    engine.setProperty('volume', 0.8)
    
    texts_and_files = [
        ("Hello world! This is a test of text to speech.", "test-simple-english.wav"),
        ("Welcome to the audio driving game!", "test-game-welcome.wav"),
        ("Game over! Your final score is one hundred points.", "test-game-over.wav")
    ]
    
    for text, filename in texts_and_files:
        print(f"Generating: {filename}")
        engine.save_to_file(text, filename)
    
    engine.runAndWait()
    print("✅ Simple TTS files generated!")

def main():
    """Main function to run all TTS examples"""
    print("=" * 60)
    print("🎤 Text-to-Speech Generator")
    print("=" * 60)
    
    # Change to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")
    
    try:
        # Method 1: pyttsx3 (offline)
        create_tts_with_pyttsx3()
        
        # Method 2: Google TTS (online)
        create_tts_with_gtts()
        
        # Method 3: Simple reliable TTS
        create_simple_tts()
        
        # List generated files
        print("\n📂 Generated audio files:")
        audio_files = [f for f in os.listdir('.') if f.endswith(('.wav', '.mp3')) and f.startswith('test-')]
        for file in sorted(audio_files):
            size = os.path.getsize(file)
            print(f"  📄 {file} ({size} bytes)")
            
        if not audio_files:
            print("  ⚠️ No audio files were generated")
        
        print("\n✅ TTS generation complete!")
        print("💡 You can play these files with any audio player")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()