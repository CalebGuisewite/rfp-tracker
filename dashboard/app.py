import streamlit as st
import pandas as pd
import json
import os
import requests

st.set_page_config(page_title="RFP Dashboard", layout="wide")
st.title("📄 Employee Benefits RFP Dashboard")

# Sidebar for crawler controls
st.sidebar.header("🕷️ Crawler Controls")

# Get crawler service URL from environment or use default
crawler_url = os.getenv("CRAWLER_SERVICE_URL", "https://your-crawler-service.onrender.com")

# Check crawler status
try:
    status_response = requests.get(f"{crawler_url}/status", timeout=5)
    crawler_status = status_response.json()
    st.sidebar.info(f"Crawler Status: {'🟢 Running' if crawler_status.get('crawler_running') else '🔴 Idle'}")
except Exception as e:
    st.sidebar.warning(f"Could not connect to crawler: {e}")
    crawler_status = {"crawler_running": False}

# Trigger crawler button
if st.sidebar.button("🚀 Start Crawler", disabled=crawler_status.get("crawler_running", False)):
    try:
        response = requests.post(f"{crawler_url}/crawl", timeout=10)
        if response.status_code == 200:
            st.sidebar.success("Crawler started successfully!")
            st.rerun()
        else:
            st.sidebar.error(f"Failed to start crawler: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        st.sidebar.error(f"Error starting crawler: {e}")

# Main dashboard content
st.header("📊 RFP Results")

# Try multiple possible paths for the results file
possible_paths = [
    "../shared/rfp_scan_results.json",
    "shared/rfp_scan_results.json",
    "./shared/rfp_scan_results.json"
]

data = None
for path in possible_paths:
    try:
        with open(path, "r") as f:
            data = json.load(f)
            st.success(f"Data loaded from: {path}")
            break
    except FileNotFoundError:
        continue

if data is None:
    st.error("rfp_scan_results.json not found in any expected location.")
    st.info("The crawler may not have run yet, or the file path is incorrect.")
    st.info("Click the 'Start Crawler' button in the sidebar to begin crawling.")
    st.stop()

rows = []
for r in data:
    try:
        gpt_data = json.loads(r['gpt_result'])
        if gpt_data.get("is_rfp") and gpt_data.get("category", "").lower() == "employee benefits":
            rows.append({
                "School URL": r["url"],
                "Summary": gpt_data.get("summary", ""),
                "Deadline": gpt_data.get("submission_deadline", ""),
                "Submission Location": gpt_data.get("submission_location", ""),
                "Contact Email": gpt_data.get("contact_email", ""),
                "RFP Type": gpt_data.get("category", ""),
                "Depth": r["depth"]
            })
    except Exception as e:
        st.warning(f"Error processing result: {e}")
        continue

if not rows:
    st.info("No employee benefits RFPs found.")
    st.info("The crawler may need to run again or the school district may not have any current RFPs.")
    st.stop()

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)
st.download_button("Download CSV", df.to_csv(index=False), "rfps.csv")
