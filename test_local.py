#!/usr/bin/env python3
"""
Test script to verify the RFP crawler works locally
"""

import os
import sys
import json

# Add crawler directory to path
sys.path.append('crawler')

def test_crawler():
    print("Testing RFP crawler...")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        # Import and test the crawler
        from crawl_site_enhanced import crawl_site
        
        print("✅ Crawler module imported successfully")
        
        # Test with a small crawl (just the homepage)
        print("Testing crawl with limited depth...")
        results = crawl_site("https://www.carroll.kyschools.us", max_depth=1)
        
        print(f"✅ Crawl completed! Found {len(results)} pages")
        
        # Save results for testing
        os.makedirs("shared", exist_ok=True)
        with open("shared/test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print("✅ Test results saved to shared/test_results.json")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_crawler()
    if success:
        print("\n🎉 Local test passed! Ready for Render deployment.")
    else:
        print("\n❌ Local test failed. Please fix issues before deploying.")
        sys.exit(1) 