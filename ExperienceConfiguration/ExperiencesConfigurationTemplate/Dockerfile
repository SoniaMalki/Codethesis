# Build stage
FROM node:20.11.0 as build
WORKDIR /app

# Copy package.json and package-lock.json to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps
RUN npm install -g @angular/cli

# Copy the rest of the application code
COPY . .

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Expose the port the app runs on
EXPOSE 4200

# Run the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
