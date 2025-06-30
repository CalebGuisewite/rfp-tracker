from flask import Flask, jsonify
import subprocess
import os
import threading
import time

app = Flask(__name__)

# Global variable to track if crawler is running
crawler_running = False
crawler_lock = threading.Lock()

@app.route("/")
def health():
    return jsonify({
        "status": "healthy", 
        "service": "rfp-crawler",
        "crawler_running": crawler_running
    })

@app.route("/crawl", methods=["POST"])
def trigger_crawl():
    global crawler_running
    
    with crawler_lock:
        if crawler_running:
            return jsonify({
                "status": "error", 
                "message": "Crawler is already running"
            }), 409
        
        crawler_running = True
    
    try:
        # Run crawler in a separate thread to avoid blocking
        def run_crawler():
            global crawler_running
            try:
                result = subprocess.run(
                    ["bash", "crawler/start.sh"], 
                    capture_output=True, 
                    text=True, 
                    timeout=300
                )
                print(f"Crawler completed with return code: {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
            except Exception as e:
                print(f"Crawler error: {e}")
            finally:
                with crawler_lock:
                    crawler_running = False
        
        # Start crawler in background thread
        thread = threading.Thread(target=run_crawler)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "Crawler started successfully",
            "crawler_running": True
        })
        
    except Exception as e:
        with crawler_lock:
            crawler_running = False
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route("/status")
def get_status():
    return jsonify({
        "crawler_running": crawler_running,
        "timestamp": time.time()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080))) 