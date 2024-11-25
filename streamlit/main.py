# /********************************************************************************************************************
# *  Copyright 2024 Amazon.com, Inc. or its affiliates. All Rights Reserved.                                           *
# *                                                                                                                    *
# *  Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance        *
# *  with the License. A copy of the License is located at                                                             *
# *                                                                                                                    *
# *      http://aws.amazon.com/asl/                                                                                    *
# *                                                                                                                    *
# *  or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES *
# *  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    *
# *  and limitations under the License.                                                                                *
# **********************************************************************************************************************/

import os
import json
import boto3
import langchain_app
from boto3.dynamodb.conditions import Key
from flask import Flask, request
import threading
import logging
import asyncio
import psycopg2

# Setup logging.
logging.basicConfig(level=logging.INFO)
logging.info('Logging configured.')

# Prepare one-time items.
mount_path = os.environ['EFS_MOUNT_PATH']

secretmanager = boto3.client('secretsmanager')
password = json.loads(secretmanager.get_secret_value(
    SecretId=os.environ['DB_SECRET_NAME']
)['SecretString'])['password']

conn = psycopg2.connect(
    host=os.environ['DB_ENDPOINT'],
    port=os.environ['DB_PORT'],
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USERNAME'],
    password=password
)
cursor = conn.cursor()

websocket = boto3.client(
    service_name="apigatewaymanagementapi",
    endpoint_url=os.environ['WEBSOCKET_ENDPOINT']
)

# The is the primary hanlder for messages from the client. Each invocation runs asynchronously in seperate thread.
def handler(action, message, user, connection):
    # Support for asyncio.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Configure workspace for the langchain app.
    langchain_app.set_workspace(f'{mount_path}/{user}')

    # Set state for the langchain app.
    cursor.execute("SELECT state FROM user_states WHERE user_id = %s", (user,))
    result = cursor.fetchone()
    if result:
        state = result[0]
    else:
        state = None

    langchain_app.set_state(state)

    # Handle message listing.
    if action == 'LIST_MESSAGES':
        messages = langchain_app.get_messages()
        messages = [{'from': chat.type, 'message': chat.content} for chat in messages]

        response = {
            'action': action,
            'messages': messages
        }
    
    # Handle new message.
    elif action == 'SEND_MESSAGE':
        reply = langchain_app.send_message(message)

        state = langchain_app.get_state()
        cursor.execute("INSERT INTO user_states (user_id, state) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET state = %s", (user, state, state))
        conn.commit()

        response = {
            'action': action,
            'reply': reply
        }
    
    # Handle message clearing.
    elif action == 'CLEAR_MESSAGES':
        cursor.execute("DELETE FROM user_states WHERE user_id = %s", (user,))
        conn.commit()

        response = {
            'action': action,
            'data': 'OK'
        }

    logging.info('reply: ' + json.dumps(response))
    websocket.post_to_connection(
        Data=json.dumps(response).encode("utf-8"), ConnectionId=connection
    )

# Prepare flask app.
app = Flask(__name__)

# Health check endpoint for ECS.
@app.route('/health', methods=['GET'])
def health_check():
    return 'OK\n'

# Message handling.
@app.route('/messages', methods=['POST'])
def handle_messages():
    logging.info('Processing messages...')
    try:
        data = request.get_json()
        threading.Thread(target=handler, args=(data.get('action'), data.get('message'), data.get('user'), data.get('connection'))).start()
                            
        return json.dumps({
            'statusCode': 200
        })
        
    except:
        logging.error('Exception occured...')
        return json.dumps({
            'statusCode': 502
        }) 

if __name__ == "__main__":
    app.run()
