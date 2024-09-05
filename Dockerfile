# Use a Node.js base image
FROM node:14

# Install Python and required system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    poppler-utils

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port and start the app
EXPOSE 3000
# CMD ["node", "index.js"]

# Start the container with a Bash shell
CMD ["node", "index.js"]