#!/usr/bin/env python3
"""
School District RFP Crawler - MVP Version
Based on existing Playwright implementation
"""

import os
import json
import time
import logging
from datetime import datetime
from crawler.crawl_with_playwright import crawl_site_with_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# School districts to crawl - configurable via environment
DEFAULT_DISTRICTS = [
    "https://www.boone.kyschools.us",
    "https://www.carroll.kyschools.us"
]

def get_school_districts():
    """Get list of school districts from environment or default"""
    districts_env = os.getenv('SCHOOL_DISTRICTS', '')
    if districts_env:
        return [url.strip() for url in districts_env.split(',') if url.strip()]
    return DEFAULT_DISTRICTS

def save_results(all_results, shared_dir):
    """Save results in multiple formats for the dashboard"""
    timestamp = datetime.now().isoformat()
    
    # Analyze results for RFPs
    rfp_results = []
    total_pages = len(all_results)
    
    for result in all_results:
        try:
            claude_result = result.get('claude_result', '{}')
            if isinstance(claude_result, str):
                # Check if it's an RFP by looking for the is_rfp flag
                if '"is_rfp": true' in claude_result.lower():
                    # Try to parse the JSON for better data
                    try:
                        parsed = json.loads(claude_result)
                        rfp_data = {
                            'url': result['url'],
                            'title': result.get('title', 'Unknown Title'),
                            'summary': parsed.get('summary', 'No summary available'),
                            'category': parsed.get('category', 'Other'),
                            'confidence': parsed.get('confidence', 'Medium'),
                            'deadline': parsed.get('submission_deadline', ''),
                            'contact_email': parsed.get('contact_email', ''),
                            'contact_phone': parsed.get('contact_phone', ''),
                            'budget_range': parsed.get('budget_range', ''),
                            'submission_location': parsed.get('submission_location', ''),
                            'crawl_time': result.get('crawl_timestamp', timestamp),
                            'depth': result.get('depth', 0),
                            'method': result.get('method', 'playwright')
                        }
                        rfp_results.append(rfp_data)
                    except json.JSONDecodeError:
                        # Fallback for malformed JSON
                        rfp_data = {
                            'url': result['url'],
                            'title': result.get('title', 'Unknown Title'),
                            'summary': 'RFP detected but details could not be parsed',
                            'category': 'Other',
                            'confidence': 'Low',
                            'deadline': '',
                            'contact_email': '',
                            'contact_phone': '',
                            'budget_range': '',
                            'submission_location': '',
                            'crawl_time': timestamp,
                            'depth': result.get('depth', 0),
                            'method': result.get('method', 'playwright')
                        }
                        rfp_results.append(rfp_data)
        except Exception as e:
            logger.warning(f"Error processing result: {e}")
            continue
    
    # Create summary data
    categories = {}
    for rfp in rfp_results:
        category = rfp.get('category', 'Other')
        categories[category] = categories.get(category, 0) + 1
    
    # Main results file (detailed)
    detailed_results = {
        'metadata': {
            'crawl_timestamp': timestamp,
            'total_districts_crawled': len(get_school_districts()),
            'total_pages_crawled': total_pages,
            'total_rfps_found': len(rfp_results),
            'categories': categories,
            'version': 'mvp-1.0'
        },
        'rfp_summary': rfp_results,
        'raw_results': all_results
    }
    
    # Save detailed results
    results_file = os.path.join(shared_dir, 'rfp_scan_results.json')
    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    # Save simple summary for dashboard
    dashboard_summary = {
        'timestamp': timestamp,
        'total_rfps': len(rfp_results),
        'total_pages': total_pages,
        'categories': categories,
        'active_rfps': rfp_results
    }
    
    summary_file = os.path.join(shared_dir, 'dashboard_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(dashboard_summary, f, indent=2, default=str)
    
    logger.info(f"✅ Results saved to {results_file}")
    logger.info(f"✅ Dashboard summary saved to {summary_file}")
    
    return results_file, summary_file

def main():
    """Main crawler execution"""
    start_time = time.time()
    logger.info("=== Starting School District RFP Crawler (MVP) ===")
    
    # Environment checks
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        logger.error("❌ ANTHROPIC_API_KEY not found in environment variables")
        return 1
    logger.info("✅ Anthropic API key found")
    
    # Setup shared directory
    shared_dir = os.getenv('SHARED_DIR', '/opt/render/project/src/shared')
    if not os.path.exists(shared_dir):
        try:
            os.makedirs(shared_dir, exist_ok=True)
            logger.info(f"📁 Created shared directory: {shared_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to create shared directory: {e}")
            return 1
    else:
        logger.info(f"✅ Shared directory found: {shared_dir}")
    
    # Get districts to crawl
    school_districts = get_school_districts()
    logger.info(f"🎯 Will crawl {len(school_districts)} districts")
    
    all_results = []
    successful_crawls = 0
    failed_crawls = 0
    
    # Crawl each school district
    for i, district_url in enumerate(school_districts, 1):
        logger.info(f"\n🕷️ [{i}/{len(school_districts)}] Starting crawl: {district_url}")
        
        try:
            # Use your existing crawler with reasonable limits for MVP
            results = crawl_site_with_playwright(
                start_url=district_url,
                max_depth=int(os.getenv('CRAWLER_MAX_DEPTH', '2')),
                max_pages=int(os.getenv('CRAWLER_MAX_PAGES', '15'))
            )
            
            if results:
                logger.info(f"✅ Completed {district_url}: {len(results)} pages crawled")
                all_results.extend(results)
                successful_crawls += 1
                
                # Quick RFP count
                rfp_count = sum(1 for r in results 
                               if '"is_rfp": true' in r.get('claude_result', '').lower())
                if rfp_count > 0:
                    logger.info(f"  🎯 Found {rfp_count} potential RFPs!")
            else:
                logger.warning(f"⚠️ No results from {district_url}")
                failed_crawls += 1
                
        except Exception as e:
            logger.error(f"❌ Error crawling {district_url}: {e}")
            failed_crawls += 1
            continue
        
        # Brief pause between districts
        if i < len(school_districts):
            time.sleep(int(os.getenv('CRAWL_DELAY', '2')))
    
    # Save all results
    if all_results:
        try:
            save_results(all_results, shared_dir)
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
            return 1
    else:
        logger.warning("⚠️ No results to save")
        # Create empty results file so dashboard doesn't break
        empty_results = {
            'metadata': {
                'crawl_timestamp': datetime.now().isoformat(),
                'total_districts_crawled': len(school_districts),
                'total_pages_crawled': 0,
                'total_rfps_found': 0,
                'categories': {},
                'version': 'mvp-1.0'
            },
            'rfp_summary': [],
            'raw_results': []
        }
        
        results_file = os.path.join(shared_dir, 'rfp_scan_results.json')
        with open(results_file, 'w') as f:
            json.dump(empty_results, f, indent=2)
    
    # Final summary
    execution_time = round(time.time() - start_time, 2)
    total_rfps = sum(1 for r in all_results 
                    if '"is_rfp": true' in r.get('claude_result', '').lower())
    
    logger.info("\n" + "="*50)
    logger.info("📊 CRAWL SUMMARY")
    logger.info("="*50)
    logger.info(f"⏱️  Execution time: {execution_time} seconds")
    logger.info(f"🎯 Districts attempted: {len(school_districts)}")
    logger.info(f"✅ Successful crawls: {successful_crawls}")
    logger.info(f"❌ Failed crawls: {failed_crawls}")
    logger.info(f"📄 Total pages crawled: {len(all_results)}")
    logger.info(f"🏆 RFPs found: {total_rfps}")
    
    logger.info("\n📋 Breakdown by District:")
    for district_url in school_districts:
        district_results = [r for r in all_results if district_url in r.get('url', '')]
        if district_results:
            district_rfps = sum(1 for r in district_results 
                               if '"is_rfp": true' in r.get('claude_result', '').lower())
            logger.info(f"   {district_url}: {district_rfps} RFPs / {len(district_results)} pages")
        else:
            logger.info(f"   {district_url}: No results")
    
    logger.info("\n🎉 Crawler completed!")
    return 0

if __name__ == "__main__":
    exit(main())