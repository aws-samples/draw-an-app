
# Draw-an-App

This project uses AWS Bedrock's Claude 3 Sonnet model to convert hand-drawn UI sketches into working web applications. It captures images through a webcam, processes them, and generates corresponding web application code.

## Prerequisites

- Python 3.8 or higher
- Webcam
- AWS Account with Bedrock access
- Access to Claude 3 Sonnet model in AWS Bedrock
- Git

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd draw-an-app
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## AWS Bedrock Configuration

1. Configure AWS credentials:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2  # or your preferred region
```

Alternatively, you can configure AWS credentials using the AWS CLI:
```bash
aws configure
```

2. Verify Bedrock Access:
- Ensure you have access to the Claude 3 Sonnet model in AWS Bedrock
- Verify your AWS account has the necessary permissions to invoke the Bedrock runtime

## System Check

Before running the application, verify:

1. Your webcam is properly connected and accessible
2. You have access to AWS Bedrock's Claude 3 Sonnet model
3. AWS credentials are properly configured

## Usage

1. Start the Next.js development server:
```bash
cd blank-nextjs-app
npm install
npm run dev
```
Keep this server running to view your generated applications at http://localhost:3000

2. In a new terminal, run the main application:
```bash
# Make sure you're in the project root directory
python main_v2.py
```

3. When the webcam window opens:
   - Press SPACE to capture and process an image
   - Press Q to quit the application

4. After capturing an image:
   - The system will process the image
   - Generate corresponding web application code
   - Update the project files automatically
   - View the generated application at http://localhost:3000 (the page will auto-update)

## Project Structure

- `main_v2.py`: Main application file
- `prompt_system.txt`: System prompt for Claude
- `prompt_assistant.txt`: Assistant prompt for Claude
- `requirements.txt`: Python dependencies
- `nextjs-app-template/`: Template for generated web applications
- `blank-nextjs-app/`: Working directory for generated applications

## Troubleshooting

1. Webcam Issues:
   - Ensure your webcam is properly connected
   - Check if other applications are using the webcam
   - Try different camera indices if multiple cameras are present

2. AWS Bedrock Access:
   - Verify AWS credentials are correctly set
   - Ensure you have access to the Claude 3 Sonnet model
   - Check AWS region configuration

3. Python Environment:
   - Ensure virtual environment is activated
   - Verify all dependencies are installed correctly
   - Check Python version compatibility

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

