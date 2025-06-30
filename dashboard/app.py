import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="RFP Dashboard", layout="wide")
st.title("📄 Employee Benefits RFP Dashboard")

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
    st.stop()

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)
st.download_button("Download CSV", df.to_csv(index=False), "rfps.csv")
