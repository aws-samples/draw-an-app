import { BedrockRuntimeClient, InvokeModelCommand, InvokeModelWithResponseStreamCommand } from "@aws-sdk/client-bedrock-runtime"; // Import the AWS SDK for Bedrock

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

  const payload = {
    anthropic_version: 'bedrock-2023-05-31',
    max_tokens: 8192,
    system: systemPrompt,
    messages: [      
      {
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: 'image/png', // Adjust the media type if necessary
              data: encodedImage.split(",")[1],              
            },
          }
        ],
      },
    ],
  };

  // Invoke the model
  const params = {
    modelId: 'anthropic.claude-3-5-sonnet-20240620-v1:0', // Use the correct model ID
    contentType: "application/json",
    accept: "application/json",
    body: JSON.stringify(payload),
  };

  try {
    

    const command = new InvokeModelWithResponseStreamCommand(params);
    const apiResponse = await client.send(command);

    let completeMessage = "";

    // Decode and process the response stream
    for await (const item of apiResponse.body!) {
      /** @type Chunk */
      const chunk = JSON.parse(new TextDecoder().decode(item.chunk!.bytes));
      const chunk_type = chunk.type;

      if (chunk_type === "content_block_delta") {
        const text = chunk.delta.text;
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