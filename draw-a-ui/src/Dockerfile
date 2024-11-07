
# Use an official Node.js runtime as the base image
FROM node:18-alpine AS frontend

# Set the working directory for the frontend
WORKDIR /app/frontend

# Copy package.json and package-lock.json
COPY frontend/ /app/frontend

# Install frontend dependencies
RUN npm ci

# Copy the rest of the frontend code
#COPY frontend/ .

# Build the Next.js app
RUN npm run build

# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory for the backend
WORKDIR /app/backend

# Copy the backend requirements file
COPY backend/requirements.txt .

# Install backend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY backend .

# Copy the built frontend from the previous stage
COPY --from=frontend /app/frontend/ /app/frontend/
COPY --from=frontend /app/frontend/public /app/frontend/public

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm

# Install serve to run the Next.js app
RUN npm install -g serve

# Expose ports for both frontend and backend
EXPOSE 3000 8000

# Create a script to run both services
RUN echo '#!/bin/bash\n\
cd /app/frontend \n\
npm run start &\n\
cd /app/backend \n\
uvicorn main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Set the command to run the script
CMD ["/app/start.sh"]