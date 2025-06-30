#!/usr/bin/env python3
"""
Playwright-based crawler for school district websites
Enhanced version of your existing code
"""

import anthropic
import os
import time
import json
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def is_relevant_page(content, url):
    """Use Claude to determine if a page contains relevant RFP information"""
    prompt = f"""
You are analyzing a school district website page to find RFP (Request for Proposal) opportunities.

Look for RFPs related to:
- Technology services and equipment
- Construction and facilities
- Transportation services
- Food services and catering
- Educational services and curriculum
- Insurance and employee benefits
- Professional services (legal, accounting, consulting)
- Maintenance and facility services
- Security services
- Any other procurement opportunities

Given this page content from {url}:
{content[:4000]}

Return JSON only (no other text):
{{
  "is_rfp": true or false,
  "summary": "Brief summary of the RFP or page content",
  "category": "Technology|Construction|Transportation|Food Services|Professional Services|Insurance|Other",
  "submission_deadline": "Deadline date if found, otherwise empty string",
  "submission_location": "Where to submit if found, otherwise empty string", 
  "contact_email": "Contact email if found, otherwise empty string",
  "contact_phone": "Contact phone if found, otherwise empty string",
  "budget_range": "Budget information if found, otherwise empty string",
  "confidence": "High|Medium|Low based on how certain you are this is an RFP"
}}
"""
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.content[0].text.strip()
        
        # Ensure we return valid JSON
        try:
            json.loads(result)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from response
            start = result.find('{')
            end = result.rfind('}') + 1
            if start != -1 and end != 0:
                json_part = result[start:end]
                json.loads(json_part)  # Validate
                return json_part
            else:
                raise Exception("No valid JSON found")
                
    except Exception as e:
        logger.error(f"[CLAUDE ERROR] {e}")
        return json.dumps({
            "is_rfp": False, 
            "summary": f"Error processing with Claude: {str(e)}", 
            "category": "Other",
            "submission_deadline": "",
            "submission_location": "",
            "contact_email": "",
            "contact_phone": "",
            "budget_range": "",
            "confidence": "Low"
        })

def get_school_priority_urls(base_url):
    """Get priority URLs for school districts"""
    priority_paths = [
        '/administration',
        '/business',
        '/finance', 
        '/purchasing',
        '/procurement',
        '/bids',
        '/rfp',
        '/rfps',
        '/vendors',
        '/contracts',
        '/board',
        '/departments/business',
        '/departments/finance',
        '/about/business-office'
    ]
    
    return [urljoin(base_url, path) for path in priority_paths]

def crawl_site_with_playwright(start_url, max_depth=2, max_pages=20):
    """Enhanced Playwright crawler for school districts"""
    visited = set()
    results = []
    
    with sync_playwright() as p:
        # Launch browser with Render-optimized options
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--memory-pressure-off'
            ]
        )
        
        page = browser.new_page()
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Set longer timeouts for school sites
        page.set_default_timeout(45000)
        page.set_default_navigation_timeout(60000)
        
        try:
            def crawl(url, depth):
                if (url in visited or 
                    depth > max_depth or 
                    len(results) >= max_pages or
                    not url.startswith('http')):
                    return
                
                visited.add(url)
                logger.info(f"[Depth {depth}] Crawling: {url}")
                
                try:
                    # Navigate and wait for content
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    page.wait_for_timeout(2000)  # Wait for dynamic content
                    
                    # Get page title and content
                    title = page.title()
                    content = page.content()
                    
                    # Clean content with BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Remove scripts, styles, and navigation
                    for script in soup(["script", "style", "nav", "header", "footer"]):
                        script.decompose()
                    
                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    if len(clean_text) < 50:
                        logger.info(f"  ⚠️ Skipping {url} - insufficient content")
                        return
                    
                    logger.info(f"  ✅ Extracted {len(clean_text)} characters from: {title}")
                    
                    # Use Claude to analyze
                    claude_result = is_relevant_page(clean_text, url)
                    logger.info(f"  ↪ Claude analysis complete")
                    
                    # Check if RFP found
                    try:
                        parsed_result = json.loads(claude_result)
                        if parsed_result.get('is_rfp', False):
                            logger.info(f"  🎯 RFP FOUND: {parsed_result.get('summary', '')[:100]}")
                    except:
                        pass
                    
                    result = {
                        "url": url,
                        "title": title,
                        "depth": depth,
                        "content_length": len(clean_text),
                        "claude_result": claude_result,
                        "crawl_timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
                        "method": "playwright"
                    }
                    
                    results.append(result)
                    
                    # Continue crawling if needed
                    if len(results) < max_pages and depth < max_depth:
                        # First try priority URLs (only on depth 0)
                        if depth == 0:
                            priority_urls = get_school_priority_urls(start_url)
                            for priority_url in priority_urls:
                                if priority_url not in visited and len(results) < max_pages:
                                    time.sleep(1)
                                    crawl(priority_url, depth + 1)
                        
                        # Then find additional links
                        try:
                            links = page.query_selector_all("a[href]")
                            found_links = []
                            
                            for link in links[:20]:  # Limit links to check
                                try:
                                    href = link.get_attribute("href")
                                    if href and start_url in href:
                                        found_links.append(href)
                                except:
                                    continue
                            
                            # Crawl unique links
                            for link in list(set(found_links))[:5]:
                                if link not in visited and len(results) < max_pages:
                                    time.sleep(1)
                                    crawl(link, depth + 1)
                                    if len(results) >= max_pages:
                                        break
                        except Exception as e:
                            logger.warning(f"Error finding links: {e}")
                            
                except Exception as e:
                    logger.error(f"  ❌ Error crawling {url}: {e}")
            
            # Start crawling from the main URL
            crawl(start_url, 0)
            
        finally:
            browser.close()
    
    logger.info(f"✅ Crawl completed. Found {len(results)} pages total")
    return results