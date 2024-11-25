import boto3
import json
import base64
import re
import os
import io
import shutil
from PIL import Image
import numpy as np
import time
import traceback
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain_aws import ChatBedrockConverse
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain.chains import LLMChain
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

template_folder = 'nextjs-app-template'
demo_folder = 'blank-nextjs-app'
CORNER_COORDS = [[0, 288], [3994, 72], [3868, 2696], [357, 2852]]

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
    img = Image.open('staging/IMG_9126.jpeg')
    return img

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

def process_image(img):
    # Align image
    # img = align_image(img, np.array(CORNER_COORDS, dtype="float32"))

    # Extract neon part.
    img = extract_neon(img)

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
                        "text": "Use this image and proceed. "
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
    # print(response)
    response = re.search(r"<json>(.*?)</json>", response, re.DOTALL).group(1)
    response = json.loads(response)

    return response

def invoke_model_langchain(bedrock_runtime, system_prompt, chat_prompt, image, format="JPEG"):
    # Create image file and base64 encode it.
    buffer = io.BytesIO()
    image.save(buffer, format)    
    buffer.seek(0)

    base64_image = base64.b64encode(buffer.read()).decode('utf-8')

    # Initialize Bedrock LLM

    llm = ChatBedrock(
        model='anthropic.claude-3-5-sonnet-20241022-v2:0',
        temperature=0,
        max_tokens=8192,
        client=bedrock_runtime,
    )

    # Create a JSON output parser
    json_parser = JsonOutputParser()
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Use this image and proceed.You must always return valid JSON"},
            {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type":  "image/"+format.lower(),
                                "data": base64_image,
                            },
            }            
        ],
    )

    format_instructions = json_parser.get_format_instructions()
    # Define the chat prompt template
    chat_template = ChatPromptTemplate.from_messages([
        ("system", "{system_prompt}"),
        message,
        ("ai", "{chat_prompt}")
    ])

    # Create the LLMChain
    # chain = LLMChain(
    #     llm=llm,
    #     prompt=chat_template,
    #     output_parser=json_parser
    # )

    chain = chat_template | llm | StrOutputParser()


    # Invoke the chain
    result = chain.invoke({"chat_prompt": chat_prompt, "system_prompt" : system_prompt})

    print(result)
    # Process the response
    response = result
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

# Main flow.
def main():
    bedrock_runtime, system_prompt, chat_prompt = initialize()

    while True:
        os.system('clear')
        
        print('Resetting project', end='', flush=True)
        reset_project()
        print(' ✅', flush=True)

        print('Ready ✅', flush=True)
        input()

        os.system('clear')
        print('Resetting project ✅')
        print('Ready ✅', flush=True)

        print('Capturing board image', end='', flush=True)
        image = aquire_image()
        print(' ✅', flush=True)

        #print('Processing image', end='', flush=True)
        #image = process_image(image)
        #print(' ✅', flush=True)

        while True:
            try:
                print('Calling multimodal LLM', end='', flush=True)
                response = invoke_model_langchain(bedrock_runtime, system_prompt, chat_prompt, image)
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
        break

if __name__ == "__main__":
    main()