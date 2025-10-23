import json
from pathlib import Path
from typing import List, Dict, Any

# Do not export PII/log-heavy doctypes
SENSITIVE = {
    "User",
    "Communication",
    "File",
    "Activity Log",
    "Access Log",
    "Email Queue",
    "Error Log",
    "Scheduled Job Log",
}


def plan_export(app_name: str, exclude_sensitive: bool = True) -> List[Dict[str, Any]]:
    here = Path(__file__).resolve().parent.parent
    app_cat = here / "export_catalog.json"
    cat = (
        json.loads(app_cat.read_text())
        if app_cat.exists()
        else {"core_fixtures": [], "domain": []}
    )
    items = cat.get("core_fixtures", []) + cat.get("domain", [])
    if exclude_sensitive:
        items = [i for i in items if i.get("doctype") not in SENSITIVE]
    return items
