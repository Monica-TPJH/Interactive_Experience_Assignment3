import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import cv2
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Video Stream Effects - Backup (Fixed)",
    page_icon="📹",
    layout="wide",
)

st.title("📹 Smart Video Stream with Expression Recognition (Backup)")
st.markdown("Apply real-time effects and detect facial expressions with AI! 😊😮😢😡")

# Sidebar for effect selection
with st.sidebar:
    st.header("🎛️ Effect Controls")
    effect = st.selectbox(
        "Choose an effect:",
        [
            "Face Detection",
            "None",
            "Flip Vertical",
            "Flip Horizontal",
            "Grayscale",
            "Edge Detection",
            "Blur",
            "Sepia",
            "Emotion Recognition",
            "Fun Emoji Overlay",
        ],
    )

    # AI Features Toggle
    st.subheader("🤖 Facial Detection Features")
    enable_emotion_detection = st.checkbox("Enable Emotion Detection", value=False)
    enable_face_tracking = st.checkbox("Enable Face Tracking", value=True)
    show_emotion_stats = st.checkbox("Show Emotion Statistics", value=False)
    debug_mode = st.checkbox("🔧 Debug Mode (Show detection info)", value=True)

    # Face detection sensitivity
    st.subheader("🎯 Detection Sensitivity")
    detection_sensitivity = st.slider("Detection Sensitivity", 1, 10, 7, help="Higher = more sensitive")
    min_face_size = st.slider("Minimum Face Size", 15, 100, 20, help="Smaller = detects smaller faces")

    # Defaults for effect parameters
    blur_amount = 15
    threshold1 = 100
    threshold2 = 200

    if effect == "Blur":
        blur_amount = st.slider("Blur Amount", 1, 50, 15, step=2)

    if effect == "Edge Detection":
        threshold1 = st.slider("Edge Threshold 1", 50, 200, 100)
        threshold2 = st.slider("Edge Threshold 2", 100, 300, 200)

# Store values in session state for callback access
st.session_state.effect_params = {
    "effect": effect,
    "blur_amount": blur_amount,
    "threshold1": threshold1,
    "threshold2": threshold2,
    "enable_emotion_detection": enable_emotion_detection,
    "enable_face_tracking": enable_face_tracking,
    "show_emotion_stats": show_emotion_stats,
    "debug_mode": debug_mode,
    "detection_sensitivity": detection_sensitivity,
    "min_face_size": min_face_size,
}

# Initialize simple emotion/face stats in session_state
st.session_state.setdefault("emotion_history", [])
st.session_state.setdefault("current_emotion", "neutral")
st.session_state.setdefault("emotion_confidence", 0.0)
st.session_state.setdefault("face_count", 0)
st.session_state.setdefault("last_emotion_time", 0)

# Load cascade classifiers once
@st.cache_resource
def load_cascades():
    primary = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    alt = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt.xml")
    return primary, alt


face_cascade, alt_cascade = load_cascades()

