# Alternative: Using Ollama instead of LMStudio
import ollama
import sys

print("🦙 Testing connection to Ollama server...")
print("📡 Default Ollama URL: http://localhost:11434")
print("---")

try:
    # Test if Ollama is running and has models
    models = ollama.list()
    
    if not models['models']:
        print("⚠️  No models found in Ollama!")
        print("📥 Please install a model first:")
        print("   ollama pull llama3")
        print("   or")
        print("   ollama pull llama3.2")
        sys.exit(1)
    
    print("✅ Ollama is running!")
    print("📚 Available models:")
    for model in models['models']:
        print(f"   - {model['name']}")
    
    # Use the first available model
    model_name = models['models'][0]['name']
    print(f"\n🤖 Using model: {model_name}")
    print("---")
    
    # Generate completion
    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": "Always answer in rhymes."},
            {"role": "user", "content": "Introduce yourself."}
        ]
    )
    
    print("✅ SUCCESS! Ollama connection working!")
    print("🤖 AI Response:")
    print("---")
    print(response['message']['content'])
    print("---")
    print("📊 Model used:", response['model'])
    print("⏱️  Response time:", f"{response.get('total_duration', 0) / 1000000000:.2f} seconds")
    
except ollama.ResponseError as e:
    print(f"❌ Ollama API Error: {e}")
    print("\n📋 TROUBLESHOOTING:")
    print("1. Make sure Ollama is installed: https://ollama.ai")
    print("2. Start Ollama: ollama serve")
    print("3. Pull a model: ollama pull llama3")
    
except ConnectionError:
    print("❌ ERROR: Cannot connect to Ollama server!")
    print("\n📋 TROUBLESHOOTING STEPS:")
    print("1. 📥 Install Ollama from https://ollama.ai")
    print("2. 🚀 Start Ollama server: ollama serve")
    print("3. 📦 Download a model: ollama pull llama3")
    print("4. 🔁 Run this script again")
    
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    print("\n📋 TROUBLESHOOTING:")
    print("1. Make sure Ollama is installed and running")
    print("2. Try: ollama serve")
    print("3. Try: ollama pull llama3")
    print("4. Check if port 11434 is available")