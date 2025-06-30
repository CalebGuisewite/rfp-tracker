
from crawl_site_enhanced import crawl_site
import json
import os

os.makedirs("../shared", exist_ok=True)

results = crawl_site("https://www.carroll.kyschools.us")

with open("../shared/rfp_scan_results.json", "w") as f:
    json.dump(results, f, indent=2)
