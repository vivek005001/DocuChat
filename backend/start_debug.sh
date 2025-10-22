#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Export environment variables from .env
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

# Make sure we have all dependencies
echo "Ensuring dependencies are installed..."
pip3 install -r requirements.txt

# Set development environment
export ENVIRONMENT=development

# Start the server
echo "🚀 Starting DocChat backend server with authentication bypass..."
python3 main.py