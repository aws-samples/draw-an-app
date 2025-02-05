import json
import base64
import re
import io
import logging
import time
import traceback

logger = logging.getLogger(__name__)




def invoke_model(bedrock_runtime, system_prompt, chat_prompt, image, format="JPEG"):
    """Invoke AWS Bedrock model with image input."""
    # Create image file and base64 encode it
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
                            "media_type": f"image/{format.lower()}",
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
    complete_response = response
    print(response)
    response = re.search(r"<json>(.*?)</json>", response, re.DOTALL).group(1)
    response = json.loads(response)

    return (response, complete_response)

def invoke_model_stream(bedrock_runtime, system_prompt, chat_prompt, image, format="JPEG"):
    """Invoke AWS Bedrock model with streaming response."""
    # Create image file and encode
    buffer = io.BytesIO()
    image.save(buffer, format)    
    buffer.seek(0)
    bytes_data = buffer.read()

    # Prepare messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": f"{format.lower()}",
                        "source": {
                            "bytes": bytes_data
                        }
                    }
                },            
                {
                    "text": "Use this image and proceed."
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
        "maxTokens": 4096,
    }

    try:
        response = bedrock_runtime.converse_stream(
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config,
            additionalModelRequestFields={}
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
