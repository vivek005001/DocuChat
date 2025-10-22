#!/usr/bin/env python3
"""
Test the LLM module with a simple query.
"""

import os
import sys

# Try to add logging
import logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Try to import the LLM module
try:
    from core.llm import ask_llm
    print("✓ Successfully imported ask_llm function")
except ImportError as e:
    print(f"✗ Failed to import ask_llm: {e}")
    sys.exit(1)

# Create some mock documents
mock_docs = [
    {"text": "The academic calendar starts in September and ends in June."},
    {"text": "Final exams are scheduled during the last two weeks of each semester."},
    {"text": "Spring break occurs in the middle of the second semester, usually in March."}
]

# Test a simple query
test_query = "When do final exams happen?"

print(f"\nTesting query: '{test_query}'")
print("Mock documents:")
for i, doc in enumerate(mock_docs):
    print(f"  Doc {i+1}: {doc['text']}")

try:
    # Call the LLM function
    print("\nCalling ask_llm function...")
    response = ask_llm(test_query, mock_docs)
    
    print("\n=== Response ===")
    print(response)
    print("===============")
    
    print("\n✓ Test successful!")
except Exception as e:
    print(f"\n✗ Error calling ask_llm: {e}")
    print("\nDebug information:")
    import traceback
    traceback.print_exc()