import os
import shutil

template_folder = 'nextjs-app-template'
demo_folder = 'blank-nextjs-app'

def initialize():
    """Initialize Bedrock client and load prompts."""
    import boto3
    
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
    """Reset the project by cleaning up and copying template files."""
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

def update_project(contents):
    """Update project files with new content."""
    for path in contents:
        # Create all required directories.
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

        # Write the file data.
        with open(path, 'w') as file:
            file.write(contents[path])
