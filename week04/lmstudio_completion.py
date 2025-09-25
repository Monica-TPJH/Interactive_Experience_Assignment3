# Example: reuse your existing OpenAI setup
from openai import OpenAI
import sys

# Point to the local server
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

print("🤖 Testing connection to LMStudio server...")
print("📡 Server URL: http://127.0.0.1:1234/v1")
print("---")

try:
    completion = client.chat.completions.create(
      model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
      messages=[
        {"role": "system", "content": "Always answer in rhymes."},
        {"role": "user", "content": "Introduce yourself."}
      ],
      temperature=0.7,
    )
    
    print("✅ SUCCESS! LMStudio connection working!")
    print("🤖 AI Response:")
    print("---")
    print(completion.choices[0].message.content)
    print("---")
    print("📊 Model used:", completion.model)
    print("💫 Response ID:", completion.id)
    
except Exception as e:
    print("❌ ERROR: Cannot connect to LMStudio server!")
    print(f"🔧 Error details: {str(e)}")
    print("\n📋 TROUBLESHOOTING STEPS:")
    print("1. 🚀 Open LMStudio application")
    print("2. 📥 Download and load a model (e.g., Meta-Llama-3-8B-Instruct)")
    print("3. 🖥️  Go to 'Local Server' tab in LMStudio")
    print("4. ⚡ Click 'Start Server' (should run on port 1234)")
    print("5. 🔄 Wait for server to start (you'll see 'Server started' message)")
    print("6. 🔁 Run this script again")
    print("\n💡 Alternative: You can also try Ollama instead:")
    print("   - Install Ollama: https://ollama.ai")
    print("   - Run: ollama serve")
    print("   - Run: ollama run llama3")
    
    sys.exit(1)