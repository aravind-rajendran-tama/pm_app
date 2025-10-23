import frappe
from pm_app.pm_suite.import_engine.runner import run_import
from .exporter.runner import run_export


@frappe.whitelist()
def export_app_data(
    app: str, exclude_sensitive: int = 1, out_zip: str = "~/pm_bundle.zip"
):
    return run_export(
        target_app=app, out_zip=out_zip, exclude_sensitive=bool(int(exclude_sensitive))
    )


def import_app_data(export_path: str, validate_only: int = 1):
    return run_import(bundle_zip=export_path, validate_only=bool(int(validate_only)))
