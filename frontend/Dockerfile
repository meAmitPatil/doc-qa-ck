# Frontend Dockerfile
FROM node:16

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the entire frontend application
COPY . .

# Build the application
RUN npm run build

# Expose the frontend port
EXPOSE 3000

# Start the application
CMD ["npm", "run", "start"]