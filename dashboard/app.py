import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="RFP Dashboard", layout="wide")
st.title("📄 Employee Benefits RFP Dashboard")

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
shared_dir = os.path.join(project_root, "shared")
results_file = os.path.join(shared_dir, "rfp_scan_results.json")

try:
    with open(results_file, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    st.error(f"rfp_scan_results.json not found at {results_file}")
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
    except Exception:
        continue

if not rows:
    st.info("No employee benefits RFPs found.")
    st.stop()

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)
st.download_button("Download CSV", df.to_csv(index=False), "rfps.csv")
