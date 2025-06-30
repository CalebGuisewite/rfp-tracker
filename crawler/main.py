from crawl_site_enhanced import crawl_site
import json
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
shared_dir = os.path.join(project_root, "shared")
os.makedirs(shared_dir, exist_ok=True)

results = crawl_site("https://www.carroll.kyschools.us")

output_file = os.path.join(shared_dir, "rfp_scan_results.json")
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_file}")
