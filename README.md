# Vinyl Cut Server

A local web app for controlling Silhouette-compatible vinyl cutters from a browser on another computer on the same local network.

This version runs as a local web interface on a Raspberry Pi, Armbian box, or Linux PC and exposes a simple API for:

- uploading SVG files
- scanning detected USB devices
- queuing and starting jobs
- viewing live progress and logs
- cancelling jobs

This is intentionally a practical local-first implementation for real cutter hardware.

## Features

- FastAPI backend
- browser dashboard
- SQLite-backed job persistence
- USB device scanning via pyusb for supported Silhouette devices
- real cutter execution flow for connected devices
- install script and systemd example

## Requirements

- Python 3.10+
- USB access for a connected Silhouette-compatible cutter
- A real backend command or script for actual cutter execution

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

```text
http://<your-pi-or-linux-host>:8000
```

## Local network access

This app is intended to be used from another PC on the same LAN, for example by visiting:

```text
http://192.168.1.50:8000
```

## Installing on an Armbian box

Run these commands on the target device:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip libusb-1.0-0-dev

cd /opt
sudo git clone https://github.com/percaine/vinyl-cut-server.git
cd vinyl-cut-server

git checkout remove-demo-mode
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Then start it manually:

```bash
source /opt/vinyl-cut-server/.venv/bin/activate
cd /opt/vinyl-cut-server

export CUTTER_BACKEND_COMMAND="python3 /path/to/your/silhouette/backend.py"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the app from a browser on the same network:

```text
http://<armbian-ip>:8000
```

## Running as a systemd service

Create a service file:

```bash
sudo nano /etc/systemd/system/vinyl-cut-server.service
```

With contents:

```ini
[Unit]
Description=Vinyl Cut Server
After=network.target

[Service]
User=root
WorkingDirectory=/opt/vinyl-cut-server
Environment="CUTTER_BACKEND_COMMAND=python3 /path/to/your/silhouette/backend.py"
ExecStart=/opt/vinyl-cut-server/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vinyl-cut-server
sudo systemctl start vinyl-cut-server
sudo systemctl status vinyl-cut-server
```

## Real device requirements

This app requires a physically connected Silhouette-compatible USB cutter. It does not include demo or simulated device behavior.

The actual job execution path requires a real backend command or script. Configure one using either:

```bash
export CUTTER_BACKEND_COMMAND="/path/to/real/backend"
```

or:

```bash
export CUTTER_BACKEND_SCRIPT="/path/to/real/backend.py"
```

If no real backend is configured, the app will fail with a clear backend configuration error instead of running a simulated cut.

## Notes

This is intentionally a local-first prototype for real hardware. It is not a demo or simulation mode.

## Next steps

- integrate the upstream Silhouette backend workflow directly
- add richer device metadata and connection diagnostics
- improve job history, persistence, and recovery
- add authentication and local-only network binding
- add more formal error reporting for cutter failures
