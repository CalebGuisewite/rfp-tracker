#!/bin/bash

echo "=== Testing Deployment Environment ==="

# Test basic Python functionality
echo "Testing Python..."
python --version

# Test if we can access the crawler directory
echo "Testing directory access..."
cd /opt/render/project/src/crawler
pwd
ls -la

# Test the environment test script
echo "Running environment test..."
python test_deployment.py

# Test Playwright installation
echo "Testing Playwright..."
playwright --version

echo "=== Deployment Test Complete ===" 