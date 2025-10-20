import streamlit as st
from openai import OpenAI
from typing import List, Dict, Any
import random

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Snoopy's Playground",
    page_icon="🐶",
    layout="wide"
)

# -----------------------------
# Session state initialization
# -----------------------------
if "current_robot" not in st.session_state:
    st.session_state["current_robot"] = "General Assistant"
if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = {}
if "current_session" not in st.session_state:
    st.session_state["current_session"] = "Default Chat"
if "game_state" not in st.session_state:
    st.session_state["game_state"] = {
        "score": 0,
        "level": 1,
        "lives": 3,
        "time_left": 60,
        "game_active": False,
        "mines": []
    }

# -----------------------------
# Robot configurations
# -----------------------------
ROBOTS: Dict[str, Dict[str, Any]] = {
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

# -----------------------------
# Sidebar: Robot selection and session management
# -----------------------------
st.sidebar.title("🐕 Snoopy's Helpers")

selected_robot = st.sidebar.selectbox(
    "Choose your AI companion:",
    list(ROBOTS.keys()),
    index=list(ROBOTS.keys()).index(st.session_state["current_robot"])
)
if selected_robot != st.session_state["current_robot"]:
    st.session_state["current_robot"] = selected_robot

robot_info = ROBOTS[selected_robot]
st.sidebar.markdown(f"### {robot_info['icon']} {selected_robot}")
st.sidebar.write(robot_info['description'])

st.sidebar.markdown("---")

# Chat Sessions Management
st.sidebar.markdown("### 💬 Chat Sessions")
session_names: List[str] = list(st.session_state["chat_sessions"].keys()) + ["Create New Session"]
if st.session_state["current_session"] not in st.session_state["chat_sessions"]:
    st.session_state["chat_sessions"][st.session_state["current_session"]] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

selected_session = st.sidebar.selectbox(
    "Select chat session:",
    session_names,
    index=0 if st.session_state["current_session"] not in session_names else session_names.index(st.session_state["current_session"])
)

if selected_session == "Create New Session":
    new_session_name = st.sidebar.text_input("New session name:", value=f"Chat {len(st.session_state['chat_sessions']) + 1}")
    if st.sidebar.button("Create Session"):
        if new_session_name and new_session_name not in st.session_state["chat_sessions"]:
            st.session_state["chat_sessions"][new_session_name] = [{"role": "assistant", "content": "Woof! I'm here to help you! What can Snoopy's best helper do for you today? 🐾"}]
            st.session_state["current_session"] = new_session_name
            st.rerun()
else:
    st.session_state["current_session"] = selected_session

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
    user_messages = len([m for m in current_messages if m.get("role") == "user"])
    st.sidebar.metric("User Messages", user_messages)
    st.sidebar.metric("Assistant Messages", len(current_messages) - user_messages)

# Create OpenAI client (LMStudio-compatible)
client = OpenAI(base_url=server_url, api_key=api_key)

# -----------------------------
# Header
# -----------------------------
robot_info = ROBOTS[st.session_state["current_robot"]]
st.title(f"🐕 Snoopy's Playground - {robot_info['icon']} {st.session_state['current_robot']}")
st.caption(f"🎾 Your faithful AI companion | {robot_info['description']} | Session: {st.session_state['current_session']}")

# Ensure current session exists with intro message
if st.session_state["current_session"] not in st.session_state["chat_sessions"]:
    st.session_state["chat_sessions"][st.session_state["current_session"]] = [
        {"role": "assistant", "content": "Woof! I'm here to help you! What can Snoopy's best helper do for you today? 🐾"}
    ]
current_messages = st.session_state["chat_sessions"][st.session_state["current_session"]]

# Helper to attach system prompt
def get_messages_with_system_prompt() -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": robot_info["system_prompt"]}]
    messages.extend(current_messages)
    return messages

# -----------------------------
# Main tabs in chat area
# -----------------------------
tab_chat, tab_music, tab_video, tab_game, tab_article, tab_fortune = st.tabs(["Chat", "Music", "Video", "Game", "Article", "Fortune"])

# --- Chat tab ---
with tab_chat:
    for msg in current_messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Type your message"):
        current_messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=get_messages_with_system_prompt(),
                stream=True,
            )
            msg_acc: List[str] = []

            def stream_response():
                for chunk in response:
                    part = getattr(chunk.choices[0].delta, "content", None)
                    if part:
                        msg_acc.append(part)
                        yield part

            st.chat_message("assistant").write_stream(stream_response)
            msg_text = "".join(msg_acc)
            current_messages.append({"role": "assistant", "content": msg_text})
            st.session_state["chat_sessions"][st.session_state["current_session"]] = current_messages
        except Exception as e:
            st.error(f"Error connecting to LMStudio server: {str(e)}")
            st.info("Please make sure LMStudio is running on the specified server URL.")

