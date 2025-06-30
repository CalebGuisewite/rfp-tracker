#!/bin/bash
set -e

echo "Starting RFP crawler in Docker environment..."
cd /app

# Set environment variables for headless operation
export DISPLAY=:99
export PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

echo "Running crawler..."
python crawler/main.py

echo "Crawler completed successfully!"
