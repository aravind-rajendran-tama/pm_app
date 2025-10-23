import frappe


class ImportErrorPrecheck(Exception):
    pass


def is_site_read_only_from_conf() -> bool:
    conf = frappe.get_conf() or {}
    # trust explicit config flags only
    return bool(conf.get("read_only")) or bool(conf.get("maintenance_mode"))


def ensure_db():
    try:
        frappe.db.sql("select 1")
    except Exception as e:
        raise ImportErrorPrecheck(f"Database not reachable: {e}")


def ensure_site_is_writable():
    # block writes only if configs explicitly say so
    if is_site_read_only_from_conf():
        raise ImportErrorPrecheck(
            "Site is read-only (or in maintenance_mode); cannot import."
        )


def ensure_manifest_ok(manifest: dict):
    for key in ("app", "frappe_version", "items"):
        if key not in manifest:
            raise ImportErrorPrecheck(f"manifest.json missing key: {key}")
    if not manifest.get("items"):
        raise ImportErrorPrecheck("manifest.items must be a non-empty list")


def ensure_app_installed(app: str):
    if app not in frappe.get_installed_apps():
        raise ImportErrorPrecheck(f"Required app not installed: {app}")


def run_prechecks(manifest: dict, *, validate_only: bool = False):
    ensure_db()
    # allow dry-run anywhere; only block writes when configs demand it
    if not validate_only:
        ensure_site_is_writable()
    ensure_manifest_ok(manifest)
    ensure_app_installed(manifest["app"])
