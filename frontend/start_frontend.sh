#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Make sure BACKEND_URL is in .env.local
if [ -f .env.local ]; then
  if ! grep -q "BACKEND_URL" .env.local; then
    echo "Adding BACKEND_URL to .env.local"
    echo "BACKEND_URL=http://localhost:8000" >> .env.local
  fi
else
  echo "Creating .env.local with BACKEND_URL"
  echo "BACKEND_URL=http://localhost:8000" > .env.local
fi

# Start Next.js in development mode
echo "🚀 Starting Next.js frontend..."
npm run dev