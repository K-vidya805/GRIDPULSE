import subprocess
import webbrowser
import time
import os
import sys

# Configuration
FRONTEND_PORT = 8000
BACKEND_PORT = 5000

# Ensure we are in the same folder as the files
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=========================================")
print("🚀 Starting GRIDPULSE...")
print("=========================================")

# 1. Start the Flask Backend (app.py)
print("🤖 Starting Machine Learning Backend (Flask)...")
# Using sys.executable ensures it uses the same Python environment
backend_process = subprocess.Popen([sys.executable, "app.py"])

# Give Flask a second to boot up
time.sleep(2) 

# 2. Start the Frontend (Python HTTP Server)
print("🌍 Starting Frontend Web Server...")
frontend_process = subprocess.Popen([sys.executable, "-m", "http.server", str(FRONTEND_PORT)])

# 3. Open the browser
time.sleep(1) # Give the web server a second to start
url = f"http://localhost:{FRONTEND_PORT}/index.html"
print(f"✅ Opening browser at {url}")
webbrowser.open_new(url)

print("=========================================")
print("⚠️  GRIDPULSE is running.")
print("🛑 Press Ctrl+C in this terminal to stop everything.")
print("=========================================")

# Keep the script running until Ctrl+C is pressed
try:
    # Wait for the backend process to finish (which keeps the script alive)
    backend_process.wait()
except KeyboardInterrupt:
    print("\n🛑 Shutting down GRIDPULSE...")
    
    # Terminate both processes
    backend_process.terminate()
    frontend_process.terminate()
    
    print("✅ Servers stopped successfully.")