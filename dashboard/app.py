import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

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

# Process the data
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
                "Budget Range": gpt_data.get("budget_range", ""),
                "Confidence": gpt_data.get("confidence", "Low"),
                "RFP Type": gpt_data.get("category", ""),
                "Depth": r["depth"],
                "Content Length": r.get("content_length", 0)
            })
    except Exception as e:
        st.warning(f"Error processing result: {e}")
        continue

if not rows:
    st.info("No employee benefits RFPs found.")
    st.stop()

df = pd.DataFrame(rows)

# Sidebar filters
st.sidebar.header("Filters")

# Confidence filter
confidence_filter = st.sidebar.multiselect(
    "Confidence Level",
    options=df["Confidence"].unique(),
    default=df["Confidence"].unique()
)

# Filter the dataframe
filtered_df = df[df["Confidence"].isin(confidence_filter)]

# Display statistics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total RFPs Found", len(filtered_df))
with col2:
    high_confidence = len(filtered_df[filtered_df["Confidence"] == "High"])
    st.metric("High Confidence", high_confidence)
with col3:
    st.metric("Average Content Length", f"{filtered_df['Content Length'].mean():.0f} chars")

# Display the data
st.subheader("Employee Benefits RFPs")
st.dataframe(filtered_df, use_container_width=True)

# Download options
col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "Download CSV", 
        filtered_df.to_csv(index=False), 
        "rfps.csv",
        mime="text/csv"
    )
with col2:
    st.download_button(
        "Download JSON", 
        json.dumps(filtered_df.to_dict('records'), indent=2), 
        "rfps.json",
        mime="application/json"
    )

# Show raw data for debugging
with st.expander("Raw Crawl Data"):
    st.json(data)
