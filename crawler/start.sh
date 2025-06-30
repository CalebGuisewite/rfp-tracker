#!/bin/bash

echo "Starting RFP crawler with Selenium..."

# Test Selenium setup first
echo "Testing Selenium setup..."
cd /opt/render/project/src/crawler
python test_selenium.py

# Run the main crawler
echo "Running main crawler..."
python main.py

echo "Crawler completed."
