# Render Deployment Instructions

## Step-by-Step Guide

### 1. Prepare Your Repository
- Ensure all files are committed to your GitHub repository
- Make sure you have an OpenAI API key ready

### 2. Deploy to Render
1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Click "Apply" to deploy both services

### 3. Set Environment Variables
After the initial deployment:

1. **For the Crawler Service (`rfp-crawler`)**:
   - Go to the service dashboard
   - Click "Environment" tab
   - Add: `OPENAI_API_KEY` = your actual OpenAI API key

2. **For the Dashboard Service (`rfp-dashboard`)**:
   - Go to the service dashboard  
   - Click "Environment" tab
   - Add: `CRAWLER_SERVICE_URL` = your crawler service URL (e.g., `https://rfp-crawler-xyz.onrender.com`)

### 4. Test the Deployment

1. **Test Crawler Service**:
   - Visit your crawler service URL
   - You should see: `{"status": "healthy", "service": "rfp-crawler", "crawler_running": false}`

2. **Test Dashboard**:
   - Visit your dashboard service URL
   - You should see the RFP dashboard with a "Start Crawler" button

3. **Test Crawler Trigger**:
   - Click "Start Crawler" in the dashboard
   - Check the crawler service logs to see the crawling progress
   - Wait for completion and refresh the dashboard to see results

### 5. Monitor and Troubleshoot

**Check Logs**:
- Both services have log tabs in their Render dashboards
- Monitor for any errors during deployment or crawling

**Common Issues**:
- **Crawler not starting**: Check if `OPENAI_API_KEY` is set correctly
- **Dashboard can't connect to crawler**: Verify `CRAWLER_SERVICE_URL` is correct
- **No results found**: The school district may not have current RFPs, or the crawler needs to run

### 6. Manual Crawler Trigger (Alternative)
If the dashboard button doesn't work, you can trigger the crawler manually:

```bash
curl -X POST https://your-crawler-service.onrender.com/crawl
```

### 7. Verify File Sharing
After a successful crawl, both services should be able to access the same data file through the shared persistent disk.

## Service URLs
- **Crawler**: `https://rfp-crawler-{random}.onrender.com`
- **Dashboard**: `https://rfp-dashboard-{random}.onrender.com`

## Next Steps After Deployment
1. Test the complete workflow
2. Add more school districts to crawl
3. Customize the RFP detection criteria
4. Set up monitoring and alerts 