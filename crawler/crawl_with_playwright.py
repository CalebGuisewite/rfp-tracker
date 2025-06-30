import anthropic
import os
import time
import json
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def is_relevant_page(content, url):
    """Use Claude to determine if a page contains relevant RFP information"""
    prompt = f"""
You are an AI agent helping an insurance brokerage locate RFPs related only to:
- Employee benefits
- Group health, dental, vision, life, or disability insurance
- Benefits administration
- Insurance procurement

Given this page content from {url}:
{content[:4000]}

Return JSON:
{{
  "is_rfp": true or false,
  "summary": "Brief summary of the RFP or page content",
  "category": "Employee Benefits" or "Other",
  "submission_deadline": "Deadline date if found, otherwise empty string",
  "submission_location": "Where to submit if found, otherwise empty string",
  "contact_email": "Contact email if found, otherwise empty string",
  "budget_range": "Budget information if found, otherwise empty string",
  "confidence": "High/Medium/Low based on how certain you are this is an insurance RFP"
}}
"""
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"[CLAUDE ERROR] {e}")
        return '{"is_rfp": false, "summary": "Error processing with Claude", "confidence": "Low"}'

def crawl_site_with_playwright(start_url, max_depth=2, max_pages=20):
    """Crawl a website using Playwright to handle JavaScript"""
    visited = set()
    results = []
    
    with sync_playwright() as p:
        # Launch browser with appropriate options for Render
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        
        page = browser.new_page()
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        try:
            def crawl(url, depth):
                if url in visited or depth > max_depth or len(results) >= max_pages:
                    return
                
                visited.add(url)
                print(f"[Depth {depth}] Crawling with Playwright: {url}")
                
                try:
                    # Navigate and wait for content
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(3000)
                    
                    # Get content after JavaScript execution
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Remove scripts and get text
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    text = soup.get_text()
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    if not text:
                        return
                    
                    print(f"  ✅ Extracted {len(text)} characters")
                    
                    # Use Claude to analyze
                    claude_result = is_relevant_page(text, url)
                    print(f"  ↪ Claude Result: {claude_result[:100]}...")
                    
                    results.append({
                        "url": url,
                        "depth": depth,
                        "content_length": len(text),
                        "claude_result": claude_result,
                        "method": "playwright"
                    })
                    
                    # Continue crawling if needed
                    if len(results) < max_pages and depth < max_depth:
                        links = page.query_selector_all("a")
                        found_links = []
                        
                        for link in links:
                            try:
                                href = link.get_attribute("href")
                                if href and urlparse(start_url).netloc in href:
                                    found_links.append(href)
                            except:
                                continue
                        
                        for link in list(set(found_links))[:5]:
                            if link not in visited:
                                time.sleep(2)
                                crawl(link, depth + 1)
                                if len(results) >= max_pages:
                                    break
                                    
                except Exception as e:
                    print(f"[ERROR] {url}: {e}")
            
            crawl(start_url, 0)
            
        finally:
            browser.close()
    
    return results 