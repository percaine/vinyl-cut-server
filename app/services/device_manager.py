from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    import usb  # type: ignore
except Exception:  # pragma: no cover
    usb = None


# Complete list of all Silhouette-compatible USB devices from the inkscape-silhouette project
# Extracted from silhouette-udev.rules and sendto_silhouette.inx
SILHOUETTE_USB_DEVICES = {
    # Vendor 0x3844: Silhouette Cameo 5 Alpha series (newer devices)
    (0x3844, 0x0001): "Silhouette Cameo 5 Alpha",
    (0x3844, 0x0002): "Silhouette Cameo 5 Alpha Plus",
    
    # Vendor 0x0B4D: Silhouette / Graphtec main range
    (0x0B4D, 0x1121): "Silhouette Cameo",
    (0x0B4D, 0x112B): "Silhouette Cameo 2",
    (0x0B4D, 0x112F): "Silhouette Cameo 3",
    (0x0B4D, 0x1137): "Silhouette Cameo 4",
    (0x0B4D, 0x1138): "Silhouette Cameo 4 Plus",
    (0x0B4D, 0x1139): "Silhouette Cameo 4 Pro",
    (0x0B4D, 0x1140): "Silhouette Cameo 5",
    (0x0B4D, 0x1146): "Silhouette Cameo Pro MK-II",
    
    # Portrait series
    (0x0B4D, 0x1123): "Silhouette Portrait",
    (0x0B4D, 0x1132): "Silhouette Portrait 2",
    (0x0B4D, 0x113A): "Silhouette Portrait 3",
    (0x0B4D, 0x113F): "Silhouette Portrait 4",
    
    # SD series
    (0x0B4D, 0x111C): "Silhouette SD-1",
    (0x0B4D, 0x111D): "Silhouette SD-2",
    
    # Craft Robo (compatible cutters)
    (0x0B4D, 0x110A): "Craft Robo CC200-20",
    (0x0B4D, 0x111A): "Craft Robo CC300-20",
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

                    key = (int(vendor_id), int(product_id))
                    if key not in SILHOUETTE_USB_DEVICES:
                        continue

                    device_name = SILHOUETTE_USB_DEVICES[key]
                    devices.append(
                        {
                            "id": f"usb-{vendor_id:04x}-{product_id:04x}",
                            "name": device_name,
                            "kind": "usb",
                            "status": "ready",
                            "details": {
                                "vendor_id": vendor_id,
                                "product_id": product_id,
                                "model": device_name,
                            },
                        }
                    )
            except Exception:
                pass

        if not devices:
            devices.append(
                {
                    "id": "simulated-usb-cutter",
                    "name": "Simulated Silhouette Cutter (Demo)",
                    "kind": "usb",
                    "status": "demo",
                    "details": {
                        "mode": "demo",
                        "note": "No real Silhouette cutter detected. Running in simulation mode. Supports: Cameo, Cameo 2-5, Portrait 1-4, SD-1/2, Craft Robo CC200/300.",
                    },
                }
            )

        return devices

    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        for device in self.scan():
            if device["id"] == device_id:
                return device
        return None
