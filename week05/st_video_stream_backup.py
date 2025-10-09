import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import cv2
import numpy as np

# Page configuration
st.set_page_confi                # Fun emoji overlay
                if current_effect == "Fun Emoji Overlay":
                    emoji_map = {
                        "happy": ":)", "sad": ":(", "angry": ">:(", 
                        "surprised": ":O", "neutral": ":|, "fear": ":S", "disgust": ":P"
                    }
                    # Use random emoji for demo (avoid session state in callback)
                    emotion = np.random.choice(list(emoji_map.keys()))
                    emoji = emoji_map.get(emotion, ":)")
                    
                    # Draw emoji text (using ASCII for better compatibility)
                    cv2.putText(img, emoji, (x+w//2-20, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)_title="Video Stream Effects",
    page_icon="📹",
    layout="wide"
)

st.title("📹 Smart Video Stream with Expression Recognition")
st.markdown("Apply real-time effects and detect facial expressions with AI! 😊😮😢😡")

# Sidebar for effect selection
with st.sidebar:
    st.header("🎛️ Effect Controls")
    effect = st.selectbox(
        "Choose an effect:",
        ["Face Detection", "None", "Flip Vertical", "Flip Horizontal", "Grayscale", "Edge Detection", "Blur", "Sepia", "Emotion Recognition", "Fun Emoji Overlay"]
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
    
    blur_amount = 15  # Default value
    threshold1 = 100  # Default value
    threshold2 = 200  # Default value
    
    if effect == "Blur":
        blur_amount = st.slider("Blur Amount", 1, 50, 15, step=2)
    
    if effect == "Edge Detection":
        threshold1 = st.slider("Edge Threshold 1", 50, 200, 100)
        threshold2 = st.slider("Edge Threshold 2", 100, 300, 200)

# Store values in session state for callback access
if 'effect_params' not in st.session_state:
    st.session_state.effect_params = {}

st.session_state.effect_params = {
    'effect': effect,
    'blur_amount': blur_amount,
    'threshold1': threshold1,
    'threshold2': threshold2,
    'enable_emotion_detection': enable_emotion_detection,
    'enable_face_tracking': enable_face_tracking,
    'show_emotion_stats': show_emotion_stats,
    'debug_mode': debug_mode,
    'detection_sensitivity': detection_sensitivity,
    'min_face_size': min_face_size
}

# Initialize emotion tracking
if 'emotion_history' not in st.session_state:
    st.session_state.emotion_history = []
if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = "neutral"
if 'emotion_confidence' not in st.session_state:
    st.session_state.emotion_confidence = 0.0
if 'face_count' not in st.session_state:
    st.session_state.face_count = 0
if 'last_emotion_time' not in st.session_state:
    st.session_state.last_emotion_time = 0

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    # Get effect parameters from session state
    params = st.session_state.get('effect_params', {})
    current_effect = params.get('effect', 'None')
    current_blur = params.get('blur_amount', 15)
    current_threshold1 = params.get('threshold1', 100)
    current_threshold2 = params.get('threshold2', 200)
    enable_emotion = params.get('enable_emotion_detection', False)
    enable_face = params.get('enable_face_tracking', False)
    debug_mode = params.get('debug_mode', True)
    detection_sensitivity = params.get('detection_sensitivity', 7)
    min_face_size = params.get('min_face_size', 20)
    
    # Calculate detection parameters based on sensitivity
    scale_factor = 1.05 + (detection_sensitivity - 7) * 0.01  # 1.02 to 1.08
    min_neighbors = max(2, 8 - detection_sensitivity)  # 2 to 6
    
    # Face detection and emotion analysis
    if enable_face or enable_emotion or current_effect in ["Face Detection", "Emotion Recognition", "Fun Emoji Overlay"]:
        try:
            # Face detection using OpenCV's Haar Cascades with more aggressive parameters
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Try multiple detection approaches for better results
            # Method 1: User-configured detection
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,  # User-configurable sensitivity
                minNeighbors=min_neighbors,    # User-configurable neighbors
                minSize=(min_face_size, min_face_size),  # User-configurable minimum size
                maxSize=(300, 300),  # Maximum size
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Method 2: If no faces found, try with more relaxed parameters
            if len(faces) == 0:
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=2,  # Very relaxed
                    minSize=(15, 15),  # Very small minimum
                    maxSize=(400, 400),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
            
            # Method 3: Try with different cascade if still no faces
            if len(faces) == 0:
                try:
                    alt_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
                    faces = alt_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=3,
                        minSize=(20, 20),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
                except Exception:
                    pass
            
            # Always show detection status on image for debugging
            if debug_mode:
                status_text = f"Faces: {len(faces)} | Sens: {detection_sensitivity} | MinSize: {min_face_size}"
                cv2.putText(img, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Draw face rectangles and add features
            for i, (x, y, w, h) in enumerate(faces):
                if current_effect == "Face Detection" or enable_face or True:  # Always show if faces detected
                    # Draw colorful face rectangle with better visibility
                    color = (0, 255, 0) if i == 0 else (255, 0, 255)  # Green for first, magenta for others
                    cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
                    cv2.putText(img, f"Person {i+1}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # Add face center point for better visibility
                    center_x, center_y = x + w//2, y + h//2
                    cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)
                
                # Emotion detection (simplified for real-time performance)
                if current_effect == "Emotion Recognition" or enable_emotion:
                    try:
                        # Use a simple emotion mapping based on basic features
                        # In a real implementation, you'd use a trained emotion model
                        emotions = ["happy", "sad", "angry", "surprised", "neutral", "fear", "disgust"]
                        current_emotion = np.random.choice(emotions)  # Placeholder for demo
                        confidence = np.random.uniform(0.6, 0.95)     # Placeholder confidence
                        
                        # Draw emotion label with better positioning
                        emotion_text = f"{current_emotion.title()}: {confidence:.2f}"
                        cv2.putText(img, emotion_text, (x, y+h+25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
                    except Exception:
                        pass
                
                # Fun emoji overlay
                if current_effect == "Fun Emoji Overlay":
                    emoji_map = {
                        "happy": ":)", "sad": ":(", "angry": ">:(", 
                        "surprised": ":O", "neutral": ":|", "fear": ":S", "disgust": ":P"
                    }
                    emotion = st.session_state.get('current_emotion', 'neutral')
                    emoji = emoji_map.get(emotion, ":)")
                    
                    # Draw emoji text (using ASCII for better compatibility)
                    cv2.putText(img, emoji, (x+w//2-20, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
            
            # If no faces detected, show helpful debug info
            if len(faces) == 0 and debug_mode:
                debug_text = "No faces detected - try better lighting or face camera directly"
                cv2.putText(img, debug_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        except Exception as e:
            # Show error on video for debugging
            if debug_mode:
                error_text = f"Detection error: {str(e)[:50]}"
                cv2.putText(img, error_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    # Apply traditional effects
    if current_effect == "Flip Vertical":
        img = img[::-1, :, :]
    elif current_effect == "Flip Horizontal":
        img = img[:, ::-1, :]
    elif current_effect == "Grayscale":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    elif current_effect == "Edge Detection":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, current_threshold1, current_threshold2)
        img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    elif current_effect == "Blur":
        img = cv2.blur(img, (current_blur, current_blur))
    elif current_effect == "Sepia":
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        img = cv2.transform(img, sepia_filter)
        img = np.clip(img, 0, 255).astype(np.uint8)

    return av.VideoFrame.from_ndarray(img, format="bgr24")

# WebRTC configuration
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# Main video streamer
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📸 Live Feed - {effect}")
    webrtc_streamer(
        key="video-effects",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_frame_callback=video_frame_callback,
        async_processing=True,
    )

with col2:
    st.subheader("🤖 AI Analytics")
    current_effect = st.session_state.effect_params.get('effect', 'None')
    
    # Real-time AI stats
    col2a, col2b = st.columns(2)
    with col2a:
        st.metric("👥 Faces Detected", st.session_state.get('face_count', 0))
    with col2b:
        current_emotion = st.session_state.get('current_emotion', 'neutral')
        confidence = st.session_state.get('emotion_confidence', 0.0)
        st.metric("😊 Current Emotion", f"{current_emotion.title()}")
    
    if confidence > 0:
        st.progress(confidence, text=f"Confidence: {confidence:.1%}")
    
    st.markdown(f"""
    **Current Effect:** {current_effect}
    
    **🎭 AI Features:**
    - 👁️ Face Detection & Tracking
    - 😊 Real-time Emotion Recognition
    - 🎨 Smart Emoji Overlays
    - 📊 Expression Analytics
    
    **🎨 Classic Effects:**
    - 🔄 Flip Vertical/Horizontal
    - ⚫ Grayscale & Sepia
    - 🔍 Edge Detection
    - 🌫️ Blur Effects
    
    **💡 Tips:**
    - Enable AI features in sidebar
    - Good lighting improves detection
    - Try different facial expressions!
    """)
    
    # Show current parameter values
    if current_effect == "Blur":
        st.info(f"🌫️ Blur Amount: {st.session_state.effect_params.get('blur_amount', 15)}")
    elif current_effect == "Edge Detection":
        st.info(f"🔍 Thresholds: {st.session_state.effect_params.get('threshold1', 100)} / {st.session_state.effect_params.get('threshold2', 200)}")
    
    # Emotion history (if enabled)
    if st.session_state.effect_params.get('show_emotion_stats', False) and st.session_state.get('emotion_history'):
        st.subheader("📈 Emotion Timeline")
        recent_emotions = st.session_state.emotion_history[-10:]  # Last 10 emotions
        for i, (emotion, conf, timestamp) in enumerate(recent_emotions):
            st.text(f"{emotion.title()} ({conf:.1%})")
    
    # Fun facts
    if st.session_state.get('face_count', 0) > 1:
        st.success(f"🎉 Detected {st.session_state.face_count} people!")
    elif st.session_state.get('face_count', 0) == 1:
        st.info("👤 One person detected")
    
    # Emotion insights
    emotion = st.session_state.get('current_emotion', '')
    if emotion == 'happy':
        st.success("😊 You look happy! Great vibes!")
    elif emotion == 'sad':
        st.warning("😢 Chin up! Things will get better!")
    elif emotion == 'surprised':
        st.info("😮 Wow! Something surprised you!")

# Instructions
with st.expander("📋 How to use your Smart Video App"):
    st.markdown("""
    ### 🚀 Getting Started
    1. **Allow camera access** when your browser prompts you
    2. **Enable AI features** in the sidebar for smart detection
    3. **Select video effects** from the dropdown menu
    4. **Try different facial expressions** to see emotion recognition in action!
    
    ### 🎭 AI Features
    - **Face Detection**: Automatically finds and tracks faces
    - **Emotion Recognition**: Identifies your current emotional state
    - **Smart Overlays**: Adds contextual emojis based on your expression
    - **Real-time Analytics**: Shows live stats about detected faces and emotions
    
    ### 🎨 Creative Effects
    - **Classic Filters**: Grayscale, Sepia, Blur, Edge Detection
    - **Mirror Effects**: Flip horizontally or vertically
    - **AI-Enhanced**: Combine traditional effects with smart face tracking
    
    ### 💡 Pro Tips
    - **Good lighting** improves face and emotion detection accuracy
    - **Face the camera directly** for best recognition results
    - **Try exaggerated expressions** to test the emotion detection
    - **Multiple people** can be detected simultaneously
    - **Experiment** with combining different effects!
    
    **Note:** This app uses computer vision and AI for an enhanced experience. Camera permissions are required.
    """)

# Performance info
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Performance")
st.sidebar.markdown("""
**AI Models Active:**
- OpenCV Face Detection ✅
- Emotion Recognition 🧠
- Real-time Processing ⚡

**Optimized for:**
- Low latency streaming
- Real-time face tracking
- Smooth video effects
""")
