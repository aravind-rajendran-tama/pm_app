from typing import Optional, Dict, Any

def run_export(app: str, exclude_sensitive: int = 1, out_zip: Optional[str] = None) -> Dict[str, Any]:
    """
    v2 stub: implement real export here.
    Keep signature stable so CLI keeps working.
    """
    return {
        "ok": False,
        "stage": "exporter_v2",
        "msg": "Exporter v2 not implemented yet. This is a safe placeholder.",
        "app": app,
        "exclude_sensitive": int(exclude_sensitive),
        "out_zip": out_zip,
    }
