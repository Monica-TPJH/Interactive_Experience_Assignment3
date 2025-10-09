from diffusers import AutoPipelineForText2Image, LCMScheduler
import torch

model = 'lykon/dreamshaper-8-lcm'

# Optimize for macOS with MPS support
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

if device == "mps":
    # Use float32 for MPS compatibility
    pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float32)
else:
    # Use float16 for CUDA or float32 for CPU
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=dtype)

pipe.to(device)
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)

while True:
    prompt = input("Type a prompt and press enter to generate an image:\n>>> ")
    images = pipe(prompt, num_inference_steps=4, guidance_scale=1.5).images
    images[0].save("lcm_generated_image.png")
    print("Image saved as lcm_generated_image.png")
