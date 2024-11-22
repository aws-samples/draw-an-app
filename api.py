from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
from main import (
    initialize, reset_project, aquire_image, 
    process_image, invoke_model, update_project
)
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    image: str

@app.post("/api/toHtml")
async def convert_to_html(request: ImageRequest):
    try:
        bedrock_runtime, system_prompt, chat_prompt = initialize()
        
        # Reset project
        print('Resetting project', end='', flush=True)
        reset_project()
        encoded_image = request.image
        # Capture and process image
        print('Resetting project ✅')
        print('Ready ✅', flush=True)

        print('Capturing board image', end='', flush=True)

        image = Image.open(io.BytesIO(base64.b64decode(encoded_image.split(",")[1])))
        print(' ✅', flush=True)
        #image = process_image(image)

        retry = 0
        while retry<5:
            try:
                print('Calling multimodal LLM', end='', flush=True)
                response = invoke_model(bedrock_runtime, system_prompt, chat_prompt, image, "PNG")
                break
            except Exception as e:
                retry = retry + 1
                print(traceback.format_exc())
                print(type(e).__name__ + ' ❌ \nTrying again', flush=True)
                time.sleep(1)

        print(' ✅', flush=True)
        
        # Update project
        print('Updating project', end='', flush=True)
        update_project(response)
        print(' ✅', flush=True)

        print('Done 🎉', flush=True)
        
        return {"status": "success", "message": "Project generated successfully"}
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
