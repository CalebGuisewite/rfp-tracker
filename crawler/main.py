import os
import json
import time
import subprocess
import sys
from datetime import datetime
from crawl_with_playwright import crawl_site_with_playwright

# School districts to crawl
SCHOOL_DISTRICTS = [
    "https://www.boone.kyschools.us",
    "https://www.carroll.kyschools.us"
]

def ensure_playwright_browsers():
    """Ensure Playwright browsers are installed"""
    print("🔧 Checking Playwright browser installation...")
    try:
        # Try to install browsers if not present
        result = subprocess.run(
            ["playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully")
        else:
            print(f"⚠️ Browser installation output: {result.stdout}")
            print(f"⚠️ Browser installation errors: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Could not install browsers: {e}")

def main():
    print("=== Starting RFP Crawler with Playwright ===")
    
    # Ensure browsers are installed
    ensure_playwright_browsers()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return
    
    print("✅ Anthropic API key found")
    
    # Check shared directory
    shared_dir = "/opt/render/project/src/shared"
    if not os.path.exists(shared_dir):
        print(f"❌ Shared directory not found: {shared_dir}")
        return
    
    print(f"✅ Shared directory: {shared_dir}")
    
    all_results = []
    
    # Crawl each school district
    for district_url in SCHOOL_DISTRICTS:
        print(f"\n🕷️ Starting Playwright crawl of: {district_url}")
        
        try:
            # Crawl the site with Playwright
            results = crawl_site_with_playwright(
                start_url=district_url,
                max_depth=2,
                max_pages=10
            )
            
            print(f"✅ Completed {district_url}. Found {len(results)} pages")
            all_results.extend(results)
            
        except Exception as e:
            print(f"❌ Error crawling {district_url}: {e}")
            continue
    
    # Save results
    output_file = os.path.join(shared_dir, "rfp_scan_results.json")
    
    # Prepare final results
    final_results = {
        "timestamp": datetime.now().isoformat(),
        "total_pages": len(all_results),
        "districts_crawled": len(SCHOOL_DISTRICTS),
        "results": all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n✅ Total crawl completed. Found {len(all_results)} total pages")
    print(f"✅ Results saved to: {output_file}")
    
    # Summary
    rfp_count = sum(1 for result in all_results 
                   if '"is_rfp": true' in result.get('claude_result', ''))
    
    print(f"\n📊 Summary: {rfp_count} potential RFPs found out of {len(all_results)} pages crawled")
    
    # Breakdown by district
    print("📋 Breakdown by District:")
    for district_url in SCHOOL_DISTRICTS:
        district_results = [r for r in all_results if district_url in r.get('url', '')]
        district_rfps = sum(1 for r in district_results 
                           if '"is_rfp": true' in r.get('claude_result', ''))
        print(f"  {district_url}: {district_rfps} RFPs out of {len(district_results)} pages")
    
    print("\nCrawler completed.")

if __name__ == "__main__":
    main()
