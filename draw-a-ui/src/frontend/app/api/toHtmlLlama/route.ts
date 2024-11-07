import { BedrockRuntimeClient, InvokeModelCommand, InvokeModelWithResponseStreamCommand, ConverseStreamCommand } from "@aws-sdk/client-bedrock-runtime"; // Import the AWS SDK for Bedrock

import fs from 'fs';
import path from 'path';

 const client = new BedrockRuntimeClient({
      region: "us-west-2",
    });

const systemPrompt = `You are an expert tailwind developer. A user will provide you with a
low-fidelity wireframe of an application and you will return 
a single html file that uses tailwind to create the website. Use creative license to make the application more fleshed out.
if you need to insert an image, use placehold.co to create a placeholder image. Respond only with the html file.`;


async function sendImageToClaude(encodedImage: string) {
  // Prepare the request payload
  //const imageBytes = fs.readFileSync("./testImage.png");
  //encodedImage = Buffer.from(imageBytes).toString('base64');



  try {
    
    
    const base64Data: string = encodedImage.split(",")[1];
    console.log(base64Data)
        // Decode the base64 string to a Buffer
    const byteData = Buffer.from(base64Data, 'base64');
    console.log(byteData)
    // Set the model ID, e.g., Llama 3 8b Instruct.
    const modelId = "us.meta.llama3-2-90b-instruct-v1:0";

    // Start a conversation with the user message.    
    const conversation = [
      {
                "role": "user",
                "content": [
                    {                
                        "text": systemPrompt
                    },
                    {
                        "image": {
                            "format": "png",
                            "source": {
                                "bytes": byteData
                            }
                        }
                    }
                ]
            }
    ];


    // Create a command with the model ID, the message, and a basic configuration.
    const command = new ConverseStreamCommand({
      modelId,
      messages: conversation,
      inferenceConfig: { maxTokens: 4096, temperature: 0.5, topP: 0.9 },
    });
    
    const apiResponse = await client.send(command);

    let completeMessage = "";

    // Decode and process the response stream
    // for await (const item of apiResponse.body!) {
    //   /** @type Chunk */
    //   const chunk = JSON.parse(new TextDecoder().decode(item.chunk!.bytes));
    //   const chunk_type = chunk.type;

    //   if (chunk_type === "content_block_delta") {
    //     const text = chunk.delta.text;
    //     completeMessage = completeMessage + text;
    //     process.stdout.write(text);
    //   }
    // }

    for await (const item of apiResponse.stream) {
      if (item.contentBlockDelta) {
        const text = item.contentBlockDelta.delta?.text
        completeMessage = completeMessage + text;
        process.stdout.write(text);
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
  const resp = await sendImageToClaude(image);

  return new Response(JSON.stringify(resp), {
    headers: {
      'content-type': 'application/json; charset=UTF-8',
    },
  });
}