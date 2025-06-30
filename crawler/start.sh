#!/bin/bash

echo "Starting RFP crawler with Selenium..."

# Navigate to the correct directory
cd /opt/render/project/src/crawler

# Check if files exist
echo "Checking required files..."
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found"
    exit 1
fi

if [ ! -f "crawl_with_selenium.py" ]; then
    echo "❌ crawl_with_selenium.py not found"
    exit 1
fi

# Run the main crawler
echo "Running main crawler..."
python main.py

echo "Crawler completed."
