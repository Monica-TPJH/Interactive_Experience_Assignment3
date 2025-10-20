import streamlit as st
from openai import OpenAI
from typing import List, Dict, Any
import random
import time
import base64
from pathlib import Path
from urllib.request import urlopen, Request

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Snoopy's Playground",
    page_icon="🐶",
    layout="wide"
)

# Default appearance settings used by background CSS
if "bg_opacity" not in st.session_state:
    st.session_state["bg_opacity"] = 0.3  # initial default opacity (lighter background)
if "bg_fit" not in st.session_state:
    # How the background image scales:
    # - "cover": fill screen, may crop (default)
    # - "contain": show entire image, may leave bars
    # - "100% 100%": stretch to fill exactly (may distort)
    st.session_state["bg_fit"] = "cover"

# -----------------------------
# Global background styling (light base with Snoopy image)
# -----------------------------
BACKGROUND_IMAGE_URL = (
    "https://www.xtrafondos.com/wallpapers/charlie-brown-y-snoopy-12601.jpg"
)

# Local cache path for background image
_APP_DIR = Path(__file__).parent
_ASSETS_DIR = _APP_DIR / "assets"
_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
_LOCAL_BG_PATH = _ASSETS_DIR / "background.jpg"

# Featured audio persistence helpers
_ALLOWED_AUDIO_SUFFIXES = [".mp3", ".wav", ".ogg", ".m4a"]
_FEATURED_AUDIO_BASENAME = "featured"

def _find_featured_audio_file():
    try:
        for p in _ASSETS_DIR.glob(f"{_FEATURED_AUDIO_BASENAME}.*"):
            if p.suffix.lower() in _ALLOWED_AUDIO_SUFFIXES and p.is_file():
                return p
    except Exception:
        pass
    return None

