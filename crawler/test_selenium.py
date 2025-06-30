#!/usr/bin/env python3
"""
Test script to verify Selenium setup with Boone and Carroll County Schools
"""
import time
from crawl_with_selenium import setup_driver, get_page_content_with_selenium

def test_selenium_setup():
    """Test Selenium setup and basic functionality"""
    print("=== Testing Selenium Setup ===")
    
    # Test driver setup
    print("🔧 Setting up Chrome driver...")
    driver = setup_driver()
    
    if not driver:
        print("❌ Failed to setup Chrome driver")
        return False
    
    print("✅ Chrome driver setup successful")
    
    # Test URLs
    test_urls = [
        "https://www.boone.kyschools.us",
        "https://www.carroll.kyschools.us"
    ]
    
    results = {}
    
    for url in test_urls:
        print(f"\n--- Testing {url} ---")
        
        try:
            # Test page loading
            start_time = time.time()
            content = get_page_content_with_selenium(driver, url)
            load_time = time.time() - start_time
            
            if content:
                results[url] = {
                    "success": True,
                    "content_length": len(content),
                    "load_time": load_time,
                    "preview": content[:200] + "..." if len(content) > 200 else content
                }
                print(f"✅ Success: {len(content)} characters in {load_time:.2f}s")
                print(f"📄 Preview: {content[:100]}...")
            else:
                results[url] = {
                    "success": False,
                    "error": "No content extracted"
                }
                print(f"❌ Failed: No content extracted")
                
        except Exception as e:
            results[url] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ Error: {e}")
    
    # Cleanup
    try:
        driver.quit()
        print("\n✅ Driver cleaned up successfully")
    except:
        print("\n⚠️ Driver cleanup had issues")
    
    # Summary
    print(f"\n=== Test Summary ===")
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print(f"Successful: {successful}/{total}")
    
    for url, result in results.items():
        if result["success"]:
            print(f"✅ {url}: {result['content_length']} chars in {result['load_time']:.2f}s")
        else:
            print(f"❌ {url}: {result['error']}")
    
    return successful == total

def test_specific_pages():
    """Test specific pages that might contain RFPs"""
    print("\n=== Testing Specific RFP-Related Pages ===")
    
    # Common RFP-related paths
    rfp_paths = [
        "/rfp",
        "/procurement",
        "/bids",
        "/business",
        "/vendor",
        "/purchasing",
        "/contracts",
        "/insurance",
        "/benefits"
    ]
    
    base_urls = [
        "https://www.boone.kyschools.us",
        "https://www.carroll.kyschools.us"
    ]
    
    driver = setup_driver()
    if not driver:
        print("❌ Failed to setup driver for specific page testing")
        return
    
    try:
        for base_url in base_urls:
            print(f"\n--- Testing {base_url} ---")
            
            for path in rfp_paths:
                url = base_url + path
                print(f"  🔍 Testing: {path}")
                
                try:
                    content = get_page_content_with_selenium(driver, url)
                    
                    if content and len(content) > 100:
                        # Look for RFP indicators
                        rfp_indicators = ["rfp", "request for proposal", "bid", "tender", "procurement", "insurance", "benefits"]
                        found = [indicator for indicator in rfp_indicators if indicator in content.lower()]
                        
                        if found:
                            print(f"    ✅ Found RFP indicators: {found}")
                        else:
                            print(f"    ⚠️ Accessible but no RFP content")
                    else:
                        print(f"    ❌ No content or too short")
                        
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                
                time.sleep(1)  # Be respectful
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    # Test basic setup
    if test_selenium_setup():
        print("\n🎉 Selenium setup is working correctly!")
        
        # Test specific pages
        test_specific_pages()
    else:
        print("\n❌ Selenium setup has issues") 