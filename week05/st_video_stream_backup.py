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

st.title("📹 Smart Video Stream - Face Detection Only (Backup)")
st.markdown("Apply real-time effects and detect faces only (no expression recognition).")

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
        # emotion-related effects removed — face detection only
        ],
    )

    # AI Features Toggle
    st.subheader("🤖 Facial Detection Features")
    enable_face_tracking = st.checkbox("Enable Face Tracking", value=True)
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
    "enable_face_tracking": enable_face_tracking,
    "debug_mode": debug_mode,
    "detection_sensitivity": detection_sensitivity,
    "min_face_size": min_face_size,
}

# Initialize simple face stats in session_state
st.session_state.setdefault("face_count", 0)

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
            "enable_face_tracking": True,
            "debug_mode": True,
            "detection_sensitivity": 7,
            "min_face_size": 20,
        }

    current_effect = params.get("effect", "None")
    current_blur = int(params.get("blur_amount", 15))
    current_threshold1 = int(params.get("threshold1", 100))
    current_threshold2 = int(params.get("threshold2", 200))
    enable_face = params.get("enable_face_tracking", True)
    debug = params.get("debug_mode", True)
    detection_sensitivity = int(params.get("detection_sensitivity", 7))
    min_face_size = int(params.get("min_face_size", 20))

    # Prepare gray image for detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = []
    detection_method = "none"

    # Only run detection when relevant
    if enable_face or current_effect == "Face Detection":
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

        # Face-only overlays (label and bounding box) kept above

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

    st.markdown(f"""
    **Current Effect:** {current_effect}
    
    **🎭 AI Features:**
    - 👁️ Face Detection & Tracking
    - 🎨 Smart Emoji Overlays (face-only)
    
    **💡 Tips:**
    - Enable AI features in sidebar
    - Good lighting improves detection
    """)
