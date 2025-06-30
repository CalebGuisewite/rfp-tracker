#!/usr/bin/env python3
"""
Alternative data sources for RFP discovery
"""
import requests
import json
import time
from bs4 import BeautifulSoup

def check_state_portals():
    """Check state-level procurement portals"""
    print("=== Checking State Procurement Portals ===")
    
    state_portals = [
        "https://emars.ky.gov/",
        "https://www.kentucky.gov/",
        "https://procurement.ky.gov/",
        "https://www.kentucky.gov/agencies/pages/agency.aspx?AgencyId=12"
    ]
    
    for portal in state_portals:
        try:
            response = requests.get(portal, timeout=30)
            if response.status_code == 200:
                print(f"✅ {portal} - Accessible")
            else:
                print(f"❌ {portal} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {portal} - Error: {e}")

def check_rss_feeds():
    """Check for RSS feeds from school districts"""
    print("\n=== Checking RSS Feeds ===")
    
    # Common RSS feed patterns
    rss_patterns = [
        "/rss",
        "/feed",
        "/news/feed",
        "/announcements/feed",
        "/rfp/feed",
        "/procurement/feed"
    ]
    
    test_districts = [
        "https://www.fayette.kyschools.us",
        "https://www.jefferson.kyschools.us",
        "https://www.kenton.kyschools.us"
    ]
    
    for district in test_districts:
        for pattern in rss_patterns:
            try:
                url = district + pattern
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'xml' in content_type or 'rss' in content_type:
                        print(f"✅ {url} - RSS feed found!")
                    else:
                        print(f"⚠️ {url} - Accessible but not RSS")
                else:
                    print(f"❌ {url} - HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")

def check_news_sections():
    """Check news/announcement sections of accessible websites"""
    print("\n=== Checking News Sections ===")
    
    news_paths = [
        "/news",
        "/announcements", 
        "/district-news",
        "/public-notices",
        "/board-meetings",
        "/documents"
    ]
    
    # Test with a few accessible districts
    test_districts = [
        "https://www.fayette.kyschools.us",
        "https://www.jefferson.kyschools.us"
    ]
    
    for district in test_districts:
        for path in news_paths:
            try:
                url = district + path
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text().lower()
                    
                    # Look for RFP-related content
                    rfp_indicators = ["rfp", "request for proposal", "bid", "tender"]
                    found = [indicator for indicator in rfp_indicators if indicator in text]
                    
                    if found:
                        print(f"✅ {url} - Found RFP indicators: {found}")
                    else:
                        print(f"⚠️ {url} - Accessible but no RFP content")
                else:
                    print(f"❌ {url} - HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")

def check_document_repositories():
    """Check for document repositories and board meeting minutes"""
    print("\n=== Checking Document Repositories ===")
    
    doc_paths = [
        "/documents",
        "/board-meetings",
        "/board-documents",
        "/public-records",
        "/procurement-documents",
        "/contracts"
    ]
    
    test_districts = [
        "https://www.fayette.kyschools.us",
        "https://www.jefferson.kyschools.us"
    ]
    
    for district in test_districts:
        for path in doc_paths:
            try:
                url = district + path
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text().lower()
                    
                    # Look for document links
                    links = soup.find_all('a', href=True)
                    pdf_links = [link for link in links if '.pdf' in link['href'].lower()]
                    
                    if pdf_links:
                        print(f"✅ {url} - Found {len(pdf_links)} PDF documents")
                    else:
                        print(f"⚠️ {url} - Accessible but no PDFs found")
                else:
                    print(f"❌ {url} - HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")

def main():
    """Run all alternative source checks"""
    print("=== Alternative RFP Discovery Sources ===")
    
    check_state_portals()
    check_rss_feeds()
    check_news_sections()
    check_document_repositories()
    
    print("\n=== Recommendations ===")
    print("1. Focus on state-level procurement portals")
    print("2. Look for RSS feeds from school districts")
    print("3. Check news/announcement sections")
    print("4. Monitor board meeting documents")
    print("5. Use manual discovery for JavaScript-heavy sites")

if __name__ == "__main__":
    main() 