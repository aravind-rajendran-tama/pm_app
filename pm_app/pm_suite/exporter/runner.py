import json, datetime, importlib, shutil, zipfile
from pathlib import Path
from typing import Dict, Any, Iterable
import frappe

from .planner import plan_export
from .writers import write_jsonl
from .schema import validate_manifest
from .checksums import sha256_file


def _get_app_version(app: str) -> str:
    try:
        mod = importlib.import_module(app)
        return getattr(mod, "__version__", "0.0.0")
    except Exception:
        return "0.0.0"


def _iter_docs(doctype: str) -> Iterable[Dict[str, Any]]:
    # fetch all doc names, then load full docs (child tables included)
    for name in frappe.get_all(doctype, pluck="name"):
        yield frappe.get_doc(doctype, name).as_dict(no_nulls=True)


def _build_manifest(out_dir: Path, target_app: str, items):
    m = {
        "app": target_app,
        "app_version": _get_app_version(target_app),
        "site": frappe.local.site,
        "frappe_version": frappe.__version__,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "items": [{"doctype": it["doctype"]} for it in items],
        "notes": "No PII exported by default",
        "checksums": {},
    }
    data_dir = out_dir / "data"
    if data_dir.exists():
        for p in sorted(data_dir.glob("*.jsonl")):
            m["checksums"][f"data/{p.name}"] = sha256_file(p)
    validate_manifest(m)
    (out_dir / "manifest.json").write_text(json.dumps(m, indent=2), encoding="utf-8")


def run_export(
    target_app: str, out_zip: str, exclude_sensitive: bool = True
) -> Dict[str, Any]:
    """
    Main entrypoint. Builds a zip with manifest.json and data/*.jsonl for the given app.
    """
    out_zip = Path(out_zip).expanduser().resolve()
    build_dir = out_zip.with_suffix("")  # temp folder alongside the zip
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    items = plan_export(target_app, exclude_sensitive)
    data_dir = build_dir / "data"

    for it in items:
        dt = it["doctype"]
        rows = list(_iter_docs(dt))
        write_jsonl(data_dir / f"{dt}.jsonl", rows)

    _build_manifest(build_dir, target_app, items)

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.write(build_dir / "manifest.json", arcname="manifest.json")
        if data_dir.exists():
            for p in sorted(data_dir.glob("*.jsonl")):
                z.write(p, arcname=f"data/{p.name}")

    return {"ok": True, "zip": str(out_zip)}
