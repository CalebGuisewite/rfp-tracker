#!/usr/bin/env python3
"""
Find school districts with accessible websites (no JavaScript required)
"""
import requests
from bs4 import BeautifulSoup
import time
import json

def test_district_accessibility(url):
    """Test if a school district website is accessible without JavaScript"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Check for JavaScript requirements
            js_indicators = [
                "javascript is disabled", "javascript is required", "enable javascript",
                "please enable javascript", "javascript must be enabled", "noscript"
            ]
            
            requires_js = any(indicator in text_content for indicator in js_indicators)
            
            if not requires_js:
                # Look for RFP-related content
                rfp_indicators = ["rfp", "request for proposal", "bid", "tender", "procurement"]
                found_indicators = [indicator for indicator in rfp_indicators if indicator in text_content]
                
                title = soup.find('title')
                title_text = title.get_text() if title else "No title"
                
                return {
                    "url": url,
                    "accessible": True,
                    "title": title_text,
                    "content_length": len(text_content),
                    "rfp_indicators": found_indicators,
                    "has_content": len(text_content) > 1000  # Meaningful content
                }
            else:
                return {"url": url, "accessible": False, "reason": "JavaScript required"}
        else:
            return {"url": url, "accessible": False, "reason": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"url": url, "accessible": False, "reason": str(e)}

def main():
    """Test a comprehensive list of Kentucky school districts"""
    print("=== Finding Accessible School District Websites ===")
    
    # Comprehensive list of Kentucky school districts
    kentucky_districts = [
        # Northern Kentucky
        "https://www.boone.kyschools.us",
        "https://www.carroll.kyschools.us", 
        "https://www.kenton.kyschools.us",
        "https://www.campbell.kyschools.us",
        "https://www.grant.kyschools.us",
        "https://www.pendleton.kyschools.us",
        "https://www.bracken.kyschools.us",
        "https://www.gallatin.kyschools.us",
        "https://www.owen.kyschools.us",
        "https://www.henry.kyschools.us",
        "https://www.oldham.kyschools.us",
        "https://www.shelby.kyschools.us",
        "https://www.spencer.kyschools.us",
        "https://www.trimble.kyschools.us",
        
        # Central Kentucky
        "https://www.fayette.kyschools.us",
        "https://www.jessamine.kyschools.us",
        "https://www.woodford.kyschools.us",
        "https://www.scott.kyschools.us",
        "https://www.harrison.kyschools.us",
        "https://www.bourbon.kyschools.us",
        "https://www.nicholas.kyschools.us",
        "https://www.montgomery.kyschools.us",
        "https://www.clark.kyschools.us",
        "https://www.madison.kyschools.us",
        "https://www.estill.kyschools.us",
        "https://www.powell.kyschools.us",
        "https://www.lee.kyschools.us",
        "https://www.breathitt.kyschools.us",
        "https://www.wolfe.kyschools.us",
        "https://www.menifee.kyschools.us",
        "https://www.morgan.kyschools.us",
        "https://www.rowan.kyschools.us",
        "https://www.bath.kyschools.us",
        "https://www.fleming.kyschools.us",
        "https://www.lewis.kyschools.us",
        "https://www.carter.kyschools.us",
        "https://www.greenup.kyschools.us",
        "https://www.boyd.kyschools.us",
        "https://www.lawrence.kyschools.us",
        "https://www.johnson.kyschools.us",
        "https://www.martin.kyschools.us",
        "https://www.floyd.kyschools.us",
        "https://www.pike.kyschools.us",
        "https://www.knott.kyschools.us",
        "https://www.leslie.kyschools.us",
        "https://www.perry.kyschools.us",
        "https://www.harlan.kyschools.us",
        "https://www.bell.kyschools.us",
        "https://www.whitley.kyschools.us",
        "https://www.knox.kyschools.us",
        "https://www.clay.kyschools.us",
        "https://www.laurel.kyschools.us",
        "https://www.jackson.kyschools.us",
        "https://www.rockcastle.kyschools.us",
        "https://www.garrard.kyschools.us",
        "https://www.lincoln.kyschools.us",
        "https://www.boyle.kyschools.us",
        "https://www.mercer.kyschools.us",
        "https://www.anderson.kyschools.us",
        "https://www.washington.kyschools.us",
        "https://www.marion.kyschools.us",
        "https://www.taylor.kyschools.us",
        "https://www.casey.kyschools.us",
        "https://www.adair.kyschools.us",
        "https://www.russell.kyschools.us",
        "https://www.cumberland.kyschools.us",
        "https://www.clinton.kyschools.us",
        "https://www.mccreary.kyschools.us",
        "https://www.pulaski.kyschools.us",
        "https://www.wayne.kyschools.us",
        "https://www.mccreary.kyschools.us",
        "https://www.somerset.kyschools.us",
        "https://www.wayne.kyschools.us",
        "https://www.russell.kyschools.us",
        "https://www.green.kyschools.us",
        "https://www.hart.kyschools.us",
        "https://www.hardin.kyschools.us",
        "https://www.meade.kyschools.us",
        "https://www.breckinridge.kyschools.us",
        "https://www.grayson.kyschools.us",
        "https://www.butler.kyschools.us",
        "https://www.edmonson.kyschools.us",
        "https://www.warren.kyschools.us",
        "https://www.simpson.kyschools.us",
        "https://www.allen.kyschools.us",
        "https://www.barren.kyschools.us",
        "https://www.metcalfe.kyschools.us",
        "https://www.monroe.kyschools.us",
        "https://www.cumberland.kyschools.us",
        "https://www.clinton.kyschools.us",
        "https://www.mccreary.kyschools.us",
        "https://www.pulaski.kyschools.us",
        "https://www.wayne.kyschools.us",
        "https://www.russell.kyschools.us",
        "https://www.green.kyschools.us",
        "https://www.hart.kyschools.us",
        "https://www.hardin.kyschools.us",
        "https://www.meade.kyschools.us",
        "https://www.breckinridge.kyschools.us",
        "https://www.grayson.kyschools.us",
        "https://www.butler.kyschools.us",
        "https://www.edmonson.kyschools.us",
        "https://www.warren.kyschools.us",
        "https://www.simpson.kyschools.us",
        "https://www.allen.kyschools.us",
        "https://www.barren.kyschools.us",
        "https://www.metcalfe.kyschools.us",
        "https://www.monroe.kyschools.us"
    ]
    
    accessible_districts = []
    inaccessible_districts = []
    
    for i, district in enumerate(kentucky_districts, 1):
        print(f"[{i}/{len(kentucky_districts)}] Testing: {district}")
        
        result = test_district_accessibility(district)
        
        if result["accessible"] and result.get("has_content", False):
            accessible_districts.append(result)
            print(f"  ✅ ACCESSIBLE: {result['title']} ({len(result['rfp_indicators'])} RFP indicators)")
        else:
            inaccessible_districts.append(result)
            print(f"  ❌ Inaccessible: {result.get('reason', 'Unknown error')}")
        
        time.sleep(1)  # Be respectful
    
    # Save results
    results = {
        "accessible": accessible_districts,
        "inaccessible": inaccessible_districts,
        "summary": {
            "total_tested": len(kentucky_districts),
            "accessible_count": len(accessible_districts),
            "inaccessible_count": len(inaccessible_districts),
            "success_rate": f"{len(accessible_districts)/len(kentucky_districts)*100:.1f}%"
        }
    }
    
    with open("accessible_districts.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n=== RESULTS ===")
    print(f"Total districts tested: {len(kentucky_districts)}")
    print(f"Accessible: {len(accessible_districts)} ({results['summary']['success_rate']})")
    print(f"Inaccessible: {len(inaccessible_districts)}")
    
    if accessible_districts:
        print(f"\n=== ACCESSIBLE DISTRICTS ===")
        for district in accessible_districts:
            print(f"✅ {district['url']}")
            print(f"   Title: {district['title']}")
            print(f"   RFP Indicators: {district['rfp_indicators']}")
            print()

if __name__ == "__main__":
    main() 