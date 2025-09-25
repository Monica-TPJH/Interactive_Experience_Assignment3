import streamlit as st
from openai import OpenAI

# Configure page
st.set_page_config(
    page_title="Snoopy's best helper",
    page_icon="�",
    layout="wide"
)

# Initialize session states
if "current_robot" not in st.session_state:
    st.session_state["current_robot"] = "General Assistant"
if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = {}
if "current_session" not in st.session_state:
    st.session_state["current_session"] = "Default Chat"

# Robot configurations
ROBOTS = {
    "General Assistant": {
        "icon": "🤖",
        "description": "A helpful general-purpose AI assistant",
        "system_prompt": "You are Snoopy's best helper, a friendly and loyal AI assistant. Be helpful, cheerful, and occasionally reference Snoopy's world when appropriate."
    },
    "Code Expert": {
        "icon": "💻", 
        "description": "Expert programmer and code reviewer",
        "system_prompt": "You are Snoopy's coding buddy - an expert programmer who helps with coding questions, debugging, and code reviews. Be as loyal and determined as Snoopy!"
    },
    "Creative Writer": {
        "icon": "✍️",
        "description": "Creative writing and storytelling assistant", 
        "system_prompt": "You are Snoopy's creative writing companion. Help with stories, poems, and creative content. Channel Snoopy's imagination and creativity!"
    },
    "Fortune Teller": {
        "icon": "🔮",
        "description": "Mystical fortune teller and advisor",
        "system_prompt": "You are Snoopy's mystical advisor. Provide fortune readings, tarot interpretations, and mystical advice with the wisdom of the World War I Flying Ace!"
    },
    "Teacher": {
        "icon": "👨‍🏫",
        "description": "Educational tutor and explainer",
        "system_prompt": "You are Snoopy's wise teacher companion. Explain concepts clearly and help with learning, just like how Snoopy would patiently teach Woodstock!"
    }
}

# Sidebar configuration
st.sidebar.title("🐕 Snoopy's Helpers")

# Robot selector
selected_robot = st.sidebar.selectbox(
    "Choose your AI companion:",
    list(ROBOTS.keys()),
    index=list(ROBOTS.keys()).index(st.session_state["current_robot"])
)

if selected_robot != st.session_state["current_robot"]:
    st.session_state["current_robot"] = selected_robot

# Display robot info
robot_info = ROBOTS[selected_robot]
st.sidebar.markdown(f"### {robot_info['icon']} {selected_robot}")
st.sidebar.write(robot_info['description'])

st.sidebar.markdown("---")

# Chat Sessions Management
st.sidebar.markdown("### � Chat Sessions")

# Session selector
session_names = list(st.session_state["chat_sessions"].keys()) + ["Create New Session"]
if st.session_state["current_session"] not in st.session_state["chat_sessions"]:
    st.session_state["chat_sessions"][st.session_state["current_session"]] = [{"role": "assistant", "content": "How can I help you?"}]

selected_session = st.sidebar.selectbox(
    "Select chat session:",
    session_names,
    index=0 if st.session_state["current_session"] not in session_names else session_names.index(st.session_state["current_session"])
)

# Handle new session creation
if selected_session == "Create New Session":
    new_session_name = st.sidebar.text_input("New session name:", value=f"Chat {len(st.session_state['chat_sessions']) + 1}")
    if st.sidebar.button("Create Session"):
        if new_session_name and new_session_name not in st.session_state["chat_sessions"]:
            st.session_state["chat_sessions"][new_session_name] = [{"role": "assistant", "content": "Woof! I'm here to help you! What can Snoopy's best helper do for you today? 🐾"}]
            st.session_state["current_session"] = new_session_name
            st.rerun()
else:
    st.session_state["current_session"] = selected_session

# Session management buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🗑️ Delete Session") and len(st.session_state["chat_sessions"]) > 1:
        del st.session_state["chat_sessions"][st.session_state["current_session"]]
        st.session_state["current_session"] = list(st.session_state["chat_sessions"].keys())[0]
        st.rerun()

