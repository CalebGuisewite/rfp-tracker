from playwright.sync_api import sync_playwright
import openai
import os
import requests
import time
from urllib.parse import urljoin, urlparse

openai.api_key = os.getenv("OPENAI_API_KEY")

def is_relevant_page(content):
    prompt = f"""
You are an AI agent helping an insurance brokerage locate RFPs related only to:
- Employee benefits
- Group health, dental, vision, life, or disability insurance

Given this page content:
{content[:4000]}

Return JSON:
{{
  "is_rfp": true or false,
  "summary": "...",
  "category": "...",
  "submission_deadline": "...",
  "submission_location": "...",
  "contact_email": "..."
}}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return '{"is_rfp": false}'

def crawl_site(start_url, max_depth=4):
    visited = {}
    results = []

    with sync_playwright() as p:
        # Launch browser with Render-compatible settings
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )
        page = browser.new_page()

        def crawl(url, depth):
            if url in visited or depth > max_depth:
                return
            visited[url] = depth
            try:
                page.goto(url, timeout=15000)
                time.sleep(3)
                content = page.content()

                gpt_result = is_relevant_page(content)
                print(f"[Depth {depth}] {url}")
                print(f"  ↪ GPT: {gpt_result}")

                results.append({
                    "url": url,
                    "depth": depth,
                    "gpt_result": gpt_result
                })

                links = page.query_selector_all("a")
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue
                    full_url = urljoin(url, href)
                    domain = urlparse(start_url).netloc
                    if domain not in full_url:
                        continue
                    crawl(full_url, depth + 1)
            except Exception as e:
                print(f"[ERROR] {url}: {e}")

        crawl(start_url, 0)
        browser.close()
    return results
