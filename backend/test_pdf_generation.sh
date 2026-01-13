#!/bin/bash

# Test PDF generation via chat endpoint
echo "Testing PDF generation with chat endpoint..."
curl -X 'POST' \
  'http://127.0.0.1:8000/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "tell me about python programming language",
  "generate_pdf": true
}'

echo -e "\n\n---\n"

# Test direct PDF generation
echo "Testing direct PDF generation endpoint..."
curl -X 'POST' \
  'http://127.0.0.1:8000/generate-pdf' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "content": "This is a test document. Python is a high-level programming language known for its simplicity and readability.",
  "filename": "test_document.pdf"
}'
