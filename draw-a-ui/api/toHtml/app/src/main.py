from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import json
from typing import Dict
import os
from dotenv import load_dotenv
import base64
import traceback

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-west-2'
)

CLAUDE_SYSTEM_PROMPT = """You are an expert tailwind developer. A user will provide you with a
low-fidelity wireframe of an application and you will return 
a single html file that uses tailwind to create the website. Use creative license to make the application more fleshed out.
if you need to insert an image, use placehold.co to create a placeholder image. Respond only with the html file."""

LLAMA_SYSTEM_PROMPT = """You are an expert tailwind developer tasked with converting wireframe images into HTML code.When shown a wireframe image, analyze it carefully and create a single HTML file using Tailwind CSS that implements the design.Feel free to enhance the basic wireframe with appropriate styling and additional details.For any images needed, use placehold.co to create placeholder images.Provide only the HTML code in your response, nothing else."""

class ImageRequest(BaseModel):
    image: str

async def send_image_to_claude(encoded_image: str) -> Dict:
    try:
        # Prepare the payload
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 8192,
            "system": CLAUDE_SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": encoded_image.split(",")[1],
                            },
                        }
                    ],
                }
            ],
        }

        # Invoke the model
        response = bedrock_runtime.invoke_model_with_response_stream(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        # Process the response stream
        complete_message = ""
        for event in response['body']:
            chunk = json.loads(event['chunk']['bytes'].decode())
            if chunk['type'] == 'content_block_delta':
                complete_message += chunk['delta']['text']

        return {"html": complete_message}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

async def send_image_to_llama(encoded_image: str) -> Dict:
    try:
        # Prepare the payload for llama
        #my_url = f"""data:image/png;base64,{encoded_image}"""
        byte_data = base64.b64decode(encoded_image.split(",")[1])

        messages = [    
            {
                "role": "user",
                "content": [
                    {                
                        "text": LLAMA_SYSTEM_PROMPT
                    },
                    {
                        "image": {
                            "format": "png",
                            "source": {
                                "bytes": byte_data
                            }
                        }
                    }
                    # {
                    #     "type": "image_url",
                    #     "image_url": {
                    #         "url": my_url
                    #     }
                    # }
                ]
            }
        ]

        # Invoke the model
        response = bedrock_runtime.converse(
            modelId="us.meta.llama3-2-90b-instruct-v1:0", 
            messages=messages
        )

        # Process the response
        #response_body = json.loads(response['body'].read())
        complete_message = response["output"]["message"]["content"][0]["text"]

        return {"html": complete_message}

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/toHtml")
async def convert_to_html(request: ImageRequest):
    return await send_image_to_claude(request.image)

@app.post("/api/toHtmlLlama")
async def convert_to_html_llama(request: ImageRequest):
    return await send_image_to_llama(request.image)

@app.get("/api/health")
async def health():
    """For health check if needed"""
    return {"status": "OK"}    
