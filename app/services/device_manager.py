from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    import usb  # type: ignore
except Exception:  # pragma: no cover
    usb = None


SILHOUETTE_USB_IDS = {
    (0x0E21, 0x0902),
    (0x0E21, 0x0901),
    (0x0E21, 0x0900),
    (0x0E21, 0x0903),
    (0x0E21, 0x0904),
    (0x0E21, 0x0101),
    (0x0E21, 0x0100),
    (0x0E21, 0x0102),
    (0x0E21, 0x0103),
    (0x0E21, 0x0111),
    (0x0E21, 0x0112),
    (0x0E21, 0x0113),
    (0x0E21, 0x0120),
    (0x0E21, 0x0301),
    (0x0E21, 0x0302),
    (0x0E21, 0x0303),
    (0x0E21, 0x0304),
    (0x0E21, 0x0305),
    (0x0E21, 0x0400),
    (0x0E21, 0x0401),
    (0x0E21, 0x0402),
    (0x0E21, 0x0403),
    (0x1A40, 0x0101),
    (0x1A40, 0x0102),
    (0x1A40, 0x0103),
    (0x1A40, 0x0104),
}


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

                    if (int(vendor_id), int(product_id)) not in SILHOUETTE_USB_IDS:
                        continue

                    devices.append(
                        {
                            "id": f"usb-{vendor_id:04x}-{product_id:04x}",
                            "name": f"Silhouette USB device {vendor_id:04x}:{product_id:04x}",
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
                    "name": "Simulated Silhouette cutter",
                    "kind": "usb",
                    "status": "demo",
                    "details": {
                        "mode": "demo",
                        "note": "No recognized Silhouette cutter found. Demo mode is active.",
                    },
                }
            )

        return devices

    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        for device in self.scan():
            if device["id"] == device_id:
                return device
        return None
