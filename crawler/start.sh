#!/bin/bash

# Install Playwright browsers with system dependencies
playwright install --with-deps

# Run the crawler from the correct directory
cd /opt/render/project/src/crawler
python main.py
