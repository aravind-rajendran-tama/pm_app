from typing import Dict, Any

REQUIRED_KEYS = ["app", "app_version", "site", "frappe_version", "timestamp", "items"]


def validate_manifest(m: Dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in m]
    if missing:
        raise ValueError(f"Manifest missing keys: {missing}")
    if not isinstance(m["items"], list):
        raise TypeError("Manifest 'items' must be a list")
    for it in m["items"]:
        if not isinstance(it, dict) or "doctype" not in it:
            raise TypeError("Each manifest item must be an object with 'doctype'")
    if "checksums" in m and not isinstance(m["checksums"], dict):
        raise TypeError("Manifest 'checksums' must be a dict if present")
