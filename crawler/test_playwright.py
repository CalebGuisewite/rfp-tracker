#!/usr/bin/env python3
"""
Simple test script to verify Playwright works on Render
"""

from playwright.sync_api import sync_playwright
import time

def test_playwright():
    print("🧪 Testing Playwright on Render...")
    
    with sync_playwright() as p:
        try:
            # Launch browser
            print("  🔧 Launching Chromium...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            
            # Create page
            page = browser.new_page()
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Test with a simple page
            print("  🌐 Testing with a simple page...")
            page.goto("https://httpbin.org/html", wait_until="networkidle")
            
            # Get title
            title = page.title()
            print(f"  ✅ Page title: {title}")
            
            # Get content
            content = page.content()
            print(f"  ✅ Content length: {len(content)} characters")
            
            # Test JavaScript execution
            print("  🔄 Testing JavaScript execution...")
            result = page.evaluate("() => document.title")
            print(f"  ✅ JavaScript result: {result}")
            
            browser.close()
            print("✅ Playwright test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Playwright test failed: {e}")
            return False

if __name__ == "__main__":
    test_playwright() 