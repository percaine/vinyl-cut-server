# Vinyl Cut Server

A first-pass local web app for controlling vinyl cutters such as Silhouette Cameo and related devices from a browser on another PC.

This version runs as a local web interface on a Raspberry Pi or Linux PC and exposes a simple API for:

- uploading SVG files
- scanning detected devices
- queuing and starting jobs
- viewing live progress and logs
- cancelling jobs

This is intentionally a practical first version built around a local network browser interface.

## Features

- FastAPI backend
- simple browser dashboard
- in-memory job queue
- device scanning (USB via pyusb when available, otherwise simulated devices)
- simulated job execution for first-run testing
- install script and systemd example

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

## Notes

This first version is intentionally a working local prototype. It does not yet fully integrate all Silhouette USB/Bluetooth logic from the upstream Inkscape extension, but it provides a clean browser workflow and a codebase that can evolve toward direct hardware integration.

## Next steps

- directly run the upstream `sendto_silhouette.py` workflow as a backend executor
- integrate real USB/Bluetooth detection and control
- add queue persistence with SQLite
- add file previews and richer job history
- add authentication and local-only network binding
