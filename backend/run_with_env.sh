#!/bin/bash

# Import environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Run the Python server with all environment variables available
python3 main.py