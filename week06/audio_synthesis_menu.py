#!/usr/bin/env python3
"""
Audio Synthesis Examples - Complete Collection
Demonstrates multiple approaches to replace pyo functionality
"""

import sys
import os

def print_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("Audio Synthesis Examples")
    print("Alternatives to pyo library")
    print("="*50)
    print("1. Original fixed script (simple replacement)")
    print("2. PyAudio real-time synthesis")
    print("3. Pyo-like interface")
    print("4. File-based audio generation")
    print("5. Run all demos")
    print("0. Exit")
    print("-"*50)

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n🎵 Running: {description}")
    print("-" * 40)
    
    try:
        # Import and run the script
        result = os.system(f"python {script_name}")
        if result == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with code {result}")
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
    
    input("\nPress Enter to continue...")

def main():
    """Main menu system"""
    print("Welcome to Audio Synthesis Examples!")
    print("These scripts replace the pyo library functionality")
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-5): ").strip()
        
        if choice == "0":
            print("Goodbye! 👋")
            break
        elif choice == "1":
            run_script("3_synth_audio.py", 
                      "Original Script (Fixed) - Simple sine wave")
        elif choice == "2":
            run_script("3_synth_audio_pyaudio.py", 
                      "PyAudio Real-time Synthesis - Interactive demos")
        elif choice == "3":
            run_script("3_synth_audio_pyo_like.py", 
                      "Pyo-like Interface - Familiar API")
        elif choice == "4":
            run_script("3_synth_audio_files.py", 
                      "File-based Generation - WAV output")
        elif choice == "5":
            print("\n🎼 Running all demos in sequence...")
            scripts = [
                ("3_synth_audio.py", "Fixed Original"),
                ("3_synth_audio_files.py", "File Generation"),
                ("3_synth_audio_pyaudio.py", "Interactive PyAudio"),
            ]
            
            for script, desc in scripts:
                run_script(script, desc)
            
            print("\n🎉 All demos completed!")
            input("Press Enter to continue...")
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"\nUnexpected error: {e}")