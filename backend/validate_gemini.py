import os
import sys

# Check if GEMINI_API_KEY is set
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY environment variable is not set.")
    print("Set it using: export GEMINI_API_KEY='your-api-key-here'")
    print("You can get a key from https://ai.google.dev/")
    print("Continuing with checks but API calls will fail...")

print("=== Gemini API Test ===")

# Try to import Google's Generative AI library
try:
    import google.generativeai as genai
    print("✓ Successfully imported google.generativeai")
    
    # Try setting up with API key if provided
    if api_key:
        try:
            genai.configure(api_key=api_key)
            print("✓ Successfully configured Gemini client with API key")
            
            # Try listing available models
            try:
                models = genai.list_models()
                gemini_models = [m.name for m in models if 'gemini' in m.name]
                if gemini_models:
                    print(f"✓ Available Gemini models: {', '.join(gemini_models)}")
                else:
                    print("⚠️ No Gemini models found in available models")
            except Exception as e:
                print(f"✗ Error listing models: {str(e)}")
                
        except Exception as e:
            print(f"✗ Error configuring Gemini client: {str(e)}")
    
except ImportError as e:
    print(f"✗ Could not import google.generativeai: {e}")
    print("  Run 'pip install google-generativeai>=0.3.0' to install it")

# Import and test our LLM module
print("\n=== Testing our LLM module ===")
try:
    from core.llm import ask_llm
    
    # Test with mock data
    mock_contexts = [
        {"text": "This is a test document about artificial intelligence."}, 
        {"text": "Gemini is Google's large language model for developers."}
    ]
    
    try:
        print("Attempting to call ask_llm function...")
        if api_key:
            answer = ask_llm("What is this document about?", mock_contexts)
            print(f"✓ ask_llm function successful!")
            print(f"  Response: {answer[:100]}...")
        else:
            print("Skipping actual API call since no API key is provided")
            print("To test completely, set the GEMINI_API_KEY environment variable")
    except Exception as e:
        print(f"✗ Error in ask_llm function: {str(e)}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"✗ Could not import ask_llm: {str(e)}")