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

FROM ubuntu:focal

# Setup timezone.
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install primary dependencies.
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install git curl python3 python3-pip python3-venv -y

# Install amazon-efs-utils.
RUN apt-get install binutils cargo pkg-config libssl-dev -y
RUN git clone https://github.com/aws/efs-utils
RUN cd efs-utils && \
./build-deb.sh && \
apt-get -y install ./build/amazon-efs-utils*deb

# Install NodeJS.
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash
RUN apt-get install nodejs

# Clean cache.
RUN rm -rf /var/lib/apt/lists/*

# Install node and python packages.
RUN npm install -g create-react-app
RUN pip install psycopg2-binary flask langchain langchain-community boto3 duckduckgo-search git-remote-codecommit

# Copy the app.
COPY . /app
WORKDIR /app

# Run Flask server.
EXPOSE 5000

# ENV FLASK_DEBUG=1
CMD ["flask", "--app", "main.py", "run", "--host=0.0.0.0"]