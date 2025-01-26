import time
import traceback
import os
import logging
from utils.camera_utils import (
    initialize_camera, capture_frame, resize_image, 
    save_image, display_frame, release_camera
)
from utils.project_utils import initialize, reset_project, update_project
from utils.image_utils import process_image, acquire_image
from utils.aws_utils import invoke_model_stream

logger = logging.getLogger(__name__)

def main():
    bedrock_runtime, system_prompt, chat_prompt = initialize()
    
    camera = initialize_camera()
    print("Camera initialized")

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
            image = acquire_image()
            print(' ✅', flush=True)

            print('Processing image', end='', flush=True)
            image = process_image(image)
            print(' ✅', flush=True)

            while True:
                try:
                    print('Calling multimodal LLM', end='', flush=True)
                    response = invoke_model_stream(bedrock_runtime, system_prompt, chat_prompt, image)
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
    
    release_camera(camera)

if __name__ == "__main__":
    main()
