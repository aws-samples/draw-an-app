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
import streamlit as st
import numpy as np

template_folder = 'nextjs-app-template'
demo_folder = 'blank-nextjs-app'

def initialize():
    # Initialize Bedrock client
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime'
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

def process_image(img):
    return img

def invoke_model(bedrock_runtime, system_prompt, chat_prompt, image, format="JPEG"):
    # Create image file and base64 encode it.
    buffer = io.BytesIO()
    image.save(buffer, format)    
    buffer.seek(0)

    base64_image = base64.b64encode(buffer.read()).decode('utf-8')

    # Prepare the payload
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8192,
        "temperature": 0.0,
        "top_k": 1,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/"+format.lower(),
                            "data": base64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Use this image and proceed."
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": chat_prompt
                    }
                ],
            }
        ],
    }

    # Invoke the model
    result = bedrock_runtime.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )

    # Process the response
    response = json.loads(result['body'].read())
    response = response['content'][0]['text']
    print(response)
    response = re.search(r"<json>(.*?)</json>", response, re.DOTALL).group(1)
    response = json.loads(response)

    return response

def update_project(contents):
    for path in contents:
        # Create all required directories.
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

        # Write the file data.
        with open(path, 'w') as file:
            file.write(contents[path])

def main():
    st.set_page_config(page_title="Draw-an-App", layout="wide")
    st.title("Draw-an-App")
    st.write("Upload an image of your app design to generate the code.")

    # Initialize on first run
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.bedrock_runtime, st.session_state.system_prompt, st.session_state.chat_prompt = initialize()

    # File uploader
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        image = image.resize((1120, 1120))
        st.image(image, caption="Original Image", use_column_width=True)

        if st.button("Generate App"):
            with st.spinner("Processing..."):
                # Reset project
                st.text("Resetting project...")
                reset_project()

                # Process image
                st.text("Processing image...")
                processed_image = process_image(image)
                st.image(processed_image, caption="Processed Image", use_column_width=True)

                # Call LLM
                st.text("Generating app code...")
                try:
                    response = invoke_model(
                        st.session_state.bedrock_runtime,
                        st.session_state.system_prompt,
                        st.session_state.chat_prompt,
                        processed_image
                    )
                    
                    # Update project
                    st.text("Updating project...")
                    update_project(response)
                    
                    st.success("App generated successfully! 🎉")
                    st.balloons()
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.text(traceback.format_exc())

if __name__ == "__main__":
    main()
