# 🍯 Building and Monitoring a Honeypot (Threat Intelligence Decoy)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask 3.x](https://img.shields.io/badge/Flask-3.x-black.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/Tests-13%20Passed-brightgreen.svg)]()
[![Security](https://img.shields.io/badge/Security-Honeypot%20%2F%20Decoy-red.svg)]()

A lightweight, dual-vector cybersecurity decoy honeypot featuring a deceptive administrative web portal and an optional SSH lure. The system attracts, traps, logs, and analyzes unauthorized reconnaissance, brute-force credential stuffing, and remote command injection attacks in real time.

---

## 📋 Table of Contents

- [Overview & Objectives](#-overview--objectives)
- [Architecture & Components](#-architecture--components)
- [Honeytraps & Attack Vectors](#-honeytraps--attack-vectors)
- [Directory Structure](#-directory-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Running the Honeypot](#-running-the-honeypot)
  - [Option A: Windows (PowerShell)](#option-a-windows-powershell)
  - [Option B: Linux (Bash Service)](#option-b-linux-bash-service)
  - [Option C: Manual / Cross-Platform](#option-c-manual--cross-platform)
- [Real-Time Log Monitor](#-real-time-log-monitor)
- [Environment Configuration](#-environment-configuration)
- [Automated Testing & Verification](#-automated-testing--verification)
- [⚠️ Security & Isolation Advisory](#️-security--isolation-advisory)
- [Credits](#-credits)

---

## 🎯 Overview & Objectives

In modern cyber defense and threat research, honeypots serve as critical early-warning sensors. This project deploys a realistic, intentionally vulnerable decoy environment to:

1. **Detect Intrusion Attempts Early**: Trap automated vulnerability scanners, threat actors, and credential stuffers before they reach production services.
2. **Harvest Attacker Telemetry**: Capture source IP addresses, HTTP request headers, target URIs, brute-force credentials, and command payloads.
3. **Monitor Live Activity**: Stream incoming attacks into a colorized, dynamically formatted terminal dashboard for immediate situational awareness.

---

## 🏗️ Architecture & Components

The honeypot architecture consists of three interconnected layers:

```
                  ┌──────────────────────────────────────────┐
                  │           Threat Actor / Scanner         │
                  └─────────────────────┬────────────────────┘
                                        │
                         HTTP (Port 80) │ SSH (Port 22)
                                        ▼
    ┌───────────────────────────────────┬──────────────────────────────────┐
    │                                   │                                  │
    │  🌐 Flask Web Decoy (app.py)      │  🔒 SSH Service (Linux)          │
    │  - Deceptive Portal (/)           │  - Port 22 SSH Daemon            │
    │  - Credential Lure (/login)       │  - Authentication logs           │
    │  - Command Injection (/vulnerable)│                                  │
    └─────────────────┬─────────────────┴──────────────────────────────────┘
                      │
                      ▼
         [ 📄 honeypot.log (Common Log + RCE Audit) ]
                      │
                      ▼
    ┌──────────────────────────────────────────────────────────────────────┐
    │  🖥️ Real-Time Log Monitor (monitor_honeypot.py)                     │
    │  - Real-time tailing engine                                          │
    │  - Regex parser for HTTP and injected commands                       │
    │  - Colorized terminal matrix (Green=200, Red=401/403, Yellow=404)    │
    └──────────────────────────────────────────────────────────────────────┘
```

1. **Web Decoy Application (`app.py`)**:
   - Built on Flask 3.x with clean Jinja2 templates mimicking an internal enterprise management portal.
   - Automatically logs all HTTP requests, client IPs, timestamps, HTTP status codes, and execution payloads.
   - Cross-platform: automatically adapts between `/var/log/honeypot.log` (Linux root) and local `honeypot.log` (Windows/dev).

2. **Real-Time Monitor (`monitor_honeypot.py`)**:
   - Tails the log file continuously (`tail -f` behavior).
   - Dynamically parses Common Log Format web requests, command submissions, and stdout/stderr responses.
   - Formats outputs in an auto-aligning ASCII table with colorized HTTP status alerts.

3. **Deployment Scripts**:
   - `run_honeypot.ps1`: Native PowerShell automation script for Windows workstations/servers.
   - `run_honeypot.sh`: Linux deployment script that launches the Flask daemon and starts the system SSH service.

4. **Automated Test Suite (`test_honeypot.py`)**:
   - Comprehensive unit and integration test suite with 13 automated tests covering routes, authentication, command execution, log generation, and parser fidelity.

---

## 🪤 Honeytraps & Attack Vectors

| Route / Service | Decoy Purpose | Observed Attacker Behavior |
| :--- | :--- | :--- |
| `GET /` | Enterprise Portal Decoy | Reconnaissance, directory indexing probes |
| `GET /login` | Admin Authentication Form | Probing for authentication mechanisms |
| `POST /login` | Credential Trap | Captures brute-force attacks (`admin`/`admin` default) |
| `GET /admin` | Admin Dashboard | Lures the attacker into interacting with server controls |
| `GET /vulnerable?cmd=` | Command Injection Trap | Logs command payloads (e.g. `whoami`, `cat /etc/passwd`) |
| `SSH (Port 22)` | Secure Shell Lure | Logs unauthorized SSH connection and authentication attempts |

---

## 📁 Directory Structure

```text
Building-And-Monitoring-Honeypot/
├── app.py                  # Core Flask decoy web server & honeypot logic
├── monitor_honeypot.py     # Real-time log monitoring terminal dashboard
├── test_honeypot.py        # Automated test suite (13 unit/integration tests)
├── requirements.txt        # Python dependency manifest (Flask 3.x, Werkzeug, Jinja2)
├── run_honeypot.ps1        # Automated deployment script for Windows (PowerShell)
├── run_honeypot.sh         # Automated deployment script for Linux (Bash)
├── Dockerfile              # Containerization definition for isolated deployment
├── docker-compose.yml      # Docker compose configuration
├── LICENSE                 # MIT License (Copyright (c) 2026 Tanishq Atul Zope)
├── .gitignore              # Git ignore rules (.venv, logs, cache)
├── README.md               # Project documentation
└── templates/              # Decoy web portal HTML templates
    ├── base.html           # Master layout template and styling
    ├── home.html           # Landing page ("Organisation Management")
    ├── login.html          # Admin login interface with flash messaging
    ├── admin.html          # Admin control panel with mock server actions
    └── vulnerable.html     # Command execution response page
```

---

## ⚙️ Prerequisites

- **Python**: Version 3.10 or newer (tested and verified on Python 3.10, 3.12, 3.13, and 3.14).
- **Administrative Privileges** (Optional): Required only if binding directly to privileged port `80` or managing system SSH service on port `22`. The application includes automatic fallback to unprivileged port `5000` if port 80 is restricted.
- **Supported OS**: Windows 10/11/Server, Linux (Ubuntu, Debian, RHEL, CentOS), or macOS.

---

## 📦 Installation

### 1. Clone or Open the Repository
```bash
git clone https://github.com/tanishqzope/Building-And-Monitoring-Honeypot.git
cd Building-And-Monitoring-Honeypot
```

### 2. Set Up a Python Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Honeypot

### Option A: Windows (PowerShell)

Run the included automated launch script:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_honeypot.ps1
```

The script will:
- Detect the active virtual environment (`.venv`).
- Start the Flask honeypot in the background.
- Attempt port `80` (or gracefully fall back to port `5000` if port 80 requires administrator elevation).
- Verify the HTTP service is online.
- Display process information and monitor launch commands.

To stop the background server:
```powershell
Stop-Process -Name python
```

---

### Option B: Linux (Bash Service)

For Linux environments with `systemd` and OpenSSH:
```bash
chmod +x run_honeypot.sh
sudo ./run_honeypot.sh
```

The script will:
- Check for required system utilities (`python`, `nohup`, `systemctl`, `curl`).
- Launch the Flask honeypot in the background (`nohup python app.py > flask.log 2>&1 &`).
- Start the system SSH daemon on port 22 (`sudo systemctl start ssh`).
- Validate that the HTTP service is listening on port 80.

---

### Option C: Manual / Cross-Platform

You can also run the web decoy directly with Python:

```bash
# Default (attempts port 80, falls back to 5000 if restricted):
python app.py

# Or specify a custom port:
# Windows (PowerShell):
$env:PORT = "8080"; python app.py

# Linux / macOS:
PORT=8080 python app.py
```

Once running, access the portal via your browser or testing tool:
- **Landing Page**: `http://localhost/` (or `http://localhost:5000/`)
- **Admin Login**: `http://localhost/login` (Default decoy credentials: `admin` / `admin`)
- **Admin Panel**: `http://localhost/admin`
- **RCE Honeypot Route**: `http://localhost/vulnerable?cmd=whoami`

---

## 📊 Real-Time Log Monitor

In a separate terminal window, launch the interactive live log monitor:

```bash
# Windows
.\.venv\Scripts\python monitor_honeypot.py

# Linux / macOS
python monitor_honeypot.py
```

### Sample Monitor Output:
```text
Monitoring C:\Users\...\Honeypot-master\honeypot.log for new entries...

Timestamp               | IP Address    | Method | Path                        | Status | Reason | Command    | Command Output
------------------------+---------------+--------+-----------------------------+--------+--------+------------+--------------------
2026-11-09 23:19:43,197 | 127.0.0.1     | GET    | /admin                      | 200    | -      |            |
2026-11-09 23:19:43,210 | 127.0.0.1     | GET    | /login                      | 200    | -      |            |
2026-11-09 23:19:43,212 |               |        |                             |        |        | whoami     |
2026-11-09 23:19:43,367 |               |        |                             |        |        |            | server-admin
2026-11-09 23:19:43,374 | 127.0.0.1     | GET    | /vulnerable?cmd=whoami      | 200    | -      |            |
2026-11-09 23:19:43,428 | 127.0.0.1     | POST   | /login                      | 401    | -      |            |
```

---

## 🔧 Environment Configuration

You can customize the honeypot behavior using environment variables:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `80` (fallback `5000`) | Network port for the Flask HTTP service. |
| `HOST` | `0.0.0.0` | Bind IP address (`0.0.0.0` listens on all network interfaces). |
| `HONEYPOT_LOG` | Auto-detected | Path to the audit log. Defaults to `/var/log/honeypot.log` on Linux if writable, otherwise `./honeypot.log`. |
| `SECRET_KEY` | `your_secret_key` | Flask session secret key for cookie signing. |

---

## 🧪 Automated Testing & Verification

The project includes a comprehensive test suite in `test_honeypot.py` that verifies the entire system:

```bash
# Run all tests using Python's unittest runner:
python test_honeypot.py
```

### Test Coverage Breakdown:
- `test_home_page`: Validates home template rendering and status 200.
- `test_login_page_get`: Verifies login form inputs.
- `test_login_invalid_credentials`: Checks 401 Unauthorized response and flash alerts.
- `test_login_valid_credentials`: Verifies 302 redirection to `/admin`.
- `test_admin_dashboard`: Checks dashboard navigation links and actions.
- `test_logout`: Confirms session termination and redirection to `/`.
- `test_vulnerable_no_cmd`: Validates graceful handling of blank RCE requests.
- `test_vulnerable_with_cmd`: Executes a real test command, verifies captured output, and validates log file generation.
- `test_log_parser_http`: Validates regex parsing of Common Log Format web requests.
- `test_log_parser_command`: Validates command injection parsing.
- `test_log_parser_command_multiword`: Ensures multi-word commands (e.g. `cat /etc/passwd`) are captured without truncation.
- `test_log_parser_command_output`: Validates command output extraction.
- `test_end_to_end_log_processing`: Full integration test connecting the HTTP client, file logger, and live parser.

---

## ⚠️ Security & Isolation Advisory

> [!CAUTION]
> **HIGH-RISK VULNERABILITY SIMULATION**: The `/vulnerable` route intentionally executes received commands directly via `subprocess.run(..., shell=True)`.
> 
> - **DO NOT** run this honeypot directly on your primary host operating system, production servers, or open corporate network without containment.
> - **CONTAINMENT RECOMMENDATION**: Always deploy the honeypot inside an **isolated Docker container**, **chroot jail**, or dedicated **sandboxed Virtual Machine (VM)** with egress firewall rules blocking outbound network connections.
> - **CREDENTIAL WARNING**: The login credentials (`admin` / `admin`) are intentionally trivial for decoy purposes; ensure this system has no access to sensitive production data or lateral network pathways.

---

## 👤 Credits & Author

- **Author / Maintainer**: Tanishq Atul Zope ([@tanishqzope](https://github.com/tanishqzope))
- **Repository**: [tanishqzope/Building-And-Monitoring-Honeypot](https://github.com/tanishqzope/Building-And-Monitoring-Honeypot)
- **License**: [MIT License](LICENSE)
- **Attribution**: Built upon high-interaction decoy concepts originally demonstrated by [@whxite](https://github.com/whxite).
- **Purpose**: Educational Threat Analysis, Defensive Cybersecurity & Cyber Deception Research

