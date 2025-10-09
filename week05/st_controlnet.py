import streamlit as st
import numpy as np
import torch
import cv2
from PIL import Image

# Add error handling for diffusers import
try:
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
except ImportError as e:
    st.error(f"❌ Error importing diffusers: {e}")
    st.info("💡 Please install diffusers: pip install diffusers")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="ControlNet Image Generator",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 ControlNet Image Generator")
st.markdown("Upload an image to extract edges, then generate a new image following that structure!")

# Add a sidebar with instructions
with st.sidebar:
    st.markdown("### 📋 How to use:")
    st.markdown("""
    1. **Upload an image** using the file uploader
    2. **View the edge detection** (Canny edges)
    3. **Enter a text prompt** describing what you want to generate
    4. **Wait for the magic** to happen! ✨
    """)
    
    st.markdown("### 💡 Example prompts:")
    st.markdown("""
    - "a beautiful painting in Van Gogh style"
    - "a futuristic cyberpunk city"
    - "a magical forest with glowing trees"
    - "an abstract digital artwork"
    """)

if "pipeline" not in st.session_state:
    # Check for MPS availability, otherwise use CPU
    if torch.backends.mps.is_available():
        device = "mps"
        torch_dtype = torch.float16
        st.info("🚀 Using Apple Silicon MPS acceleration")
    else:
        device = "cpu"
        torch_dtype = torch.float32
        st.info("💻 Using CPU for inference")
    
    with st.spinner("🔄 Loading ControlNet models... This may take a moment."):
        try:
            # Set number of threads to prevent mutex issues
            torch.set_num_threads(1)
            
            # Use float32 for better CPU compatibility
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny", 
                torch_dtype=torch_dtype,
                use_safetensors=True
            )
            pipe = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5", 
                controlnet=controlnet, 
                torch_dtype=torch_dtype,
                use_safetensors=True,
                safety_checker=None,
                requires_safety_checker=False
            )

            # Move to device and optimize for better performance
            pipe.to(device)
            if device == "cpu":
                pipe.enable_model_cpu_offload()
            
            # Set scheduler for faster inference
            pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
            
            st.session_state["pipeline"] = pipe
            st.success(f"✅ ControlNet loaded successfully on {device.upper()}!")
            
        except Exception as e:
            st.error(f"❌ Error loading ControlNet: {str(e)}")
            st.info("💡 This might be due to the model downloading for the first time. Please wait and refresh.")
            st.session_state["pipeline"] = None

def do_canny(image):
    image = np.array(image)
    # get canny image
    image = cv2.Canny(image, 100, 200)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    canny_image = Image.fromarray(image)

    return canny_image

if uploaded_file := st.file_uploader("📁 Choose an image file", type=['png', 'jpg', 'jpeg']):
    uploaded_file = Image.open(uploaded_file)
    
    # Display original and Canny edge side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📸 Original Image")
        st.image(uploaded_file, use_container_width=True)
    
    with col2:
        st.subheader("🔍 Edge Detection (Canny)")
        canny_image = do_canny(uploaded_file)
        st.image(canny_image, use_container_width=True)
    
    # Prompt input
    prompt = st.text_input("✍️ Enter your prompt:", placeholder="Describe what you want to generate...")
    
    if prompt:
        if st.button("🎨 Generate Image", type="primary"):
            with st.spinner("🎭 Generating your masterpiece..."):
                try:
                    image = st.session_state["pipeline"](
                        prompt, 
                        image=canny_image, 
                        num_inference_steps=20
                    ).images[0]
                    
                    st.subheader("✨ Generated Result")
                    st.image(image, use_container_width=True)
                    
                    # Save the generated image
                    image.save("controlnet_generated.png")
                    st.success("🎉 Image generated and saved as 'controlnet_generated.png'!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating image: {str(e)}")
else:
    st.info("👆 Please upload an image to get started!")