with col2:
    if st.button("🧹 Clear Session"):
        st.session_state["chat_sessions"][st.session_state["current_session"]] = [{"role": "assistant", "content": "Woof! I'm here to help you! What can Snoopy's best helper do for you today? 🐾"}]
        st.rerun()

st.sidebar.markdown("---")

# Fortune Telling Section
st.sidebar.markdown("### 🔮 Fortune Telling")
if st.sidebar.button("🌟 Get Daily Fortune"):
    import random
    fortunes = [
        "Today brings new opportunities your way! 🌈",
        "A pleasant surprise awaits you this afternoon! 🎁", 
        "Your creativity will shine brightly today! ✨",
        "Good news is coming from an unexpected source! 📬",
        "Today is perfect for making new connections! 🤝",
        "Trust your intuition - it will guide you well! 🧭",
        "A small act of kindness will bring great joy! 💝",
        "Success is within reach - keep pushing forward! 🎯"
    ]
    st.sidebar.success(f"**Your Fortune:** {random.choice(fortunes)}")

if st.sidebar.button("🎴 Quick Tarot Reading"):
    import random
    cards = [
        "The Sun ☀️ - Joy and success ahead!",
        "The Star ⭐ - Hope and inspiration guide you!",
        "The World 🌍 - Completion and achievement!",
        "Ace of Cups 🏆 - New emotional beginnings!",
        "Three of Pentacles 💰 - Teamwork brings success!",
        "The Magician 🎭 - You have the power to manifest!",
        "Queen of Wands 👑 - Confidence and creativity!",
        "Ten of Cups 💖 - Happiness and fulfillment!"
    ]
    st.sidebar.info(f"**Your Card:** {random.choice(cards)}")

st.sidebar.markdown("---")

# Server Configuration
with st.sidebar.expander("⚙️ Server Configuration"):
    server_url = st.text_input("Server URL", value="http://localhost:1234/v1")
    api_key = st.text_input("API Key", value="lm-studio", type="password")
    model_name = st.text_input("Model Name", value="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF")

st.sidebar.markdown("---")

# Chat Statistics
st.sidebar.markdown("### 📊 Chat Statistics")
current_messages = st.session_state["chat_sessions"].get(st.session_state["current_session"], [])
if current_messages:
    st.sidebar.metric("Total Messages", len(current_messages))
    user_messages = len([msg for msg in current_messages if msg["role"] == "user"])
    st.sidebar.metric("User Messages", user_messages)
    st.sidebar.metric("Assistant Messages", len(current_messages) - user_messages)

# Point to the local server
client = OpenAI(base_url=server_url, api_key=api_key)

# Main chat interface
robot_info = ROBOTS[st.session_state["current_robot"]]
st.title(f"🐕 Snoopy's Best Helper - {robot_info['icon']} {st.session_state['current_robot']}")
st.caption(f"🎾 Your faithful AI companion | {robot_info['description']} | Session: {st.session_state['current_session']}")

# Get current session messages
if st.session_state["current_session"] not in st.session_state["chat_sessions"]:
    st.session_state["chat_sessions"][st.session_state["current_session"]] = [{"role": "assistant", "content": "Woof! I'm here to help you! What can Snoopy's best helper do for you today? 🐾"}]

current_messages = st.session_state["chat_sessions"][st.session_state["current_session"]]

# Add system prompt to messages for API call
def get_messages_with_system_prompt():
    messages = [{"role": "system", "content": robot_info["system_prompt"]}]
    messages.extend(current_messages)
    return messages

for msg in current_messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    current_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=get_messages_with_system_prompt(),
            stream=True,
        )

        msg = ""

        def stream_response():
            global msg
            for chunk in response:
                print(chunk)
                part = chunk.choices[0].delta.content
                if part:
                    msg += part
                    yield part

        
        st.chat_message("assistant").write_stream(stream_response)
        
        current_messages.append({"role": "assistant", "content": msg})
        
        # Update the session in session_state
        st.session_state["chat_sessions"][st.session_state["current_session"]] = current_messages
    
    except Exception as e:
        st.error(f"Error connecting to LMStudio server: {str(e)}")
        st.info("Please make sure LMStudio is running on the specified server URL.")
