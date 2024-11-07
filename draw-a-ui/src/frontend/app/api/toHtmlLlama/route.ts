import { BedrockRuntimeClient, InvokeModelCommand, InvokeModelWithResponseStreamCommand, ConverseStreamCommand, Message } from "@aws-sdk/client-bedrock-runtime"; // Import the AWS SDK for Bedrock

import fs from 'fs';
import path from 'path';

 const client = new BedrockRuntimeClient({
      region: "us-west-2",
    });

const systemPrompt = `You are an expert tailwind developer. A user will provide you with a
low-fidelity wireframe of an application and you will return 
a single html file that uses tailwind to create the website. Use creative license to make the application more fleshed out.
if you need to insert an image, use placehold.co to create a placeholder image. Respond only with the html file.`;


async function sendImageToLlama(encodedImage: string) {
  try {
    
    
    const base64Data: string = encodedImage.split(",")[1];
    const byteData = Buffer.from(base64Data, 'base64');

    // Set the model ID, e.g., Llama 3 8b Instruct.
    const modelId = "us.meta.llama3-2-90b-instruct-v1:0";

    // Start a conversation with the user message.    
    const conversation : Message[] = [
      {
                "role": "user",
                "content": [                    
                    {
                        "image": {
                            "format": "png",
                            "source": {
                                "bytes": byteData
                            }
                        }
                    },
                    {                
                        "text": systemPrompt
                    },
                ]
            }
    ];

    const command = new ConverseStreamCommand({
      modelId,
      messages: conversation,
      //system:  [{ text: systemPrompt }],
      inferenceConfig: { maxTokens: 4096, temperature: 0.5, topP: 0.9 },
    });
    
    const apiResponse = await client.send(command);

    let completeMessage = "";

    for await (const item of apiResponse.stream!) {
      if (item.contentBlockDelta) {
        const text = item.contentBlockDelta.delta?.text
        completeMessage = completeMessage + text;
        process.stdout.write(text!);
      }
    }

    return { "html" :  completeMessage}

    } catch (error) {
      console.error('Error invoking model:', error);
    }
  }



export async function POST(request: Request) {
  
  const { image } = await request.json();

  // Make the API call to AWS Bedrock
  const resp = await sendImageToLlama(image);

  return new Response(JSON.stringify(resp), {
    headers: {
      'content-type': 'application/json; charset=UTF-8',
    },
  });
}