
from PIL import Image
import numpy as np

def extract_neon(pixels):
    # Color to alpha algorithm.
    color = np.array([0,0,0])
    transparency_threshold = 0.8
    opacity_threshold = 1.0

    distances = np.amax(abs(pixels[:,:,:3] - color), axis=2)/255
    alpha = (distances - transparency_threshold) / abs(opacity_threshold - transparency_threshold)
    alpha = np.clip(alpha, 0, 1)

    # Update alpha.
    pixels[:, :, 3] = alpha * 255

# Execute color to alpha.
input_image_path = "IMG_9126.jpg"
output_image_path = "out.png"

# Read input image.
img = Image.open(input_image_path).convert("RGBA")
pixels = np.array(img)

extract_neon(pixels)

# Write the output image
output_img = Image.fromarray(pixels, "RGBA")
output_img.save(output_image_path)
print(f"Image saved to {output_image_path}")