# Resolve background image as a data URI with local-cache preference
bg_image_css = None
try:
    if _LOCAL_BG_PATH.exists():
        with _LOCAL_BG_PATH.open("rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        bg_image_css = f"url('data:image/jpeg;base64,{b64}')"
except Exception:
    pass

if bg_image_css is None:
    # Try to fetch remotely and cache locally
    try:
        req = Request(
            BACKGROUND_IMAGE_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Referer": "https://www.xtrafondos.com/",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            },
        )
        with urlopen(req, timeout=6) as resp:
            data = resp.read()
            # Cache for future runs
            try:
                with _LOCAL_BG_PATH.open("wb") as f:
                    f.write(data)
            except Exception:
                pass
            content_type = resp.headers.get("Content-Type") or "image/jpeg"
            b64 = base64.b64encode(data).decode("utf-8")
            bg_image_css = f"url('data:{content_type};base64,{b64}')"
    except Exception:
        # Fallback to using the direct URL if all else fails
        bg_image_css = f"url('{BACKGROUND_IMAGE_URL}')"

# If user provided a custom background this session, prefer it
custom_b64 = st.session_state.get("custom_bg_b64")
if custom_b64:
    bg_image_css = f"url('data:image/*;base64,{custom_b64}')"

st.markdown(
    f"""
    <style>
    /* Keep global backgrounds transparent so the fixed layer shows */
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        background: transparent !important;
        height: 100% !important;
        min-height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important; /* prevent horizontal scroll */
    }}

    /* Ensure sizing doesn't cause overflow */
    *, *::before, *::after {{
        box-sizing: border-box;
    }}

    /* Prevent transformed ancestors from breaking fixed positioning on some browsers */
    .stApp, [data-testid="stAppViewContainer"] {{
        transform: none !important;
    }}

    /* Fallback on body in case container background is overridden */
    body {{
        background-color: transparent !important;
    }}

    /* Make top header transparent so the background shows through */
    [data-testid="stHeader"] {{
        background: rgba(255,255,255,0);
    }}

    /* Lighten the sidebar area for readability */
    [data-testid="stSidebar"] > div:first-child {{
        background-color: rgba(255,255,255,0.60);
        backdrop-filter: blur(2px);
    }}

    /* Ensure main content area doesn't cover the background */
    .stApp {{
        position: relative !important;
    }}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"] {{
        position: relative !important;
        z-index: 1 !important;
    }}
    [data-testid="stAppViewContainer"] > .main {{
        background: transparent !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }}

    /* Slight blur on main content container to improve contrast */
    .block-container {{
        background-color: rgba(255,255,255,0.0) !important;
        backdrop-filter: blur(1.5px);
        max-width: 100% !important;
        overflow-x: hidden !important;
    }}

    /* Keep media within viewport width */
    .stApp img, .stApp video {{
        max-width: 100% !important;
        height: auto !important;
    }}

    /* Wrap long text so it doesn't overflow horizontally */
    [data-testid="stMarkdownContainer"] {{
        overflow-wrap: anywhere;
        word-break: break-word;
    }}
    .stMarkdown pre {{
        max-width: 100% !important;
        overflow-x: auto !important; /* scroll inside code blocks, not page */
    }}

    /* Root-level background to persist during scroll */
    html::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-image: {bg_image_css};
        background-size: {st.session_state.get('bg_fit', 'cover')};
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        opacity: {st.session_state.get('bg_opacity', 0.7)};
        z-index: 0;
        pointer-events: none;
    }}

    /* Fixed background layer with adjustable transparency (kept as a fallback) */
    #bg-layer {{
        position: fixed;
        inset: 0;
        background-image: {bg_image_css};
        background-size: {st.session_state.get('bg_fit', 'cover')};
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        opacity: {st.session_state.get('bg_opacity', 0.7)};
        z-index: 0;
        pointer-events: none;
    }}
    </style>
    <div id="bg-layer"></div>
    """,
    unsafe_allow_html=True,
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
        "mines": [],
        "last_tick": None
    }

# Attempt to auto-load a persisted featured audio on first load of session
if "featured_snoopy_audio" not in st.session_state:
    _fa = _find_featured_audio_file()
    if _fa:
        try:
            st.session_state["featured_snoopy_audio"] = _fa.read_bytes()
            st.session_state["featured_snoopy_audio_path"] = str(_fa)
        except Exception:
            pass

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

# Appearance controls
with st.sidebar.expander("🎨 Appearance"):
    uploaded_bg = st.file_uploader("Custom background image", type=["jpg", "jpeg", "png", "webp"])
    new_opacity = st.slider("Background opacity (higher = stronger image)", 0.3, 1.0, st.session_state.get("bg_opacity", 0.7), 0.05)
    # Background fit mode control
    fit_options = {
        "Cover (fill screen, may crop)": "cover",
        "Contain (show all, may add bars)": "contain",
        "Stretch (fill exactly, may distort)": "100% 100%",
    }
    current_fit_value = st.session_state.get("bg_fit", "cover")
    # Find the label that corresponds to the current value
    current_fit_label = next((k for k, v in fit_options.items() if v == current_fit_value), "Cover (fill screen, may crop)")
    selected_fit_label = st.selectbox("Background fit", list(fit_options.keys()), index=list(fit_options.keys()).index(current_fit_label))
    selected_fit_value = fit_options[selected_fit_label]
    if selected_fit_value != current_fit_value:
        st.session_state["bg_fit"] = selected_fit_value
        st.rerun()
    if new_opacity != st.session_state.get("bg_opacity", 0.7):
        st.session_state["bg_opacity"] = new_opacity
        st.rerun()
    if uploaded_bg is not None:
        if st.button("Use this background"):
            data = uploaded_bg.read()
            try:
                with _LOCAL_BG_PATH.open("wb") as f:
                    f.write(data)
            except Exception:
                pass
            st.session_state["custom_bg_b64"] = base64.b64encode(data).decode("utf-8")
            st.success("Background updated!")
            st.rerun()

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
    st.markdown("Local-only playback (no external websites). Upload local audio to play.")

    # Featured track (local only)
    st.markdown("#### 🎼 Featured: Snoopy on the Swings")
    # Option A: Use a local audio file as Featured
    featured_local = st.session_state.get("featured_snoopy_audio")
    cfeat1, cfeat2 = st.columns([3, 1])
    with cfeat1:
        local_featured_upload = st.file_uploader(
            "Upload local audio for Featured (mp3/wav/ogg/m4a)",
            type=["mp3", "wav", "ogg", "m4a"],
            key="featured_audio_uploader",
        )
    with cfeat2:
        if featured_local is not None:
            if st.button("Remove Featured"):
                # Remove from session and delete any persisted featured.* file
                st.session_state.pop("featured_snoopy_audio", None)
                st.session_state.pop("featured_snoopy_audio_path", None)
                try:
                    for p in _ASSETS_DIR.glob(f"{_FEATURED_AUDIO_BASENAME}.*"):
                        if p.suffix.lower() in _ALLOWED_AUDIO_SUFFIXES:
                            p.unlink(missing_ok=True)
                except Exception:
                    pass
                st.rerun()
        else:
            if local_featured_upload is not None and st.button("Use as Featured"):
                try:
                    data = local_featured_upload.read()
                    st.session_state["featured_snoopy_audio"] = data
                    # Persist to assets as featured.<ext>
                    # Prefer extension from filename; fallback via MIME type
                    ext = Path(local_featured_upload.name).suffix.lower()
                    if not ext:
                        mime = getattr(local_featured_upload, "type", "").lower()
                        mime_map = {
                            "audio/mpeg": ".mp3",
                            "audio/mp3": ".mp3",
                            "audio/wav": ".wav",
                            "audio/x-wav": ".wav",
                            "audio/ogg": ".ogg",
                            "audio/x-m4a": ".m4a",
                            "audio/aac": ".m4a",
                            "audio/mp4": ".m4a",
                        }
                        ext = mime_map.get(mime, ".mp3")
                    if ext not in _ALLOWED_AUDIO_SUFFIXES:
                        ext = ".mp3"
                    # Remove old featured files
                    try:
                        for p in _ASSETS_DIR.glob(f"{_FEATURED_AUDIO_BASENAME}.*"):
                            if p.suffix.lower() in _ALLOWED_AUDIO_SUFFIXES:
                                p.unlink(missing_ok=True)
                    except Exception:
                        pass
                    out_path = _ASSETS_DIR / f"{_FEATURED_AUDIO_BASENAME}{ext}"
                    try:
                        with out_path.open("wb") as f:
                            f.write(data)
                        st.session_state["featured_snoopy_audio_path"] = str(out_path)
                    except Exception as e:
                        st.warning(f"Saved locally but could not persist to assets: {e}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to set featured audio: {e}")

    if st.session_state.get("featured_snoopy_audio") is not None:
        st.audio(st.session_state["featured_snoopy_audio"])
        current_fp = st.session_state.get("featured_snoopy_audio_path")
        if current_fp:
            st.caption(f"Playing local Featured track (saved: {Path(current_fp).name}).")
        else:
            st.caption("Playing local Featured track.")
    else:
        # Local-only: No featured file yet
        st.info("No Featured track yet. Upload a local file above and click 'Use as Featured'. This app does not use external music websites.")

    # Quick play (local only, not persisted)
    audio_file = st.file_uploader("Play a local audio file (temporary)", type=["mp3", "wav", "ogg", "m4a"], key="non_featured_audio")
    if audio_file is not None:
        st.audio(audio_file)

    # Local assets library to set an existing file as Featured
    with st.expander("📁 Local assets library"):
        try:
            library_files = [
                p for p in _ASSETS_DIR.glob("*")
                if p.is_file() and p.suffix.lower() in _ALLOWED_AUDIO_SUFFIXES and _FEATURED_AUDIO_BASENAME not in p.stem
            ]
        except Exception:
            library_files = []
        if library_files:
            labels = [p.name for p in library_files]
            selected_label = st.selectbox("Choose a local audio file from Website_AI/assets", labels, key="assets_library_select")
            if st.button("Set selected as Featured", key="assets_library_set_btn") and selected_label:
                try:
                    chosen = next((p for p in library_files if p.name == selected_label), None)
                    if chosen is not None:
                        data = chosen.read_bytes()
                        st.session_state["featured_snoopy_audio"] = data
                        # Remove old featured files
                        try:
                            for p in _ASSETS_DIR.glob(f"{_FEATURED_AUDIO_BASENAME}.*"):
                                if p.suffix.lower() in _ALLOWED_AUDIO_SUFFIXES:
                                    p.unlink(missing_ok=True)
                        except Exception:
                            pass
                        ext = chosen.suffix.lower()
                        if ext not in _ALLOWED_AUDIO_SUFFIXES:
                            ext = ".mp3"
                        out_path = _ASSETS_DIR / f"{_FEATURED_AUDIO_BASENAME}{ext}"
                        try:
                            with out_path.open("wb") as f:
                                f.write(data)
                            st.session_state["featured_snoopy_audio_path"] = str(out_path)
                        except Exception as e:
                            st.warning(f"Saved locally but could not persist to assets: {e}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to set Featured from library: {e}")
        else:
            st.caption("No local audio files found in Website_AI/assets (besides Featured). You can drop files there and they will appear here.")

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
            game_state["last_tick"] = time.monotonic()
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

    # Countdown timer tick (runs each render while game is active)
    if game_state.get("game_active"):
        now = time.monotonic()
        last_tick = game_state.get("last_tick") or now
        elapsed = int(now - last_tick)
        if elapsed > 0:
            # Decrease remaining time by elapsed seconds
            game_state["time_left"] = max(0, game_state.get("time_left", 0) - elapsed)
            game_state["last_tick"] = last_tick + elapsed
            # If time runs out, end the game
            if game_state["time_left"] <= 0:
                game_state["game_active"] = False
                game_state["last_result"] = {
                    "score": game_state.get("score", 0),
                    "level": game_state.get("level", 1),
                    "lives": game_state.get("lives", 0),
                    "ended_by": "timeout"
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

        # Auto-refresh the page every second while the game is active to update the countdown
        if game_state.get("game_active"):
            time.sleep(1)
            st.rerun()

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
            elif reason == "timeout":
                st.warning("Ended because: Time ran out ⏰")
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