# --- Music tab ---
with tab_music:
    st.subheader("🎵 Music")
    st.markdown("Upload an audio file or paste a public URL to play.")

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        audio_file = st.file_uploader("Upload audio (mp3/wav)", type=["mp3", "wav", "ogg", "m4a"])
        if audio_file is not None:
            st.audio(audio_file)
    with col_u2:
        audio_url = st.text_input("Audio URL (optional)")
        if audio_url:
            st.audio(audio_url)

    st.markdown("---")
    st.markdown("Or ask Snoopy to recommend a playlist for your mood:")
    mood = st.text_input("Your mood (e.g., chill, focus, happy)")
    if st.button("Suggest playlist") and mood:
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": robot_info["system_prompt"]},
                    {"role": "user", "content": f"Suggest a short 5-track playlist for a {mood} mood. Return as a simple bulleted list."}
                ],
                stream=True,
            )
            st.write_stream((getattr(c.choices[0].delta, "content", None) or "") for c in resp)
        except Exception as e:
            st.error(f"Playlist suggestion failed: {e}")

# --- Video tab ---
with tab_video:
    st.subheader("🎬 Video")
    st.markdown("Upload a video or paste a public URL to embed.")

    # Featured Snoopy video (from user's link)
    featured_snoopy_url = "https://www.youtube.com/watch?v=aDRARW93DbY"
    st.markdown("#### Featured: Snoopy Video")
    st.video(featured_snoopy_url)
    st.caption("You can replace it with your own video by uploading a file or entering a different URL below.")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        video_file = st.file_uploader("Upload video (mp4/mov)", type=["mp4", "mov", "webm", "mkv"])
        if video_file is not None:
            st.video(video_file)
    with col_v2:
        video_url = st.text_input("Video URL (optional)", value=featured_snoopy_url)
        if video_url:
            st.video(video_url)

# --- Game tab ---
with tab_game:
    st.subheader("⛏️ Snoopy's Gold Miner (Main Area)")
    game_state = st.session_state["game_state"]

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        if st.button("🎮 Start Game", key="start_game_main"):
            game_state["score"] = 0
            game_state["level"] = 1
            game_state["lives"] = 3
            game_state["time_left"] = 60
            game_state["game_active"] = True
            game_state["last_result"] = None
            game_state["mines"] = [
                {"type": "gold", "value": random.randint(50, 200), "size": random.choice(["small", "medium", "large"])}
                for _ in range(6)
            ] + [
                {"type": "rock", "value": 0, "size": "medium"}
                for _ in range(3)
            ]
        
    with col_g2:
        if st.button("🛑 Stop Game", key="stop_game_main"):
            if game_state.get("game_active"):
                game_state["game_active"] = False
                game_state["last_result"] = {
                    "score": game_state.get("score", 0),
                    "level": game_state.get("level", 1),
                    "lives": game_state.get("lives", 0),
                    "ended_by": "stopped"
                }

    st.markdown("---")

    if game_state["game_active"]:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Score", game_state["score"])
        c2.metric("❤️ Lives", game_state["lives"])
        c3.metric("⏱️ Time", f"{game_state['time_left']}s")
        c4.metric("📈 Level", game_state["level"])

        st.markdown("#### ⛏️ Mining Area — click buttons to mine")
        cols = st.columns(3)
        for i, mine in enumerate(game_state["mines"][:9]):
            col_idx = i % 3
            with cols[col_idx]:
                if mine["type"] == "gold":
                    emoji = "💰" if mine["size"] == "large" else "🥇" if mine["size"] == "medium" else "🪙"
                else:
                    emoji = "🪨"

                if st.button(f"{emoji}", key=f"mine_main_{i}"):
                    if mine["type"] == "gold":
                        points = mine["value"]
                        game_state["score"] += points
                        st.success(f"💎 Found gold! +{points} points!")
                        if game_state["score"] > game_state["level"] * 500:
                            game_state["level"] += 1
                            game_state["time_left"] += 30
                            st.info(f"🎉 Level {game_state['level']}! +30s bonus time!")
                    else:
                        game_state["lives"] -= 1
                        st.error("🪨 Hit a rock! -1 life!")
                        if game_state["lives"] <= 0:
                            game_state["game_active"] = False
                            game_state["last_result"] = {
                                "score": game_state.get("score", 0),
                                "level": game_state.get("level", 1),
                                "lives": game_state.get("lives", 0),
                                "ended_by": "no_lives"
                            }
                            st.error("💀 Game Over! Snoopy needs more practice!")

                    game_state["mines"][i] = {
                        "type": random.choice(["gold", "gold", "gold", "rock"]),
                        "value": random.randint(50, 200),
                        "size": random.choice(["small", "medium", "large"])
                    }

    else:
        # Post-game summary if available
        last_result = game_state.get("last_result")
        if last_result:
            st.markdown("## 🎮 Round Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Score", last_result.get("score", 0))
            c2.metric("📈 Level", last_result.get("level", 1))
            c3.metric("❤️ Lives Left", last_result.get("lives", 0))
            reason = last_result.get("ended_by", "unknown")
            if reason == "no_lives":
                st.error("Ended because: Out of lives 🥲")
            elif reason == "stopped":
                st.info("Ended because: Stopped manually ⏹️")
            else:
                st.warning(f"Ended because: {reason}")
            st.markdown("---")
        st.info("Click Start Game to begin mining for gold!")

