from crawl_with_selenium import crawl_site_with_selenium
import json
import os
import sys

def main():
    """Main crawler function with error handling"""
    print("=== Starting RFP Crawler with Selenium ===")
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shared_dir = os.path.join(project_root, "shared")
    os.makedirs(shared_dir, exist_ok=True)
    
    # Check if Anthropic API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    print("✅ Anthropic API key found")
    print(f"✅ Shared directory: {shared_dir}")
    
    try:
        # Test with both Boone and Carroll County Schools (JavaScript-heavy sites)
        test_urls = [
            "https://www.boone.kyschools.us",
            "https://www.carroll.kyschools.us"
        ]
        
        all_results = []
        
        for test_url in test_urls:
            print(f"\n🕷️ Starting Selenium crawl of: {test_url}")
            
            results = crawl_site_with_selenium(test_url, max_depth=2, max_pages=10)
            
            print(f"✅ Completed {test_url}. Found {len(results)} pages")
            all_results.extend(results)
        
        print(f"\n✅ Total crawl completed. Found {len(all_results)} total pages")
        
        # Save results
        output_file = os.path.join(shared_dir, "rfp_scan_results.json")
        with open(output_file, "w") as f:
            json.dump(all_results, f, indent=2)
        
        print(f"✅ Results saved to: {output_file}")
        
        # Show summary
        rfp_count = 0
        for result in all_results:
            try:
                claude_data = json.loads(result['claude_result'])
                if claude_data.get("is_rfp", False):
                    rfp_count += 1
            except:
                pass
        
        print(f"📊 Summary: {rfp_count} potential RFPs found out of {len(all_results)} pages crawled")
        
        # Show breakdown by district
        print(f"\n📋 Breakdown by District:")
        for test_url in test_urls:
            district_results = [r for r in all_results if test_url in r['url']]
            district_rfps = 0
            for result in district_results:
                try:
                    claude_data = json.loads(result['claude_result'])
                    if claude_data.get("is_rfp", False):
                        district_rfps += 1
                except:
                    pass
            print(f"  {test_url}: {district_rfps} RFPs out of {len(district_results)} pages")
        
    except Exception as e:
        print(f"❌ ERROR during crawling: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
