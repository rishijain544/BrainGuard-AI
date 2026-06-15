#!/usr/bin/env python
import subprocess
import sys
import os
import time
import webbrowser
import threading

def start_backend():
    os.chdir(r'd:\brain_tumour_prediction\backend')
    subprocess.run([sys.executable, '-m', 'uvicorn', 'fastapi_backend:app', '--host', '0.0.0.0', '--port', '8000'])

if __name__ == '__main__':
    print("Starting BrainGuard AI...")
    
    # Start the FastAPI backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait for the backend to initialize
    print("Initializing models and server, please wait...")
    time.sleep(4)
    
    # Automatically open the frontend in the default browser
    print("Opening frontend...")
    webbrowser.open('http://localhost:8000/index.html')
    
    # Keep the main script running so the server stays alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down BrainGuard AI.")
        sys.exit(0)
