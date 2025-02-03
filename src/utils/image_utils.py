import numpy as np
from PIL import Image

CORNER_COORDS = [[0, 288], [3994, 72], [3868, 2696], [357, 2852]]

def process_image(img):
    """Process the image for model input."""
    return img

def calculate_perspective_matrix(src_points, dst_points):
    """Calculate perspective transformation matrix."""
    matrix = []
    for src, dst in zip(src_points, dst_points):
        matrix.append([src[0], src[1], 1, 0, 0, 0, -dst[0]*src[0], -dst[0]*src[1], -dst[0]])
        matrix.append([0, 0, 0, src[0], src[1], 1, -dst[1]*src[0], -dst[1]*src[1], -dst[1]])

    matrix = np.array(matrix, dtype=np.float64)
    _, _, V = np.linalg.svd(matrix)
    H = V[-1, :].reshape((3, 3))

    return np.linalg.inv(H / H[2, 2])

def align_image(img, src_pts):
    """Align image using perspective transformation."""
    # Get width and height
    width, height = img.size

    # Define the destination points
    dst_pts = np.array([
        [0, 0], 
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Apply the perspective transformation
    aligned_image = img.transform(
        (width, height),
        Image.PERSPECTIVE,
        data=calculate_perspective_matrix(src_pts, dst_pts).flatten()[:8],
        resample=Image.BICUBIC
    )

    return aligned_image

def extract_neon(img):
    """Extract neon effect from image."""
    color = np.array([0,0,0])
    transparency_threshold = 0.8
    opacity_threshold = 1.0

    pixels = np.array(img)
    opaque_pixels = pixels[:,:,:3]

    distances = np.amax(abs(opaque_pixels - color), axis=2)/255
    alpha = (distances - transparency_threshold) / abs(opacity_threshold - transparency_threshold)
    alpha = np.clip(alpha, 0, 1)

    # Use alpha values as color for all channels
    opaque_pixels[:, :, 0] = alpha * 255
    opaque_pixels[:, :, 1] = alpha * 255
    opaque_pixels[:, :, 2] = alpha * 255

    return Image.fromarray(opaque_pixels, "RGB")

def acquire_image(path='captured_image.jpeg'):
    """Load image from file."""
    return Image.open(path)
