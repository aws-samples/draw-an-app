import boto3
import json
import base64
import re
import os
import io
import shutil
from PIL import Image
import time
import traceback
import cv2
import logging

logger = logging.getLogger(__name__)

template_folder = 'nextjs-app-template'
demo_folder = 'blank-nextjs-app'
CORNER_COORDS = [[0, 288], [3994, 72], [3868, 2696], [357, 2852]]

def initialize_camera(camera_index=0):
    """Initialize and return a camera object."""
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        raise IOError("Cannot open webcam")
    return camera

def capture_frame(camera):
    """Capture a single frame from the camera."""
    ret, frame = camera.read()
    if not ret:
        raise IOError("Failed to capture image")
    return frame

def resize_image(image, width, height):
    """Resize the image to the specified dimensions."""
    return cv2.resize(image, (width, height))

def save_image(image, filename):
    """Save the image to a file."""
    cv2.imwrite(filename, image)
    print(f"Image saved as {filename}")

def display_frame(frame, window_name='Webcam'):
    """Display the frame in a named window."""
    cv2.imshow(window_name, frame)

def initialize():
    # Initialize Bedrock client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )

    # Open the prompt files and read their contents into a string
    with open('prompt_system.txt', 'r') as file:
        system_prompt = file.read()
    with open('prompt_assistant.txt', 'r') as file:
        chat_prompt = file.read()

    return (bedrock_runtime, system_prompt, chat_prompt)

def reset_project():
    # Remove existing code.
    if os.path.exists(demo_folder):
        shutil.rmtree(os.path.join(demo_folder, 'app'))
        shutil.rmtree(os.path.join(demo_folder, 'public'))

    # Remove database file.
    if os.path.exists('database.sqlite'):
        os.remove('database.sqlite')

    # Copy template code.
    shutil.copytree(os.path.join(template_folder, 'app'), os.path.join(demo_folder, 'app'))
    shutil.copytree(os.path.join(template_folder, 'public'), os.path.join(demo_folder, 'public'))

def aquire_image():
    img = Image.open('captured_image.jpeg')
    return img


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

def process_image(img):
    # Align image
    # img = align_image(img, np.array(CORNER_COORDS, dtype="float32"))

    # Extract neon part.
    #img = extract_neon(img)

    return img


def invoke_model(bedrock_runtime, system_prompt, chat_prompt, image, format="JPEG"):
    # Create image file and base64 encode it.
    buffer = io.BytesIO()
    image.save(buffer, format)    
    buffer.seek(0)

    bytesData = buffer.read()
    #base64_image = base64.b64encode(buffer.read()).decode('utf-8')

    # Prepare the messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": {
                                    "format": f"{format.lower()}",
                                    "source": {
                                        "bytes": bytesData
                                    }
                                }
                },            
                {
                    "text":  "Use this image and proceed."
                }
            ],
        },
        {
            "role": "assistant",
            "content": [
                {                    
                    "text": chat_prompt
                }
            ],
        }
    ]

    # System prompts
    system_prompts = [{"text": system_prompt}]

    # Inference configuration
    inference_config = {
        #"temperature": 0.0,
    
        "maxTokens": 4096,
    }

    # Additional model fields
    additional_model_fields = {
        #"anthropic_version": "bedrock-2023-05-31",
    }

    logger.info("Streaming conversation with model anthropic.claude-3-sonnet-20240229-v1:0")

    try:
        response = bedrock_runtime.converse_stream(
            #modelId='anthropic.claude-3-sonnet-20240229-v1:0',            
            #modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            #modelId='us.amazon.nova-pro-v1:0',
            #modelId='us.amazon.nova-lite-v1:0',
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config,
            additionalModelRequestFields=additional_model_fields
        )

        output = []
        stream = response.get('stream')
        if stream:
            for event in stream:
                if 'contentBlockDelta' in event:
                    text = event['contentBlockDelta']['delta']['text']
                    print(text, end="", flush=True)
                    output.append(text)

                if 'messageStop' in event:
                    print(f"\nStop reason: {event['messageStop']['stopReason']}")

                if 'metadata' in event:
                    metadata = event['metadata']
                    if 'usage' in metadata:
                        print("\nToken usage")
                        print(f"Input tokens: {metadata['usage']['inputTokens']}")
                        print(f"Output tokens: {metadata['usage']['outputTokens']}")
                        print(f"Total tokens: {metadata['usage']['totalTokens']}")
                    if 'metrics' in metadata:
                        print(f"Latency: {metadata['metrics']['latencyMs']} milliseconds")

        full_response = "".join(output)
        # Extract JSON from the full response
        json_response = re.search(r"<json>(.*?)</json>", full_response, re.DOTALL)
        if json_response:
            response = json.loads(json_response.group(1))
        else:
            response = {"error": "No JSON found in the response"}

        return response

    except Exception as err:
        logger.error("An error occurred: %s", str(err))
        print(f"An error occurred: {str(err)}")
        return {"error": str(err)}


def update_project(contents):
    for path in contents:
        # Create all required directories.
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

        # Write the file data.
        with open(path, 'w') as file:
            file.write(contents[path])

# Main flow.
def main():
    bedrock_runtime, system_prompt, chat_prompt = initialize()
    
    camera = initialize_camera()
    print("Camera initialize")

    while True:
        frame = capture_frame(camera)
        display_frame(frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            resized_frame = resize_image(frame, 1120, 1120)
            save_image(resized_frame, 'captured_image.jpeg')
            os.system('clear')
        
            print('Resetting project', end='', flush=True)
            reset_project()
            print(' ✅', flush=True)

            print('Ready ✅', flush=True)
            os.system('clear')
            print('Resetting project ✅')
            print('Ready ✅', flush=True)

            print('Capturing board image', end='', flush=True)
            image = aquire_image()
            print(' ✅', flush=True)

            print('Processing image', end='', flush=True)
            #image = process_image(image)
            print(' ✅', flush=True)

            while True:
                try:
                    print('Calling multimodal LLM', end='', flush=True)
                    response = invoke_model(bedrock_runtime, system_prompt, chat_prompt, image)
                    break
                except Exception as e:
                    print(traceback.format_exc())
                    print(type(e).__name__ + ' ❌ \nTrying again', flush=True)
                    time.sleep(1)
            print(' ✅', flush=True)

            print('Updating project', end='', flush=True)
            update_project(response)
            print(' ✅', flush=True)

            print('Done 🎉', flush=True)            
        elif key == ord('q'):
            print("Exiting...")
            break
    
    camera.release()
    cv2.destroyAllWindows()

    
if __name__ == "__main__":
    main()