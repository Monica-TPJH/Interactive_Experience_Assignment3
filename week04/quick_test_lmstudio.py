#!/usr/bin/env python3
"""
Quick LMStudio connection test
"""
import requests
import json

def test_lmstudio_quick():
    print("🔍 Testing LMStudio connection...")
    
    try:
        # Test models endpoint
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ LMStudio server is running!")
            print(f"📊 Available models: {len(models.get('data', []))}")
            for model in models.get('data', []):
                print(f"   - {model.get('id', 'Unknown')}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n📋 TO FIX THIS:")
        print("1. 🚀 Open LMStudio application")
        print("2. 📥 Download a model (Meta-Llama-3-8B-Instruct recommended)")
        print("3. 🖥️  Go to 'Local Server' tab")
        print("4. ⚡ Select your model and click 'Start Server'")
        print("5. 🔄 Wait for 'Server started' message")
        print("6. 🔁 Run this test again")
        return False

if __name__ == "__main__":
    if test_lmstudio_quick():
        print("\n🎉 SUCCESS! Your chatbot will now be able to answer questions!")
        print("💡 Now run your Streamlit app and try chatting!")
    else:
        print("\n⚠️  LMStudio server needs to be set up first.")