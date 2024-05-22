#!/bin/sh

# Navigate to app directory
cd /app

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo "Node modules not found. Installing..."
  npm install --legacy-peer-deps
fi

# Start the Angular application
ng serve --host 0.0.0.0
