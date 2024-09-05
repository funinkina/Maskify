# Use a Node.js base image
FROM node:14

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory
WORKDIR /

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
CMD ["npm", "run", "start"]
