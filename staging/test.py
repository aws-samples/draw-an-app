
from PIL import Image
import numpy as np

def extract_neon(img):
    # GIMP's Color to alpha algorithm.
    color = np.array([0,0,0])
    transparency_threshold = 0.8
    opacity_threshold = 1.0

    pixels = np.array(img)
    opaque_pixels = pixels[:,:,:3]

    distances = np.amax(abs(opaque_pixels - color), axis=2)/255
    alpha = (distances - transparency_threshold) / abs(opacity_threshold - transparency_threshold)
    alpha = np.clip(alpha, 0, 1)

    # Use alpha values as color for all channels to get the black and white image.
    opaque_pixels[:, :, 0] = alpha * 255
    opaque_pixels[:, :, 1] = alpha * 255
    opaque_pixels[:, :, 2] = alpha * 255

    # Create neon image and return.
    neon_image = Image.fromarray(opaque_pixels, "RGB")
    return neon_image

def calculate_perspective_matrix(src_points, dst_points):
    matrix = []
    for src, dst in zip(src_points, dst_points):
        matrix.append([src[0], src[1], 1, 0, 0, 0, -dst[0]*src[0], -dst[0]*src[1], -dst[0]])
        matrix.append([0, 0, 0, src[0], src[1], 1, -dst[1]*src[0], -dst[1]*src[1], -dst[1]])

    matrix = np.array(matrix, dtype=np.float64)
    _, _, V = np.linalg.svd(matrix)
    H = V[-1, :].reshape((3, 3))

    return np.linalg.inv(H / H[2, 2])

def align_image(img, src_pts):
    # Get width and height
    width, height = img.size

    # Define the destination points. Points are in the top-left, top-right, bottom-right and bottom-left order.
    dst_pts = np.array([
        [0, 0], 
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Apply the perspective transformation using PIL's transform method
    aligned_image = img.transform(
        (width, height),
        Image.PERSPECTIVE,
        data=calculate_perspective_matrix(src_pts, dst_pts).flatten()[:8],  # PIL expects 8 values for perspective transform
        resample=Image.BICUBIC
    )

    return aligned_image

# Execute color to alpha.
input_image_path = "IMG_9126.jpg"
output_image_path = "out.jpg"

# Read input image.
img = Image.open(input_image_path)

# Align image
img = align_image(img, np.array([
        [0, 288],
        [3994, 72], 
        [3868, 2696],
        [357, 2852]
    ], dtype="float32"))

# Extract neon part.
output_img = extract_neon(img)

# Write the output image
output_img.save(output_image_path)
print(f"Image saved to {output_image_path}")