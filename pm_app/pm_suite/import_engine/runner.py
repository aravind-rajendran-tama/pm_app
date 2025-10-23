import json, zipfile, tempfile, datetime, os
from pathlib import Path
import frappe
from .prechecks import run_prechecks
from .planner import plan_import
from .handlers import run_pre


def iter_jsonl(path: Path):
    with path.open("rb") as f:
        for line in f:
            yield json.loads(line)


def _log_dir():
    p = Path(frappe.get_site_path("private")) / "files" / "import_logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _write_log(payload):
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = _log_dir() / f"import_{ts}.json"
    path.write_text(json.dumps(payload, indent=2))
    return str(path)


def upsert_doc(dt: str, doc: dict):
    try:
        doc = run_pre(dt, doc)
        if doc is None:
            return ("skipped", None)

        name = doc.get("name")
        if name and frappe.db.exists(dt, name):
            d = frappe.get_doc(dt, name)
            d.update(doc)
            d.flags.ignore_permissions = True
            d.flags.ignore_version = True
            d.save()
            return ("updated", d.name)

        d = frappe.get_doc(doc)
        d.flags.ignore_permissions = True
        d.flags.ignore_version = True
        d.insert()
        return ("inserted", d.name)
    except Exception as e:
        return ("error", str(e))


def run_import(bundle_zip: str, validate_only: bool = True):
    tmpdir = Path(tempfile.mkdtemp(prefix="bundle_import_"))
    with zipfile.ZipFile(os.path.expanduser(bundle_zip), "r") as z:
        z.extractall(tmpdir)

    manifest = json.loads((tmpdir / "manifest.json").read_text())
    run_prechecks(manifest, validate_only=validate_only)
    order = plan_import(manifest)

    # pre-count for nice planned totals
    planned_counts = {}
    for dt in order:
        p = tmpdir / "data" / f"{dt}.jsonl"
        planned_counts[dt] = sum(1 for _ in iter_jsonl(p)) if p.exists() else 0

    result = {
        "mode": "validate" if validate_only else "apply",
        "summary": {},
        "errors": [],
        "manifest": manifest,
        "log_path": None,
    }

    if validate_only:
        for dt in order:
            result["summary"][dt] = {
                "planned": planned_counts.get(dt, 0),
                "inserted": 0,
                "updated": 0,
            }
        result["log_path"] = _write_log(result)
        return result

    # apply mode – two passes
    for pass_no in (1, 2):
        for dt in order:
            p = tmpdir / "data" / f"{dt}.jsonl"
            if not p.exists():
                continue
            ins = upd = 0
            retry = []
            for row in iter_jsonl(p):
                status, info = upsert_doc(dt, row)
                if status == "inserted":
                    ins += 1
                elif status == "updated":
                    upd += 1
                elif status == "error":
                    retry.append(
                        {"doctype": dt, "name": row.get("name"), "error": info}
                    )
                # skipped: ignore
            if pass_no == 2 and retry:
                result["errors"].extend(retry)
            s = result["summary"].setdefault(
                dt, {"planned": planned_counts.get(dt, 0), "inserted": 0, "updated": 0}
            )
            s["inserted"] += ins
            s["updated"] += upd

    try:
        frappe.clear_cache()
    except Exception:
        pass

    result["mode"] = "apply"
    result["log_path"] = _write_log(result)
    return result
