import cv2

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

def main():
    camera = initialize_camera()
    
    while True:
        frame = capture_frame(camera)
        display_frame(frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            resized_frame = resize_image(frame, 1120, 1120)
            save_image(resized_frame, 'captured_image.png')            
        elif key == ord('q'):
            print("Exiting...")
            break
    
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()