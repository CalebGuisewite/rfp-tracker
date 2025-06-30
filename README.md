# RFP Tracker for School District Insurance RFPs

This system crawls school district websites to find insurance-related RFP documents and displays them on a dashboard.

## Components

- **Crawler Service**: Web service that can be triggered to crawl school district websites using Playwright and GPT-4
- **Dashboard**: Streamlit web interface to view found RFPs and trigger crawler runs
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

### Run Services Locally
```bash
# Terminal 1: Run crawler service
python crawler_service.py

# Terminal 2: Run dashboard
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
   - `CRAWLER_SERVICE_URL`: URL of your crawler service (set after first deployment)
4. Deploy using the `render.yaml` configuration

### Services Created
- **rfp-crawler**: Web service that can be triggered to run crawler (Docker-based)
- **rfp-dashboard**: Web service hosting the Streamlit dashboard

### File Sharing
Both services share a persistent disk (`rfp-data`) to store crawler results:
- Crawler: mounted at `/app/shared`
- Dashboard: mounted at `/opt/render/project/src/shared`

### Deployment Architecture
- **Crawler**: Docker container with all necessary system dependencies for Playwright
- **Dashboard**: Python runtime for Streamlit
- **Shared Storage**: Persistent disk for data exchange between services
- **Trigger System**: Manual trigger via dashboard or HTTP POST to `/crawl` endpoint

## Usage

### Manual Crawling
1. Open the dashboard in your browser
2. Use the "Start Crawler" button in the sidebar
3. Monitor the crawler status
4. View results when crawling completes

### API Endpoints
The crawler service provides these endpoints:
- `GET /`: Health check
- `GET /status`: Check if crawler is running
- `POST /crawl`: Trigger a new crawl

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
4. **Service communication**: Ensure `CRAWLER_SERVICE_URL` environment variable is set correctly

### Render-Specific Fixes
- **Playwright dependencies**: Resolved using Docker container with pre-installed system libraries
- **File paths**: Updated to work with both Docker and Python runtime environments
- **Browser compatibility**: Added Render-specific browser launch arguments
- **Cron limitations**: Replaced with web service architecture for better compatibility

### Logs
- Check Render logs for both services
- Crawler logs will show crawl progress and GPT analysis
- Dashboard logs will show file loading and display issues

## Current Limitations
- Single school district hardcoded
- Basic RFP detection
- Simple file-based storage
- Manual triggering required

## Next Steps
- Multi-site crawling
- Database storage
- Enhanced RFP extraction
- Automated scheduling
- Geographic visualization 