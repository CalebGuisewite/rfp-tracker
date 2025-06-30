from crawl_site_enhanced import crawl_site
import json
import os
import sys

def main():
    """Main crawler function with error handling"""
    print("=== Starting RFP Crawler ===")
    
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
        # Crawl the test school district
        test_url = "https://www.carroll.kyschools.us"
        print(f"🕷️ Starting crawl of: {test_url}")
        
        results = crawl_site(test_url, max_depth=3, max_pages=30)
        
        print(f"✅ Crawl completed. Found {len(results)} pages")
        
        # Save results
        output_file = os.path.join(shared_dir, "rfp_scan_results.json")
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Results saved to: {output_file}")
        
        # Show summary
        rfp_count = 0
        for result in results:
            try:
                claude_data = json.loads(result['claude_result'])
                if claude_data.get("is_rfp", False):
                    rfp_count += 1
            except:
                pass
        
        print(f"📊 Summary: {rfp_count} potential RFPs found out of {len(results)} pages crawled")
        
    except Exception as e:
        print(f"❌ ERROR during crawling: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
