#!/bin/bash

echo "=== Testing Requests + BeautifulSoup + Claude Deployment ==="

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

# Test Anthropic API
echo "Testing Anthropic Claude API..."
python test_anthropic.py

# Test the environment test script
echo "Running environment test..."
python test_deployment.py

echo "=== Deployment Test Complete ===" 