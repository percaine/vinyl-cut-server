from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import usb  # type: ignore
except Exception:  # pragma: no cover
    usb = None


class DeviceManager:
    def scan(self) -> List[Dict[str, Any]]:
        devices: List[Dict[str, Any]] = []

        if usb is not None:
            try:
                for dev in usb.core.find(find_all=True):
                    vendor_id = getattr(dev, "idVendor", None)
                    product_id = getattr(dev, "idProduct", None)
                    if vendor_id is None or product_id is None:
                        continue
                    devices.append(
                        {
                            "id": f"usb-{vendor_id:04x}-{product_id:04x}",
                            "name": f"USB device {vendor_id:04x}:{product_id:04x}",
                            "kind": "usb",
                            "status": "ready",
                            "details": {
                                "vendor_id": vendor_id,
                                "product_id": product_id,
                            },
                        }
                    )
            except Exception:
                pass

        if not devices:
            devices.append(
                {
                    "id": "simulated-usb-cutter",
                    "name": "Simulated USB cutter",
                    "kind": "usb",
                    "status": "demo",
                    "details": {
                        "mode": "demo",
                        "note": "No USB cutter detected. This is the first-pass local demo mode.",
                    },
                }
            )

            devices.append(
                {
                    "id": "simulated-ble-cutter",
                    "name": "Simulated BLE cutter",
                    "kind": "ble",
                    "status": "demo",
                    "details": {
                        "mode": "demo",
                        "note": "Bluetooth discovery can be enabled when a real device is connected.",
                    },
                }
            )

        return devices

    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        for device in self.scan():
            if device["id"] == device_id:
                return device
        return None
