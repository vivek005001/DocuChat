import os
import logging
from importlib.util import find_spec

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)
has_genai = find_spec("google.generativeai") is not None

if has_genai:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
else:
    pass

def ask_llm(query, contexts):
    context_text = "\n\n".join(
        [f"Doc {i+1}: {c['text']}" for i, c in enumerate(contexts)]
    )
    
    prompt = f"""Answer based on these documents:

{context_text}

Question: {query}

Answer with citations to the documents by referencing Doc numbers."""
    
    if has_genai:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return "Error: GEMINI_API_KEY environment variable is not set."
            
            model = genai.GenerativeModel("models/gemini-flash-latest")
            response = model.generate_content(prompt)
            
            if hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Sorry, I couldn't process your request: {str(e)}"
    
    else:
        mock_response = f"This is a mock response since Gemini API is not available.\n\n"
        mock_response += f"Your question was: {query}\n\n"
        mock_response += "Based on the documents I found:\n\n"
        
        for i, context in enumerate(contexts):
            text = context.get('text', 'No text available')
            mock_response += f"Doc {i+1}: {text[:100]}{'...' if len(text) > 100 else ''}\n\n"
            
        return mock_response
