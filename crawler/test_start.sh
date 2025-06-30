#!/bin/bash

echo "=== Testing Requests + BeautifulSoup Deployment ==="

# Test basic Python functionality
echo "Testing Python..."
python --version

# Test if we can access the crawler directory
echo "Testing directory access..."
cd /opt/render/project/src/crawler
pwd
ls -la

# Test the requests approach
echo "Testing requests + BeautifulSoup..."
python test_requests.py

# Test OpenAI API
echo "Testing OpenAI API..."
python test_openai.py

# Test the environment test script
echo "Running environment test..."
python test_deployment.py

echo "=== Deployment Test Complete ===" 