def video_frame_callback(frame):
    try:
        img = frame.to_ndarray(format="bgr24")
    except Exception:
        return None

    # Safely read parameters (fallbacks if called outside main thread)
    params = {}
    try:
        params = st.session_state.get("effect_params", {})
    except Exception:
        # fallback defaults if session_state not accessible
        params = {
            "effect": "Face Detection",
            "blur_amount": 15,
            "threshold1": 100,
            "threshold2": 200,
            "enable_emotion_detection": False,
            "enable_face_tracking": True,
            "debug_mode": True,
            "detection_sensitivity": 7,
            "min_face_size": 20,
        }

    current_effect = params.get("effect", "None")
    current_blur = int(params.get("blur_amount", 15))
    current_threshold1 = int(params.get("threshold1", 100))
    current_threshold2 = int(params.get("threshold2", 200))
    enable_emotion = params.get("enable_emotion_detection", False)
    enable_face = params.get("enable_face_tracking", True)
    debug = params.get("debug_mode", True)
    detection_sensitivity = int(params.get("detection_sensitivity", 7))
    min_face_size = int(params.get("min_face_size", 20))

    # Prepare gray image for detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = []
    detection_method = "none"

    # Only run detection when relevant
    if enable_face or enable_emotion or current_effect in ["Face Detection", "Emotion Recognition", "Fun Emoji Overlay"]:
        try:
            # Enhance image slightly
            proc = cv2.equalizeHist(gray)
            proc = cv2.GaussianBlur(proc, (3, 3), 0)

            scale_factor = 1.05 + (detection_sensitivity - 5) * 0.01
            min_neighbors = max(1, 8 - detection_sensitivity)

            # Primary detection
            faces = face_cascade.detectMultiScale(
                proc,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=(min_face_size, min_face_size),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )

            if len(faces) == 0:
                # More relaxed
                faces = face_cascade.detectMultiScale(
                    proc, scaleFactor=1.1, minNeighbors=2, minSize=(15, 15), flags=cv2.CASCADE_SCALE_IMAGE
                )
                detection_method = "relaxed"

            if len(faces) == 0 and alt_cascade is not None:
                faces = alt_cascade.detectMultiScale(proc, scaleFactor=1.08, minNeighbors=3, minSize=(20, 20))
                detection_method = "alt"

            if len(faces) > 0 and detection_method == "none":
                detection_method = "primary"

        except Exception as e:
            if debug:
                cv2.putText(img, f"Detection error: {str(e)[:60]}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Draw overlays / effects
    face_count = len(faces) if hasattr(faces, "__len__") else 0
    for i, (x, y, w, h) in enumerate(faces):
        color = (0, 255, 0) if i == 0 else (255, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, f"Person {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cx, cy = x + w // 2, y + h // 2
        cv2.circle(img, (cx, cy), 3, (0, 0, 255), -1)

        if current_effect == "Emotion Recognition" or enable_emotion:
            # Placeholder/simple random emotion for demo (replace with model if available)
            emotions = ["happy", "sad", "angry", "surprised", "neutral"]
            emotion = np.random.choice(emotions)
            conf = np.random.uniform(0.6, 0.95)
            cv2.putText(img, f"{emotion} {conf:.2f}", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            # update session_state safely (best-effort; ignore failures)
            try:
                st.session_state.current_emotion = emotion
                st.session_state.emotion_confidence = conf
            except Exception:
                pass

        if current_effect == "Fun Emoji Overlay":
            emoji_map = {"happy": ":)", "sad": ":(", "angry": ">:(", "surprised": ":O", "neutral": ":|"}
            # read from session if possible
            try:
                emotion_label = st.session_state.get("current_emotion", "neutral")
            except Exception:
                emotion_label = "neutral"
            emoji = emoji_map.get(emotion_label, ":)")
            cv2.putText(img, emoji, (x + w // 2 - 20, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)

    # If no faces and debug, show hint
    if face_count == 0 and debug:
        cv2.putText(img, "No faces detected - try better lighting / face camera directly", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Traditional effects
    if current_effect == "Flip Vertical":
        img = img[::-1, :, :]
    elif current_effect == "Flip Horizontal":
        img = img[:, ::-1, :]
    elif current_effect == "Grayscale":
        gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(gray2, cv2.COLOR_GRAY2BGR)
    elif current_effect == "Edge Detection":
        edges = cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), current_threshold1, current_threshold2)
        img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    elif current_effect == "Blur":
        ksize = max(1, int(current_blur) // 2 * 2 + 1)
        img = cv2.GaussianBlur(img, (ksize, ksize), 0)
    elif current_effect == "Sepia":
        sepia_filter = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        img = cv2.transform(img, sepia_filter)
        img = np.clip(img, 0, 255).astype(np.uint8)

    # Update face_count in session_state safely
    try:
        st.session_state.face_count = face_count
    except Exception:
        pass

    return av.VideoFrame.from_ndarray(img, format="bgr24")


# WebRTC configuration
RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

# Main video streamer layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📸 Live Feed - {effect}")
    webrtc_streamer(
        key="video-effects-backup",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_frame_callback=video_frame_callback,
        async_processing=True,
        media_stream_constraints={"video": True, "audio": False},
    )

with col2:
    st.subheader("🤖 AI Analytics")
    current_effect = st.session_state.effect_params.get("effect", "None")

    # Real-time AI stats
    st.metric("👥 Faces Detected", st.session_state.get("face_count", 0))
    st.metric("😊 Current Emotion", st.session_state.get("current_emotion", "neutral"))
    st.metric("📈 Confidence", f"{st.session_state.get('emotion_confidence', 0.0):.2f}")

    st.markdown(f"""
    **Current Effect:** {current_effect}
    
    **🎭 AI Features:**
    - 👁️ Face Detection & Tracking
    - 😊 Real-time Emotion Recognition (demo)
    - 🎨 Smart Emoji Overlays
    
    **💡 Tips:**
    - Enable AI features in sidebar
    - Good lighting improves detection
    """)