# --- Fortune tab ---
with tab_fortune:
    st.subheader("🔮 Fortune")
    st.markdown("Choose a way to check today's fortune, or ask Snoopy a question:")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        if st.button("🌟 Daily Fortune"):
            fortunes = [
                "Great day to start something new—your smile brings luck!",
                "Mind the details and you'll dodge small bumps.",
                "A helpful person may appear—take initiative!",
                "Perfect for learning and organizing—solid gains.",
                "Be patient—good news is on the way.",
                "Time with friends recharges you—good vibes ahead.",
                "Express and create—ideas will flow today.",
            ]
            st.success(f"Today's fortune: {random.choice(fortunes)}")
    with col_f2:
        if st.button("🎴 Draw a Tarot Card"):
            cards = [
                "☀️ The Sun: vitality, success, and warmth.",
                "⭐ The Star: hope, inspiration, and healing.",
                "🌍 The World: completion, wholeness, new phase.",
                "🏆 Ace of Cups: new emotional beginning, inspiration.",
                "🪄 The Magician: agency and manifesting power.",
                "👑 Queen of Wands: confidence, passion, creativity.",
                "💖 Ten of Cups: family harmony and inner contentment.",
            ]
            st.info(f"Your card: {random.choice(cards)}")
    with col_f3:
        st.write(" ")

    st.markdown("---")
    st.markdown("If you have a specific question, ask Snoopy for a reading:")
    q = st.text_input("Your question (optional)")
    if st.button("💬 Get Reading"):
        try:
            sys_prompt = (
                "You are a warm, encouraging fortune advisor. Offer positive, practical guidance. "
                "If the user has no clear question, share a short daily fortune and a tip. "
                "If there is a question, first reassure them, then provide direction and cautions."
            )
            messages = [
                {"role": "system", "content": sys_prompt},
            ]
            if q:
                messages.append({"role": "user", "content": f"Question: {q}"})
            else:
                messages.append({"role": "user", "content": "Please give me today's fortune and advice."})

            resp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                stream=True,
            )
            st.write_stream((getattr(c.choices[0].delta, "content", None) or "") for c in resp)
        except Exception as e:
            st.error(f"Reading failed: {e}")

# --- Article tab ---
with tab_article:
    st.subheader("📝 Article Writer")
    topic = st.text_input("Article topic or title")
    words = st.slider("Approximate length (words)", 100, 1200, 400, 50)
    tone = st.selectbox("Tone", ["neutral", "friendly", "professional", "playful", "academic"])

    if st.button("Generate Article"):
        if not topic:
            st.warning("Please enter a topic first.")
        else:
            try:
                sys_prompt = robot_info["system_prompt"] + " Always structure the article with a clear title and sections."
                user_prompt = (
                    f"Write an article about: '{topic}'. Aim for about {words} words. "
                    f"Tone: {tone}. Include a short introduction, 2-4 sections with headings, and a brief conclusion."
                )
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True,
                )
                st.write_stream((getattr(c.choices[0].delta, "content", None) or "") for c in resp)
            except Exception as e:
                st.error(f"Article generation failed: {e}")
