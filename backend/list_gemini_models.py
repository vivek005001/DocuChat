#!/usr/bin/env python3
"""
This script lists all available Gemini models for your API key.
Run this script to see which models you can use.
"""

import os
import sys
from pprint import pprint

# Try to load environment from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment from .env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables.")

# Check if GEMINI_API_KEY is set
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    print("Please set it using: export GEMINI_API_KEY='your-api-key'")
    print("Or create a .env file with GEMINI_API_KEY=your-api-key")
    sys.exit(1)

# Try to import google.generativeai
try:
    import google.generativeai as genai
    print(f"Successfully imported google.generativeai")
except ImportError:
    print("ERROR: google.generativeai package not installed.")
    print("Install it using: pip install google-generativeai>=0.3.0")
    sys.exit(1)

# Configure the API
print(f"Configuring Gemini with API key: {api_key[:5]}...{api_key[-4:] if len(api_key) > 8 else ''}")
genai.configure(api_key=api_key)

# List available models
print("\nListing available models...")
try:
    # In newer versions of the library, list_models returns a generator
    models = list(genai.list_models())
    
    print(f"\nFound {len(models)} models:")
    print("-" * 60)
    
    gemini_models = []
    other_models = []
    
    for model in models:
        if "gemini" in model.name:
            gemini_models.append(model)
        else:
            other_models.append(model)
    
    # Print Gemini models first
    print(f"GEMINI MODELS ({len(gemini_models)}):")
    for model in gemini_models:
        print(f"  - {model.name}")
        print(f"    Supported generation methods: {', '.join(model.supported_generation_methods)}")
    
    # Print other models
    if other_models:
        print(f"\nOTHER MODELS ({len(other_models)}):")
        for model in other_models:
            print(f"  - {model.name}")
            print(f"    Supported generation methods: {', '.join(model.supported_generation_methods)}")
    
    # Recommend a model to use
    recommended = next((m for m in gemini_models if "gemini-1.5" in m.name), None)
    if not recommended:
        recommended = next((m for m in gemini_models if "gemini-pro" in m.name), None)
    
    if recommended:
        print("\n" + "=" * 60)
        print(f"RECOMMENDED MODEL: {recommended.name}")
        print(f"Update your llm.py file to use this model name.")
        print("=" * 60)
    
except Exception as e:
    print(f"Error listing models: {e}")

print("\nTo test a specific model, you can use:")
print("genai.GenerativeModel('model-name').generate_content('Hello')")