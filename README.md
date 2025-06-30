# RFP Tracker for School District Insurance RFPs

This system crawls school district websites to find insurance-related RFP documents and displays them on a dashboard.

## Components

- **Crawler**: Uses Playwright to crawl school district websites and GPT-4 to analyze content for insurance RFPs
- **Dashboard**: Streamlit web interface to view and download found RFPs
- **Shared Storage**: JSON file storage for data between crawler and dashboard

## Local Testing

### Prerequisites
1. Python 3.8+
2. OpenAI API key
3. Git

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r crawler/requirements.txt
   pip install -r dashboard/requirements.txt
   playwright install
   ```
3. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Test Locally
```bash
python test_local.py
```

### Run Dashboard Locally
```bash
streamlit run dashboard/app.py
```

## Render Deployment

### Prerequisites
1. Render account
2. OpenAI API key

### Deploy Steps
1. Push your code to GitHub
2. Connect your repository to Render
3. Set environment variables in Render:
   - `OPENAI_API_KEY`: Your OpenAI API key
4. Deploy using the `render.yaml` configuration

### Services Created
- **rfp-crawler**: Cron job that runs daily at 2 AM (Docker-based for Playwright compatibility)
- **rfp-dashboard**: Web service hosting the Streamlit dashboard

### File Sharing
Both services share a persistent disk (`rfp-data`) to store crawler results:
- Crawler: mounted at `/app/shared`
- Dashboard: mounted at `/opt/render/project/src/shared`

### Deployment Architecture
- **Crawler**: Uses Docker container with all necessary system dependencies for Playwright
- **Dashboard**: Uses Python runtime for Streamlit
- **Shared Storage**: Persistent disk for data exchange between services

## Configuration

### Adding More School Districts
Edit `crawler/main.py` to add more URLs to crawl:
```python
# Add more school districts here
schools = [
    "https://www.carroll.kyschools.us",
    "https://www.anotherschool.edu",
    # ... more schools
]
```

### Adjusting Crawl Settings
Modify `crawler/crawl_site_enhanced.py`:
- `max_depth`: How deep to crawl (default: 4)
- GPT prompt: Customize what types of RFPs to look for

## Troubleshooting

### Common Issues
1. **"rfp_scan_results.json not found"**: The crawler hasn't run yet or there's a file path issue
2. **OpenAI API errors**: Check your API key and billing
3. **Playwright issues**: The Docker container includes all necessary dependencies

### Render-Specific Fixes
- **Playwright dependencies**: Resolved using Docker container with pre-installed system libraries
- **File paths**: Updated to work with both Docker and Python runtime environments
- **Browser compatibility**: Added Render-specific browser launch arguments

### Logs
- Check Render logs for both services
- Crawler logs will show crawl progress and GPT analysis
- Dashboard logs will show file loading and display issues

## Current Limitations
- Single school district hardcoded
- Basic RFP detection
- Simple file-based storage
- No notification system

## Next Steps
- Multi-site crawling
- Database storage
- Enhanced RFP extraction
- Notification system
- Geographic visualization 