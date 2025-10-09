#!/usr/bin/env python3
"""
Text-to-Speech (TTS) Script - Fixed Version
Generate audio files from text using pyttsx3 and gTTS
(Replacing the unavailable chatterbox library)
"""

import pyttsx3
import os
from gtts import gTTS

def generate_with_pyttsx3():
    """Generate TTS using pyttsx3 (offline, cross-platform)"""
    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Configure voice settings
    engine.setProperty('rate', 200)    # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
    
    # English example
    text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
    print(f"Generating: {text}")
    engine.save_to_file(text, "test-english.wav")
    
    # Chinese example
    chinese_text = "你好，今天天气真不错，希望你有一个愉快的周末。"
    print(f"Generating: {chinese_text}")
    engine.save_to_file(chinese_text, "test-chinese.wav")
    
    # Process the queue and generate files
    engine.runAndWait()
    print("✅ Audio files generated successfully!")

def generate_with_gtts():
    """Generate TTS using Google TTS (online, high quality)"""
    try:
        # English example
        text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
        tts_en = gTTS(text=text, lang='en', slow=False)
        tts_en.save("test-english-gtts.mp3")
        
        # Chinese example  
        chinese_text = "你好，今天天气真不错，希望你有一个愉快的周末。"
        tts_zh = gTTS(text=chinese_text, lang='zh', slow=False)
        tts_zh.save("test-chinese-gtts.mp3")
        
        print("✅ Google TTS files generated successfully!")
        
    except Exception as e:
        print(f"❌ Google TTS error: {e}")
        print("   (This requires internet connection)")

if __name__ == "__main__":
    print("🎤 Text-to-Speech Generator (Fixed Version)")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Method 1: pyttsx3 (offline)
    print("\n🎵 Using pyttsx3 (offline)...")
    generate_with_pyttsx3()
    
    # Method 2: Google TTS (online) 
    print("\n🌐 Using Google TTS (online)...")
    generate_with_gtts()
    
    # List generated files
    print("\n📂 Generated files:")
    audio_files = [f for f in os.listdir('.') if f.endswith(('.wav', '.mp3')) and 'test-' in f]
    for file in sorted(audio_files):
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  📄 {file} ({size} bytes)")
    
    print("\n✅ Complete! You can play these files with any audio player.")