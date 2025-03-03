# Use the official Node.js 22 image.
FROM node:22-alpine

# Set the working directory in the container.
WORKDIR /app

# Copy package.json and package-lock.json to the working directory.
COPY package*.json ./

# Install dependencies.
RUN npm install

# Copy the rest of the application files to the working directory.
COPY . .

# Expose the port the app runs in.
EXPOSE 3000

# Start the app.
CMD ["npm", "run", "dev"]