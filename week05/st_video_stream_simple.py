import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import cv2
import numpy as np
import time

# Page configuration
st.set_page_config(
    page_title="Video Stream Effects",
    page_icon="📹",
    layout="wide"
)

st.title("📹 Smart Video Stream with Face Detection")
st.markdown("Apply real-time effects and detect faces with computer vision! 😊📸")

# Sidebar for effect selection
with st.sidebar:
    st.header("🎛️ Effect Controls")
    effect = st.selectbox(
        "Choose an effect:",
        ["None", "Flip Vertical", "Flip Horizontal", "Grayscale", "Edge Detection", "Blur", "Sepia", "Face Detection", "Face Tracking", "Fun Overlay"]
    )
    
    # AI Features Toggle
    st.subheader("🤖 Computer Vision Features")
    enable_face_tracking = st.checkbox("Enable Face Tracking", value=True)
    show_face_count = st.checkbox("Show Face Count", value=True)
    
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
    'enable_face_tracking': enable_face_tracking,
    'show_face_count': show_face_count
}

# Initialize tracking
if 'face_count' not in st.session_state:
    st.session_state.face_count = 0
if 'total_faces_detected' not in st.session_state:
    st.session_state.total_faces_detected = 0

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    
    # Get effect parameters from session state
    params = st.session_state.get('effect_params', {})
    current_effect = params.get('effect', 'None')
    current_blur = params.get('blur_amount', 15)
    current_threshold1 = params.get('threshold1', 100)
    current_threshold2 = params.get('threshold2', 200)
    enable_face = params.get('enable_face_tracking', False)
    
    # Face detection
    if enable_face or current_effect in ["Face Detection", "Face Tracking", "Fun Overlay"]:
        try:
            # Face detection using OpenCV's Haar Cascades
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Update face count
            st.session_state.face_count = len(faces)
            if len(faces) > 0:
                st.session_state.total_faces_detected += 1
            
            # Draw face rectangles and add features
            for i, (x, y, w, h) in enumerate(faces):
                if current_effect == "Face Detection" or enable_face:
                    # Draw colorful face rectangle
                    color = (0, 255, 0) if i == 0 else (255, 0, 255)  # Green for first face, magenta for others
                    cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
                    cv2.putText(img, f"Person {i+1}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Face tracking with center point
                if current_effect == "Face Tracking":
                    # Draw face rectangle
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    # Draw center point
                    center_x, center_y = x + w//2, y + h//2
                    cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)
                    # Draw tracking info
                    cv2.putText(img, f"Face {i+1} ({center_x},{center_y})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Fun overlay
                if current_effect == "Fun Overlay":
                    # Draw a fun border around the face
                    cv2.rectangle(img, (x-10, y-10), (x+w+10, y+h+10), (255, 255, 0), 3)
                    # Add a simple "hat" on top
                    hat_y = y - 30
                    if hat_y > 0:
                        cv2.rectangle(img, (x+w//4, hat_y), (x+3*w//4, y-10), (128, 0, 128), -1)
                        cv2.putText(img, "^_^", (x+w//2-15, hat_y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        except Exception as e:
            # Fallback if face detection fails
            pass
    
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
    st.subheader("🤖 Computer Vision Analytics")
    current_effect = st.session_state.effect_params.get('effect', 'None')
    
    # Real-time CV stats
    col2a, col2b = st.columns(2)
    with col2a:
        st.metric("👥 Current Faces", st.session_state.get('face_count', 0))
    with col2b:
        st.metric("📊 Total Detections", st.session_state.get('total_faces_detected', 0))
    
    st.markdown(f"""
    **Current Effect:** {current_effect}
    
    **🎭 Computer Vision Features:**
    - 👁️ Real-time Face Detection
    - 📍 Face Position Tracking
    - 🎨 Fun Visual Overlays
    - 📊 Detection Analytics
    
    **🎨 Classic Effects:**
    - 🔄 Flip Vertical/Horizontal
    - ⚫ Grayscale & Sepia
    - 🔍 Edge Detection
    - 🌫️ Blur Effects
    
    **💡 Tips:**
    - Enable face tracking in sidebar
    - Good lighting improves detection
    - Try moving around to test tracking!
    """)
    
    # Show current parameter values
    if current_effect == "Blur":
        st.info(f"🌫️ Blur Amount: {st.session_state.effect_params.get('blur_amount', 15)}")
    elif current_effect == "Edge Detection":
        st.info(f"🔍 Thresholds: {st.session_state.effect_params.get('threshold1', 100)} / {st.session_state.effect_params.get('threshold2', 200)}")
    
    # Fun facts
    face_count = st.session_state.get('face_count', 0)
    if face_count > 1:
        st.success(f"🎉 Detected {face_count} people!")
    elif face_count == 1:
        st.info("👤 One person detected")
    else:
        st.warning("👻 No faces detected")
    
    # Detection quality indicator
    if face_count > 0:
        st.success("✅ Face detection active")
    else:
        st.info("🔍 Looking for faces...")

# Instructions
with st.expander("📋 How to use your Smart Video App"):
    st.markdown("""
    ### 🚀 Getting Started
    1. **Allow camera access** when your browser prompts you
    2. **Enable face tracking** in the sidebar for smart detection
    3. **Select video effects** from the dropdown menu
    4. **Move around** to test the face tracking!
    
    ### 🎭 Computer Vision Features
    - **Face Detection**: Automatically finds and tracks faces
    - **Position Tracking**: Shows face coordinates in real-time
    - **Multi-Face Support**: Can detect multiple people simultaneously
    - **Real-time Analytics**: Shows live stats about detected faces
    
    ### 🎨 Creative Effects
    - **Classic Filters**: Grayscale, Sepia, Blur, Edge Detection
    - **Mirror Effects**: Flip horizontally or vertically
    - **CV-Enhanced**: Combine traditional effects with smart face tracking
    - **Fun Overlays**: Adds silly hats and borders to detected faces
    
    ### 💡 Pro Tips
    - **Good lighting** improves face detection accuracy
    - **Face the camera directly** for best detection results
    - **Multiple people** can be detected simultaneously
    - **Try the Fun Overlay** for entertaining effects!
    
    **Note:** This app uses OpenCV computer vision for face detection. Camera permissions are required.
    """)

# Performance info
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Performance")
st.sidebar.markdown("""
**Computer Vision Models:**
- OpenCV Face Detection ✅
- Haar Cascade Classifier 🔍
- Real-time Processing ⚡

**Optimized for:**
- Low latency streaming
- Real-time face tracking
- Smooth video effects
- Stable performance
""")