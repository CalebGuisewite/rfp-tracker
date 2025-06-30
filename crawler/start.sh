#!/bin/bash

echo "Starting RFP crawler with requests + BeautifulSoup..."

# Run the crawler from the correct directory
cd /opt/render/project/src/crawler
python main.py

echo "Crawler completed."
