#!/usr/bin/env python3
"""
Flask dashboard for RFP crawler - replacing Streamlit
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
SHARED_DIR = os.getenv('SHARED_DIR', '/opt/render/project/src/shared')
RESULTS_FILE = os.path.join(SHARED_DIR, 'rfp_scan_results.json')
DASHBOARD_FILE = os.path.join(SHARED_DIR, 'dashboard_summary.json')

def load_data():
    """Load the latest crawler results"""
    try:
        # Try dashboard summary first (cleaner format)
        if os.path.exists(DASHBOARD_FILE):
            with open(DASHBOARD_FILE, 'r') as f:
                return json.load(f)
        
        # Fallback to full results file
        elif os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r') as f:
                data = json.load(f)
                # Convert to dashboard format
                metadata = data.get('metadata', {})
                return {
                    'timestamp': metadata.get('crawl_timestamp', 'Unknown'),
                    'total_rfps': metadata.get('total_rfps_found', 0),
                    'total_pages': metadata.get('total_pages_crawled', 0),
                    'categories': metadata.get('categories', {}),
                    'active_rfps': data.get('rfp_summary', [])
                }
        else:
            # Return empty data structure when no files exist
            return {
                'timestamp': 'No data yet',
                'total_rfps': 0,
                'total_pages': 0,
                'categories': {},
                'active_rfps': []
            }
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return {
            'error': str(e), 
            'timestamp': 'Error',
            'total_rfps': 0,
            'total_pages': 0,
            'categories': {},
            'active_rfps': []
        }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    data = load_data()
    return render_template('dashboard.html', data=data)

@app.route('/api/data')
def api_data():
    """API endpoint for dashboard data"""
    return jsonify(load_data())

@app.route('/api/status')
def api_status():
    """API endpoint for crawler status"""
    data = load_data()
    return jsonify({
        'status': 'healthy',
        'last_crawl': data.get('timestamp'),
        'total_rfps': data.get('total_rfps', 0),
        'total_pages': data.get('total_pages', 0),
        'crawler_healthy': os.path.exists(RESULTS_FILE) or os.path.exists(DASHBOARD_FILE),
        'shared_dir_exists': os.path.exists(SHARED_DIR),
        'data_files': {
            'results_file': os.path.exists(RESULTS_FILE),
            'summary_file': os.path.exists(DASHBOARD_FILE)
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'app': 'rfp-dashboard',
        'version': '1.0'
    })

if __name__ == '__main__':
    # Create shared directory if it doesn't exist
    os.makedirs(SHARED_DIR, exist_ok=True)
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)