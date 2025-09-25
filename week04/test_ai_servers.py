#!/usr/bin/env python3
"""
Simple connection test for LMStudio and Ollama servers
"""

import requests
import json
import sys

def test_lmstudio():
    """Test LMStudio server connection"""
    print("🔍 Testing LMStudio server...")
    lm_urls = [
        "http://localhost:1234/v1/models",
        "http://127.0.0.1:1234/v1/models"
    ]
    
    for url in lm_urls:
        try:
            print(f"📡 Trying: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                models = response.json()
                print("✅ LMStudio server is running!")
                print(f"📊 Found {len(models.get('data', []))} models")
                for model in models.get('data', []):
                    print(f"   - {model.get('id', 'Unknown')}")
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
    
    return False

def test_ollama():
    """Test Ollama server connection"""
    print("\n🔍 Testing Ollama server...")
    ollama_urls = [
        "http://localhost:11434/api/tags",
        "http://127.0.0.1:11434/api/tags"
    ]
    
    for url in ollama_urls:
        try:
            print(f"📡 Trying: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                models = response.json()
                print("✅ Ollama server is running!")
                print(f"📊 Found {len(models.get('models', []))} models")
                for model in models.get('models', []):
                    print(f"   - {model.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
    
    return False

def main():
    print("🚀 AI Server Connection Test")
    print("=" * 40)
    
    lmstudio_ok = test_lmstudio()
    ollama_ok = test_ollama()
    
    print("\n" + "=" * 40)
    print("📋 SUMMARY:")
    
    if lmstudio_ok:
        print("✅ LMStudio: Ready to use!")
    else:
        print("❌ LMStudio: Not available")
        print("   💡 Start LMStudio and enable Local Server")
    
    if ollama_ok:
        print("✅ Ollama: Ready to use!")
    else:
        print("❌ Ollama: Not available") 
        print("   💡 Install Ollama from https://ollama.ai")
        print("   💡 Run: ollama serve")
        print("   💡 Pull model: ollama pull llama3")
    
    if not lmstudio_ok and not ollama_ok:
        print("\n⚠️  No AI servers are currently running!")
        print("🛠️  Please set up at least one server to use the chatbot.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())