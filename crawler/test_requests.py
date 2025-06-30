#!/usr/bin/env python3
"""
Test script to verify requests + BeautifulSoup approach
"""
import requests
from bs4 import BeautifulSoup
import json

def test_requests_approach():
    """Test the requests + BeautifulSoup approach"""
    print("=== Testing Requests + BeautifulSoup ===")
    
    # Test URL
    test_url = "https://www.carroll.kyschools.us"
    
    try:
        # Test basic request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        print(f"Testing request to: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type', 'unknown')}")
        print(f"Content length: {len(response.text)} characters")
        
        # Test BeautifulSoup parsing
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        print(f"Page title: {title.get_text() if title else 'No title found'}")
        
        # Test link extraction
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} links on the page")
        
        # Show first few links
        for i, link in enumerate(links[:5]):
            href = link.get('href', '')
            text = link.get_text().strip()[:50]
            print(f"  Link {i+1}: {text} -> {href}")
        
        print("=== Test completed successfully ===")
        return True
        
    except Exception as e:
        print(f"=== Test failed: {e} ===")
        return False

if __name__ == "__main__":
    test_requests_approach() 