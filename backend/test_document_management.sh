#!/bin/bash
# Test script for DocChat document management

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BACKEND_URL="http://localhost:8000"

echo -e "${BLUE}DocChat Document Management Test Script${NC}"
echo "====================================="

# Check if backend is running
echo -e "\n${BLUE}Checking if backend is running...${NC}"
if curl -s "$BACKEND_URL/api/status" > /dev/null; then
    echo -e "${GREEN}Backend is running${NC}"
else
    echo -e "${RED}Backend is not running. Please start the backend server first.${NC}"
    exit 1
fi

# Function to test document listing
test_list_documents() {
    echo -e "\n${BLUE}Testing document listing...${NC}"
    response=$(curl -s "$BACKEND_URL/api/documents")
    echo "Documents in vector store:"
    echo "$response" | python -m json.tool
}

# Function to test document deletion
test_delete_document() {
    if [ -z "$1" ]; then
        echo -e "${RED}No document ID provided for deletion${NC}"
        return
    fi
    
    echo -e "\n${BLUE}Testing document deletion for ID: $1${NC}"
    response=$(curl -s -X DELETE "$BACKEND_URL/api/documents/$1")
    echo "Deletion response:"
    echo "$response" | python -m json.tool
}

# Function to test querying a specific document
test_query_document() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo -e "${RED}Document ID or query not provided${NC}"
        return
    fi
    
    echo -e "\n${BLUE}Testing query on document ID: $1${NC}"
    echo "Query: $2"
    
    response=$(curl -s -X POST "$BACKEND_URL/api/query" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$2\", \"doc_id\": \"$1\"}")
        
    echo "Query response:"
    echo "$response" | python -m json.tool
}

# Test document listing
test_list_documents

# If there are documents, ask if user wants to test deletion
echo -e "\n${BLUE}Do you want to delete a document? (y/n)${NC}"
read delete_choice

if [[ "$delete_choice" == "y" ]]; then
    echo "Enter the document ID to delete:"
    read doc_id
    test_delete_document "$doc_id"
    
    # Show updated list
    test_list_documents
fi

# Ask if user wants to test querying a specific document
echo -e "\n${BLUE}Do you want to query a specific document? (y/n)${NC}"
read query_choice

if [[ "$query_choice" == "y" ]]; then
    echo "Enter the document ID to query:"
    read doc_id
    echo "Enter your query:"
    read query_text
    test_query_document "$doc_id" "$query_text"
fi

echo -e "\n${GREEN}Test script completed${NC}"