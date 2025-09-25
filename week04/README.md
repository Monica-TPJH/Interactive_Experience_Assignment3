# Week 04 - AI Chatbot Applications

This week focuses on building interactive AI chatbot applications using Streamlit and various AI backends including LMStudio and Ollama.

## 📁 Project Structure

```
week04/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── 1_user_input.py              # Basic chat input example
├── 2_user_input_with_history.py # Chat with message history
├── 3_chat_with_response.py      # Simple chat with responses
├── lmstudio_chatbot.py          # Full-featured Snoopy-themed chatbot
├── lmstudio_completion.py       # LMStudio API testing script
├── ollama_chatbot.py           # Ollama-based chatbot
├── ollama_completion.py        # Ollama API testing script
├── test_ai_servers.py          # Server connectivity testing tool
├── quick_test_lmstudio.py      # Quick LMStudio connection test
├── display_graph.py            # Graph visualization example
└── display_image.py            # Image display example
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Virtual environment activated
- Either LMStudio or Ollama installed for AI functionality

### Installation

1. **Navigate to week04 directory:**
   ```bash
   cd /path/to/your/project/week04
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up AI Backend (choose one):**

   **Option A: LMStudio Setup**
   - Download and install [LMStudio](https://lmstudio.ai)
   - Download a model (e.g., Meta-Llama-3-8B-Instruct-GGUF)
   - Go to "Local Server" tab and start server on port 1234

   **Option B: Ollama Setup**
   - Install [Ollama](https://ollama.ai)
   - Run: `ollama serve`
   - Pull a model: `ollama pull llama3`

## 🎯 Main Applications

### 🐕 Snoopy's Best Helper (Featured Application)

**File:** `lmstudio_chatbot.py`

A comprehensive, Snoopy-themed chatbot with multiple AI personalities and advanced features.

**Features:**
- 🤖 **5 AI Personalities:** General Assistant, Code Expert, Creative Writer, Fortune Teller, Teacher
- 💬 **Session Management:** Create, switch, and delete multiple chat sessions
- 🔮 **Fortune Telling:** Daily fortunes and tarot card readings
- 📊 **Statistics:** Real-time chat statistics and analytics
- ⚙️ **Configuration:** Flexible server and model settings
- 🎨 **Snoopy Theme:** Fun, friendly interface with Peanuts references

**Run the application:**
```bash
streamlit run lmstudio_chatbot.py --server.port 8509
```

**Access:** http://localhost:8509

### 📝 Basic Examples

#### 1. Simple User Input
**File:** `1_user_input.py`
- Basic chat input interface
- Displays user messages

#### 2. Chat with History
**File:** `2_user_input_with_history.py`
- Maintains conversation history
- Session state management

#### 3. Chat with AI Response
**File:** `3_chat_with_response.py`
- Basic AI response integration
- Simple request-response flow

## 🛠️ Testing Tools

### Server Connection Testing
**File:** `test_ai_servers.py`
- Tests both LMStudio and Ollama connectivity
- Provides detailed troubleshooting information
- Lists available models

**Usage:**
```bash
python test_ai_servers.py
```

### Quick LMStudio Test
**File:** `quick_test_lmstudio.py`
- Fast LMStudio connection verification
- Setup instructions if connection fails

**Usage:**
```bash
python quick_test_lmstudio.py
```

### API Testing Scripts
- **`lmstudio_completion.py`** - Test LMStudio API with error handling
- **`ollama_completion.py`** - Test Ollama API functionality

## 🎨 Visualization Examples

- **`display_graph.py`** - Streamlit graph visualization
- **`display_image.py`** - Image display functionality

## 🔧 Configuration

### Server Settings
The main chatbot allows configuration of:
- **Server URL:** Default `http://localhost:1234/v1` (LMStudio)
- **API Key:** Default `lm-studio`
- **Model Name:** Configurable model selection

### Port Management
Different applications use different ports to avoid conflicts:
- Main chatbot: Port 8509
- Other examples: Ports 8501-8508

## 🚨 Troubleshooting

### Connection Issues
If you see "Connection refused" errors:

1. **Check AI Server Status:**
   ```bash
   python test_ai_servers.py
   ```

2. **For LMStudio:**
   - Ensure LMStudio is running
   - Check Local Server tab is active
   - Verify model is loaded
   - Confirm port 1234 is open

3. **For Ollama:**
   - Run `ollama serve` in terminal
   - Verify models are installed: `ollama list`
   - Check port 11434 is available

### Common Solutions
- **Port Conflicts:** Change `--server.port` parameter
- **Model Issues:** Update model names in configuration
- **Network Problems:** Try `127.0.0.1` instead of `localhost`

## 📚 Dependencies

Key packages used:
- `streamlit` - Web app framework
- `openai` - AI API client
- `ollama` - Ollama Python client
- `requests` - HTTP requests
- `pandas` - Data handling
- `numpy` - Numerical operations

## 🎯 Learning Objectives

This week covers:
- Building interactive web applications with Streamlit
- Integrating AI APIs (OpenAI-compatible)
- Session state management
- Error handling and user feedback
- Multi-personality AI systems
- Real-time streaming responses
- Configuration management
- Testing and debugging AI applications

## 🌟 Features Highlight

### Snoopy's Best Helper Features
- **Multi-personality AI:** Switch between different AI roles
- **Session management:** Multiple concurrent conversations
- **Fortune telling:** Fun, interactive fortune and tarot features
- **Real-time statistics:** Track conversation metrics
- **Responsive design:** Works on desktop and mobile
- **Error resilience:** Graceful handling of connection issues
- **Streaming responses:** Real-time AI response display

## 📖 Usage Examples

### Starting the Main Application
```bash
# Navigate to week04
cd week04

# Run Snoopy's chatbot
streamlit run lmstudio_chatbot.py --server.port 8509
```

### Testing Connectivity
```bash
# Test all servers
python test_ai_servers.py

# Quick LMStudio test
python quick_test_lmstudio.py
```

### Running Basic Examples
```bash
# Simple input example
streamlit run 1_user_input.py

# Chat with history
streamlit run 2_user_input_with_history.py

# Full chat experience
streamlit run 3_chat_with_response.py
```

## 🏆 Success Criteria

You've successfully completed Week 04 when you can:
- ✅ Run the Snoopy chatbot application
- ✅ Switch between different AI personalities
- ✅ Create and manage multiple chat sessions
- ✅ Get AI responses to your questions
- ✅ Use the fortune telling features
- ✅ Understand the connection testing tools

## 🔗 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LMStudio Official Site](https://lmstudio.ai)
- [Ollama Official Site](https://ollama.ai)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 💡 Tips

1. **Start with testing tools** before running the main application
2. **Use different ports** for multiple applications
3. **Check server configuration** if responses aren't working
4. **Try the fortune telling** features even without AI backend
5. **Experiment with different AI personalities** for varied responses

---

**Enjoy building with AI! 🐕🤖✨**