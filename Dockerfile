# Use the official Python image as the base image
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*


ENV PATH /usr/local/bin:$PATH

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Node.js (example with Node.js 18)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create and set working directory
WORKDIR /app

# Copy your package.json and package-lock.json files
COPY package*.json ./

# Install Node.js packages
RUN npm install

# Copy the rest of your application code
COPY . .

# Expose port (if needed, adjust according to your app's requirements)
EXPOSE 3000

# Command to run your application (adjust as needed)
CMD ["node", "index.js"]

