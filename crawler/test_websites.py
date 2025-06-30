#!/usr/bin/env python3
"""
Test script to check school district website accessibility
"""
import requests
from bs4 import BeautifulSoup
import time

def test_website_accessibility(url):
    """Test if a website is accessible without JavaScript"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    try:
        print(f"Testing: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            print(f"  ❌ Not HTML content: {content_type}")
            return False
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get title
        title = soup.find('title')
        title_text = title.get_text() if title else "No title"
        print(f"  📄 Title: {title_text}")
        
        # Check for JavaScript error indicators
        text_content = soup.get_text().lower()
        js_errors = [
            "javascript is disabled",
            "javascript is required", 
            "enable javascript",
            "please enable javascript"
        ]
        
        has_js_error = any(error in text_content for error in js_errors)
        
        if has_js_error:
            print(f"  ⚠️ JavaScript error detected")
            return False
        else:
            print(f"  ✅ Accessible without JavaScript")
            
            # Look for potential RFP indicators
            rfp_indicators = [
                "rfp", "request for proposal", "bid", "tender", "procurement",
                "insurance", "benefits", "health", "dental", "vision"
            ]
            
            found_indicators = []
            for indicator in rfp_indicators:
                if indicator in text_content:
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"  🔍 Found potential RFP indicators: {found_indicators}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Test multiple school district websites"""
    print("=== Testing School District Website Accessibility ===")
    
    # List of Kentucky school districts to test
    test_urls = [
        "https://www.boone.kyschools.us",
        "https://www.carroll.kyschools.us", 
        "https://www.kenton.kyschools.us",
        "https://www.campbell.kyschools.us",
        "https://www.grant.kyschools.us"
    ]
    
    accessible_sites = []
    
    for url in test_urls:
        print(f"\n--- Testing {url} ---")
        if test_website_accessibility(url):
            accessible_sites.append(url)
        time.sleep(2)  # Be respectful
    
    print(f"\n=== Results ===")
    print(f"Accessible sites: {len(accessible_sites)}/{len(test_urls)}")
    for site in accessible_sites:
        print(f"✅ {site}")

if __name__ == "__main__":
    main() 