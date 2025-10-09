import streamlit as st
import numpy as np
import cv2
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="ControlNet Image Generator (Simple)",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 ControlNet Image Generator (Simple Version)")
st.markdown("Upload an image to extract edges and see the preprocessing step!")
st.info("💡 This is a simplified version that shows the ControlNet preprocessing without the heavy AI models to avoid system compatibility issues.")

# Add a sidebar with instructions
with st.sidebar:
    st.markdown("### 📋 How to use:")
    st.markdown("""
    1. **Upload an image** using the file uploader
    2. **View the edge detection** (Canny edges)
    3. **Adjust edge detection parameters** with the sliders
    4. **Download the processed edge image** for use with ControlNet elsewhere
    """)
    
    st.markdown("### 🎛️ Edge Detection Controls:")
    low_threshold = st.slider("Low Threshold", 50, 150, 100)
    high_threshold = st.slider("High Threshold", 150, 300, 200)
    
    st.markdown("### 💡 What is ControlNet?")
    st.markdown("""
    ControlNet allows you to control Stable Diffusion image generation using:
    - **Edge maps** (Canny edges)
    - **Depth maps**
    - **Pose detection**
    - **Segmentation masks**
    
    This tool creates the edge map input that ControlNet needs!
    """)

def do_canny(image, low_threshold=100, high_threshold=200):
    """Apply Canny edge detection to an image"""
    image = np.array(image)
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Apply Canny edge detection
    edges = cv2.Canny(gray, low_threshold, high_threshold)
    
    # Convert back to 3-channel image
    edges_3ch = np.stack([edges, edges, edges], axis=2)
    canny_image = Image.fromarray(edges_3ch)
    
    return canny_image

def enhance_image_quality(image):
    """Apply some basic image enhancements"""
    img_array = np.array(image)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(img_array, (3, 3), 0)
    
    # Enhance contrast
    lab = cv2.cvtColor(blurred, cv2.COLOR_RGB2LAB)
    L, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    L = clahe.apply(L)
    enhanced = cv2.merge([L, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
    
    return Image.fromarray(enhanced)

# File uploader
uploaded_file = st.file_uploader("📁 Choose an image file", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Load and display the original image
    original_image = Image.open(uploaded_file)
    
    # Create three columns for different views
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📸 Original Image")
        st.image(original_image, use_container_width=True)
    
    with col2:
        st.subheader("✨ Enhanced Image")
        enhanced_image = enhance_image_quality(original_image)
        st.image(enhanced_image, use_container_width=True)
    
    with col3:
        st.subheader("🔍 Edge Detection (Canny)")
        canny_image = do_canny(enhanced_image, low_threshold, high_threshold)
        st.image(canny_image, use_container_width=True)
    
    # Image statistics
    st.subheader("📊 Image Analysis")
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric("Original Size", f"{original_image.size[0]} × {original_image.size[1]}")
    
    with col_stats2:
        # Count edge pixels
        edges_array = np.array(canny_image)[:,:,0]
        edge_pixels = np.sum(edges_array > 0)
        total_pixels = edges_array.shape[0] * edges_array.shape[1]
        edge_percentage = (edge_pixels / total_pixels) * 100
        st.metric("Edge Density", f"{edge_percentage:.1f}%")
    
    with col_stats3:
        st.metric("File Format", uploaded_file.type.split('/')[-1].upper())
    
    # Download buttons
    st.subheader("💾 Download Processed Images")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # Save enhanced image to bytes
        import io
        enhanced_bytes = io.BytesIO()
        enhanced_image.save(enhanced_bytes, format='PNG')
        enhanced_bytes = enhanced_bytes.getvalue()
        
        st.download_button(
            label="📥 Download Enhanced Image",
            data=enhanced_bytes,
            file_name="enhanced_image.png",
            mime="image/png"
        )
    
    with col_dl2:
        # Save Canny edge image to bytes
        canny_bytes = io.BytesIO()
        canny_image.save(canny_bytes, format='PNG')
        canny_bytes = canny_bytes.getvalue()
        
        st.download_button(
            label="📥 Download Edge Map",
            data=canny_bytes,
            file_name="canny_edges.png",
            mime="image/png"
        )
    
    # Advanced controls
    with st.expander("🔧 Advanced Edge Detection"):
        st.markdown("### Fine-tune the edge detection:")
        
        col_adv1, col_adv2 = st.columns(2)
        with col_adv1:
            blur_kernel = st.slider("Blur Kernel Size", 1, 9, 3, step=2)
            
        with col_adv2:
            dilate_iterations = st.slider("Edge Thickness", 0, 3, 1)
        
        if st.button("🔄 Apply Advanced Settings"):
            # Apply Gaussian blur before edge detection
            img_array = np.array(enhanced_image)
            blurred = cv2.GaussianBlur(img_array, (blur_kernel, blur_kernel), 0)
            
            # Apply Canny
            gray = cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, low_threshold, high_threshold)
            
            # Dilate edges to make them thicker if requested
            if dilate_iterations > 0:
                kernel = np.ones((3,3), np.uint8)
                edges = cv2.dilate(edges, kernel, iterations=dilate_iterations)
            
            # Convert back to 3-channel
            edges_3ch = np.stack([edges, edges, edges], axis=2)
            advanced_canny = Image.fromarray(edges_3ch)
            
            st.subheader("🎨 Advanced Edge Detection Result")
            st.image(advanced_canny, use_container_width=True)

else:
    st.info("👆 Please upload an image to get started!")
    
    # Show example images
    st.subheader("🎨 What you can do with this tool:")
    
    st.markdown("""
    ### 🔍 Edge Detection Features:
    - **Canny Edge Detection**: Industry-standard edge detection algorithm
    - **Adjustable Parameters**: Fine-tune sensitivity with sliders
    - **Image Enhancement**: Automatic noise reduction and contrast improvement
    - **Multiple Output Formats**: Download processed images for use elsewhere
    
    ### 🎯 Use Cases:
    - **ControlNet Preprocessing**: Create control images for Stable Diffusion
    - **Computer Vision**: Extract structural information from images
    - **Art & Design**: Create line art and sketches from photos
    - **Architecture**: Extract building outlines and floor plans
    
    ### 💡 Pro Tips:
    - **Sharp Photos** work best for edge detection
    - **High Contrast** images produce cleaner edges
    - **Adjust Thresholds** to capture fine details or reduce noise
    - **Download Edge Maps** to use with full ControlNet models elsewhere
    """)

# Footer
st.markdown("---")
st.markdown("### 🛠️ Technical Details")
st.markdown("""
This simplified version uses **OpenCV** for image processing and avoids heavy AI model loading to ensure compatibility across all systems.
For full ControlNet image generation, you can use the edge maps created here with online ControlNet services or dedicated AI hardware.
""")