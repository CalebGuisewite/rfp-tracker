import anthropic
import os
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

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

def extract_text_from_html(html_content):
    """Extract clean text from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text and clean it up
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def get_page_content(url, session):
    """Get page content with proper headers and error handling"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if it's an HTML page
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            return extract_text_from_html(response.text)
        else:
            # For non-HTML content, try to extract text
            return response.text[:4000]  # Limit content for GPT processing
            
    except requests.exceptions.RequestException as e:
        print(f"[REQUEST ERROR] {url}: {e}")
        return ""

def find_links(soup, base_url):
    """Extract all links from the page"""
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        
        # Only include links from the same domain
        if urlparse(base_url).netloc in full_url:
            links.append(full_url)
    
    return list(set(links))  # Remove duplicates

def crawl_site(start_url, max_depth=3, max_pages=50):
    """Crawl a website using requests and BeautifulSoup"""
    visited = set()
    results = []
    session = requests.Session()
    
    def crawl(url, depth):
        if url in visited or depth > max_depth or len(results) >= max_pages:
            return
        
        visited.add(url)
        print(f"[Depth {depth}] Crawling: {url}")
        
        try:
            # Get page content
            content = get_page_content(url, session)
            if not content:
                return
            
            # Use Claude to analyze the content
            claude_result = is_relevant_page(content, url)
            print(f"  ↪ Claude Result: {claude_result[:100]}...")
            
            results.append({
                "url": url,
                "depth": depth,
                "content_length": len(content),
                "claude_result": claude_result
            })
            
            # If we haven't reached max pages, continue crawling
            if len(results) < max_pages and depth < max_depth:
                # Get HTML for link extraction
                response = session.get(url, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')
                links = find_links(soup, url)
                
                # Crawl a subset of links to avoid overwhelming the site
                for link in links[:10]:  # Limit to 10 links per page
                    if link not in visited:
                        time.sleep(1)  # Be respectful with delays
                        crawl(link, depth + 1)
                        if len(results) >= max_pages:
                            break
                            
        except Exception as e:
            print(f"[ERROR] {url}: {e}")
    
    crawl(start_url, 0)
    session.close()
    return results
