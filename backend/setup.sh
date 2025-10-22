#!/bin/bash

# Simple setup script for DocChat backend

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
  echo "Virtual environment not activated."
  echo "Please activate your virtual environment first with:"
  echo "  source venv/bin/activate"
  exit 1
fi

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt
pip install python-dotenv google-generativeai

# Create .env file if it doesn't exist
if [[ ! -f .env ]]; then
  echo "Creating .env file..."
  
  # Check if GEMINI_API_KEY is in the environment
  if [[ "$GEMINI_API_KEY" != "" ]]; then
    echo "GEMINI_API_KEY=$GEMINI_API_KEY" > .env
    echo "Added GEMINI_API_KEY from environment to .env file"
  else
    echo "# Add your Gemini API key here" > .env
    echo "GEMINI_API_KEY=your_api_key_here" >> .env
    echo "Created .env file. Please edit it to add your GEMINI_API_KEY."
  fi
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the server:"
echo "  uvicorn main:app --reload"
echo ""
echo "If you haven't added your GEMINI_API_KEY yet, you can:"
echo "1. Edit the .env file directly, or"
echo "2. Set it in your environment with: export GEMINI_API_KEY='your-key-here'"