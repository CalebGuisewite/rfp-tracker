#!/usr/bin/env python3
"""
Test script to check specific RFP-related pages across school districts
"""
import requests
from bs4 import BeautifulSoup
import time
import json

def test_specific_page(base_url, path):
    """Test a specific page on a school district website"""
    url = base_url + path
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Check if it's HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = soup.get_text().lower()
                
                # Check for JavaScript errors
                js_errors = ["javascript is disabled", "javascript is required", "enable javascript"]
                has_js_error = any(error in text_content for error in js_errors)
                
                if not has_js_error:
                    # Look for RFP-related content
                    rfp_indicators = ["rfp", "request for proposal", "bid", "tender", "procurement", "insurance", "benefits"]
                    found_indicators = [indicator for indicator in rfp_indicators if indicator in text_content]
                    
                    return {
                        "url": url,
                        "accessible": True,
                        "content_length": len(text_content),
                        "rfp_indicators": found_indicators,
                        "title": soup.find('title').get_text() if soup.find('title') else "No title"
                    }
                else:
                    return {"url": url, "accessible": False, "reason": "JavaScript required"}
            else:
                return {"url": url, "accessible": False, "reason": f"Not HTML: {content_type}"}
        else:
            return {"url": url, "accessible": False, "reason": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"url": url, "accessible": False, "reason": str(e)}

def main():
    """Test multiple school districts and specific paths"""
    print("=== Testing Specific RFP Pages Across School Districts ===")
    
    # Kentucky school districts
    school_districts = [
        "https://www.boone.kyschools.us",
        "https://www.carroll.kyschools.us",
        "https://www.kenton.kyschools.us", 
        "https://www.campbell.kyschools.us",
        "https://www.grant.kyschools.us",
        "https://www.pendleton.kyschools.us",
        "https://www.bracken.kyschools.us",
        "https://www.gallatin.kyschools.us",
        "https://www.owen.kyschools.us",
        "https://www.henry.kyschools.us"
    ]
    
    # Common RFP-related paths
    paths_to_test = [
        "/rfp",
        "/procurement",
        "/bids", 
        "/tenders",
        "/business",
        "/vendor",
        "/supplier",
        "/purchasing",
        "/contracts",
        "/insurance",
        "/benefits",
        "/employment",
        "/jobs",
        "/opportunities",
        "/resources",
        "/departments/business",
        "/departments/finance",
        "/departments/human-resources"
    ]
    
    results = []
    
    for district in school_districts:
        print(f"\n--- Testing {district} ---")
        district_results = []
        
        for path in paths_to_test:
            result = test_specific_page(district, path)
            district_results.append(result)
            
            if result["accessible"]:
                print(f"  ✅ {path}: {len(result['rfp_indicators'])} RFP indicators found")
            else:
                print(f"  ❌ {path}: {result['reason']}")
            
            time.sleep(1)  # Be respectful
        
        # Find the best accessible page for this district
        accessible_pages = [r for r in district_results if r["accessible"]]
        if accessible_pages:
            best_page = max(accessible_pages, key=lambda x: len(x.get("rfp_indicators", [])))
            results.append({
                "district": district,
                "best_page": best_page,
                "total_accessible": len(accessible_pages)
            })
            print(f"  🎯 Best page: {best_page['url']} ({len(best_page['rfp_indicators'])} indicators)")
        else:
            print(f"  ⚠️ No accessible pages found")
    
    # Save results
    with open("website_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== Summary ===")
    accessible_districts = [r for r in results if r["total_accessible"] > 0]
    print(f"Districts with accessible pages: {len(accessible_districts)}/{len(school_districts)}")
    
    for result in accessible_districts:
        print(f"✅ {result['district']}: {result['best_page']['url']}")

if __name__ == "__main__":
    main() 