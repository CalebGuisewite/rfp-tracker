import anthropic
import os
import time
import json
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def setup_driver():
    """Setup Chrome driver with appropriate options for Render"""
    chrome_options = Options()
    
    # Essential options for Render deployment
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Don't load images for speed
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Memory and performance options
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    
    # Additional options for Render environment
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    
    try:
        # Use webdriver-manager to handle driver installation
        print("🔧 Installing Chrome driver via webdriver-manager...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver created successfully")
        return driver
    except Exception as e:
        print(f"❌ Error with webdriver-manager: {e}")
        return None

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

def get_page_content_with_selenium(driver, url):
    """Get page content using Selenium to handle JavaScript"""
    try:
        print(f"  🔄 Loading page with Selenium: {url}")
        
        # Navigate to the page
        driver.get(url)
        
        # Wait for page to load (wait for body or specific element)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print(f"  ⚠️ Timeout waiting for page to load: {url}")
            return ""
        
        # Additional wait for dynamic content
        time.sleep(3)
        
        # Get the page source after JavaScript has executed
        page_source = driver.page_source
        
        # Extract text content
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get clean text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        print(f"  ✅ Extracted {len(text)} characters of content")
        return text
        
    except WebDriverException as e:
        print(f"  ❌ Selenium error for {url}: {e}")
        return ""
    except Exception as e:
        print(f"  ❌ Unexpected error for {url}: {e}")
        return ""

def find_links_with_selenium(driver, base_url):
    """Find all links on the page using Selenium"""
    try:
        # Find all anchor tags
        links = driver.find_elements(By.TAG_NAME, "a")
        
        found_links = []
        for link in links:
            try:
                href = link.get_attribute("href")
                if href:
                    # Only include links from the same domain
                    if urlparse(base_url).netloc in href:
                        found_links.append(href)
            except:
                continue
        
        return list(set(found_links))  # Remove duplicates
        
    except Exception as e:
        print(f"  ❌ Error finding links: {e}")
        return []

def crawl_site_with_selenium(start_url, max_depth=2, max_pages=20):
    """Crawl a website using Selenium to handle JavaScript"""
    visited = set()
    results = []
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        print("❌ Failed to setup Chrome driver")
        return results
    
    try:
        def crawl(url, depth):
            if url in visited or depth > max_depth or len(results) >= max_pages:
                return
            
            visited.add(url)
            print(f"[Depth {depth}] Crawling with Selenium: {url}")
            
            try:
                # Get page content using Selenium
                content = get_page_content_with_selenium(driver, url)
                if not content:
                    return
                
                # Use Claude to analyze the content
                claude_result = is_relevant_page(content, url)
                print(f"  ↪ Claude Result: {claude_result[:100]}...")
                
                results.append({
                    "url": url,
                    "depth": depth,
                    "content_length": len(content),
                    "claude_result": claude_result,
                    "method": "selenium"
                })
                
                # If we haven't reached max pages, continue crawling
                if len(results) < max_pages and depth < max_depth:
                    # Find links using Selenium
                    links = find_links_with_selenium(driver, url)
                    
                    # Crawl a subset of links
                    for link in links[:5]:  # Limit to 5 links per page
                        if link not in visited:
                            time.sleep(2)  # Be respectful with delays
                            crawl(link, depth + 1)
                            if len(results) >= max_pages:
                                break
                                
            except Exception as e:
                print(f"[ERROR] {url}: {e}")
        
        crawl(start_url, 0)
        
    finally:
        # Always close the driver
        try:
            driver.quit()
        except:
            pass
    
    return results 