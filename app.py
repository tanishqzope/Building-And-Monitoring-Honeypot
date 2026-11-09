import os
import subprocess
import logging
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Needed for session management and flash messages

# Resolve honeypot log file path (cross-platform with graceful fallback)
LOG_FILE = os.environ.get('HONEYPOT_LOG')
if not LOG_FILE:
    # Check if /var/log is writable (typical Linux environment with root)
    if os.path.exists('/var/log') and os.access('/var/log', os.W_OK):
        LOG_FILE = '/var/log/honeypot.log'
    else:
        # Fallback to local directory for development / Windows / non-root environments
        LOG_FILE = os.path.abspath('honeypot.log')

# Ensure parent directory exists
os.makedirs(os.path.dirname(os.path.abspath(LOG_FILE)), exist_ok=True)

# Set up logging to file
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Hardcoded credentials
USERNAME = 'admin'
PASSWORD = 'admin'

@app.after_request
def log_request_info(response):
    """Log incoming HTTP requests in standard Common Log format for monitor_honeypot."""
    client_ip = request.remote_addr or '127.0.0.1'
    status_code = response.status_code
    protocol = request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')
    req_time = datetime.now().strftime('%d/%b/%Y:%H:%M:%S +0000')
    # Full requested path (including query string if present)
    target_path = request.full_path.rstrip('?')
    logging.info(f'{client_ip} - - [{req_time}] "{request.method} {target_path} {protocol}" {status_code} -')
    return response

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return render_template('login.html'), 401  # Explicitly set status code for errors

    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

@app.route('/vulnerable', methods=['GET'])
def vulnerable():
    cmd = request.args.get('cmd')
    if cmd:
        try:
            # Log the received command
            logging.info(f"Received command: {cmd}")
            
            # Execute the command with shell=True
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Capture the output
            output = result.stdout + result.stderr
            
            # Log the command output
            logging.info(f"Command output: {output}")
            
        except Exception as e:
            output = f"Error: {str(e)}"
            logging.error(f"Error executing command: {e}")
    else:
        output = 'No command provided'
    
    return render_template('vulnerable.html', output=output)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    host = os.environ.get('HOST', '0.0.0.0')
    print(f"[*] Starting Honeypot on {host}:{port} (Logging to: {LOG_FILE})")
    try:
        app.run(host=host, port=port, debug=True)
    except (PermissionError, OSError) as e:
        fallback_port = 5000
        print(f"[!] Unable to bind on port {port} ({e}). Falling back to port {fallback_port}...")
        app.run(host=host, port=fallback_port, debug=True)
