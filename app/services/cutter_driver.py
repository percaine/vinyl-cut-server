# Vinyl Cut Server

A local web app for controlling Silhouette-compatible vinyl cutters from a browser on the same network.

This version runs as a local web interface on a Raspberry Pi or Linux PC and exposes a simple API for:

- uploading SVG files
- scanning detected USB devices
- queuing and starting jobs
- viewing live progress and logs
- cancelling jobs

This is intentionally a practical local-first implementation for real cutter hardware.

## Features

- FastAPI backend
- browser dashboard
- in-memory job queue with SQLite persistence
- USB device scanning via pyusb for supported Silhouette devices
- real cutter execution flow for connected devices
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

This app requires a physically connected Silhouette-compatible USB cutter. It does not include demo or simulated device behavior.

## Next steps

- directly run the upstream `sendto_silhouette.py` workflow as a backend executor
- integrate real USB/Bluetooth detection and control
- add queue persistence with SQLite
- add file previews and richer job history
- add authentication and local-only network binding

