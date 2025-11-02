from typing import Optional, Dict, Any

def run_import(export_path: str, site: Optional[str] = None, validate_only: int = 1) -> Dict[str, Any]:
    """
    v2 stub: implement real import here.
    Return a dict (JSON-serializable) so bench execute prints cleanly.
    """
    return {
        "ok": False,
        "stage": "importer_v2",
        "msg": "Importer v2 not implemented yet. This is a safe placeholder.",
        "export_path": export_path,
        "site": site,
        "validate_only": int(validate_only),
    }
