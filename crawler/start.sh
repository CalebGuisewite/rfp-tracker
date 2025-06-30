#!/bin/bash

echo "Starting RFP crawler with Playwright..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run from the crawler directory."
    exit 1
fi

echo "Checking required files..."
if [ ! -f "crawl_with_playwright.py" ]; then
    echo "❌ Error: crawl_with_playwright.py not found"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

echo "Installing Playwright browsers..."
playwright install chromium

echo "Running main crawler..."
python main.py

echo "Crawler completed."
