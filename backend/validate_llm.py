import os
import sys

# Check if OPENAI_API_KEY is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("WARNING: OPENAI_API_KEY environment variable is not set.")
    print("Will skip API calls but still check imports.")
    api_key = "sk-dummy-key-for-import-testing-only"

# Try to import and check which OpenAI client we're using
print("=== OpenAI Client Check ===")

# First check if any openai package is installed at all
try:
    import pkg_resources
    openai_version = pkg_resources.get_distribution("openai").version
    print(f"OpenAI package found, version: {openai_version}")
    
    if openai_version.startswith("0."):
        print("⚠️ You have an older version of openai (pre-1.0)")
        print("  This version uses openai.ChatCompletion.create() API")
    else:
        print("✓ You have the new openai client (v1+)")
        print("  This version uses client.chat.completions.create() API")
except Exception as e:
    print(f"⚠️ Could not determine openai version: {e}")
    
# Try the new OpenAI client
try:
    from openai import OpenAI
    print("✓ Successfully imported OpenAI from openai")
    
    # Only try API call if we have a real API key
    if not api_key.startswith("sk-dummy"):
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10
            )
            print(f"✓ New client API call successful: {response.choices[0].message.content}")
        except Exception as e:
            print(f"✗ Error with new client API call: {str(e)}")
    
except ImportError as e:
    print(f"✗ Could not import OpenAI from openai: {e}")
    
# Try the old OpenAI client
try:
    import openai
    print("✓ Successfully imported openai module")
    
    # Only try API call if we have a real API key
    if not api_key.startswith("sk-dummy"):
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10
            )
            print(f"✓ Old client API call successful: {response.choices[0].message['content']}")
        except Exception as e:
            print(f"✗ Error with old client API call: {str(e)}")
            if "APIRemovedInV1" in str(e):
                print("  💡 This error is expected if you have openai>=1.0.0 installed")
                print("  Our LLM module should handle this with the fallback mechanism")
    
except ImportError as e:
    print(f"✗ Could not import openai module: {e}")

# Import our own LLM module to test
print("\n=== Testing our LLM module ===")
try:
    from core.llm import ask_llm
    
    # Test with mock data
    mock_contexts = [{"text": "This is a test document about AI."}, 
                     {"text": "OpenAI provides API for language models."}]
    
    try:
        answer = ask_llm("What is this document about?", mock_contexts)
        print(f"✓ ask_llm function successful!")
        print(f"  Response: {answer[:100]}...")
    except Exception as e:
        print(f"✗ Error in ask_llm function: {str(e)}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"✗ Could not import ask_llm: {str(e)}")