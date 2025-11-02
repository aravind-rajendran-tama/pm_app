from typing import Optional
from pm_app.pm_suite.dataflows.exporter_v2.runner import run_export
from pm_app.pm_suite.dataflows.importer_v2.runner import run_import

def export_app_data(app: str, exclude_sensitive: int = 1, out_zip: Optional[str] = None):
    """
    CLI entry (used with: bench execute pm_app.pm_suite.cli_export.export_app_data --kwargs ...)
    Routes to exporter_v2.runner.run_export
    """
    return run_export(app=app, exclude_sensitive=exclude_sensitive, out_zip=out_zip)

def import_app_data(export_path: str, site: Optional[str] = None, validate_only: int = 1):
    """
    CLI entry (used with: bench execute pm_app.pm_suite.cli_export.import_app_data --kwargs ...)
    Routes to importer_v2.runner.run_import
    """
    return run_import(export_path=export_path, site=site, validate_only=validate_only)
