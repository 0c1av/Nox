
# Nox – Penetration Testing & Target Monitoring Tool

Nox is a comprehensive penetration testing tool designed to scan targets, track related targets, and provide a web-based overview of all scans and results. It combines directory scanning, vulnerability testing (XSS, SQL, ...), and real-time monitoring in a single Dockerized solution.




## Features

- Single Target Scan – Scan a specific target for directories, vulnerabilities, and other information.
- Related Target Monitoring – Dynamically discover and monitor targets related to the main target.
- Web Interface – View all scanned targets, results, and historical data through a Flask-based dashboard.
- Persistent Scanning – Keep track of scan history for all targets.
- Easy Deployment – Fully packaged in Docker, with all dependencies included.
- Proxy & Authentication Support – Scan behind proxies or with authentication if needed.
- Real-Time XSS Tracking – Uses Selenium and Flask to detect XSS payloads in real-time.


## Installation

### Prerequisites
Docker installed on your system (https://www.docker.com/get-started/)

### Steps

```bash
git clone https://github.com/0c1av/Nox.git
cd Nox

docker-compose build

```
## Usage
- Activate webserver available at http://localhost:5000/:
```bash
docker compose up
```

- Scan a single target: 
```bash 
docker compose run --rm nox python main.py
```

- Scan a target and related targets:
```bash
docker compose run --rm nox python main.py
```

- Shut everything down:
```bash
docker compose down
```
## Legal Notice
Nox is intended for ethical penetration testing only. Users must have permission to scan and test targets. Misuse of this tool may violate laws in your country.

By using Nox, you agree to comply with all applicable laws and regulations.
## Support

For questions, issues, or guidance on using Nox, contact Camil Caudron at: 0c1avf@gmail.com
