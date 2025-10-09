from diffusers import DiffusionPipeline


import torch

model = "runwayml/stable-diffusion-v1-5"

# Load the model and move it to the GPU if available
# Use float32 for MPS compatibility on Mac
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

if device == "mps":
    # Use float32 for MPS compatibility
    pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float32)
else:
    # Use float16 for CUDA or float32 for CPU
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=dtype)

pipe.to(device)

while True:
    prompt = input("Type a prompt and press enter to generate an image:\n>>> ")
    
    # Generate the image, for options see:
    # https://huggingface.co/docs/diffusers/en/api/pipelines/stable_diffusion/text2img
    images = pipe(prompt, num_inference_steps=20).images

    images[0].save("generated_image.png")
