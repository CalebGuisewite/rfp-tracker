from crawl_site_enhanced import crawl_site
import json
import os

# Create shared directory in multiple possible locations
possible_shared_dirs = [
    "shared",
    "/app/shared",
    "../shared",
    "./shared"
]

shared_dir = None
for dir_path in possible_shared_dirs:
    try:
        os.makedirs(dir_path, exist_ok=True)
        shared_dir = dir_path
        print(f"Using shared directory: {shared_dir}")
        break
    except Exception as e:
        print(f"Could not create {dir_path}: {e}")
        continue

if shared_dir is None:
    raise Exception("Could not create shared directory")

print("Starting RFP crawler...")
results = crawl_site("https://www.carroll.kyschools.us")

output_file = os.path.join(shared_dir, "rfp_scan_results.json")
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {output_file}")
print(f"Found {len(results)} pages")
