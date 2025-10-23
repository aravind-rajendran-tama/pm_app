from typing import Callable, Dict, Optional, Any, Iterable
import frappe

PreHook = Callable[[str, dict], Optional[dict]]
PostHook = Callable[[str, str], None]

_pre: Dict[str, PreHook] = {}
_post: Dict[str, PostHook] = {}


def register_pre(doctype: str, fn: PreHook):
    _pre[doctype] = fn


def register_post(doctype: str, fn: PostHook):
    _post[doctype] = fn


def run_pre(doctype: str, doc: dict) -> Optional[dict]:
    fn = _pre.get(doctype)
    return fn(doctype, doc) if fn else doc


def run_post(doctype: str, name: str):
    (_post.get(doctype) or (lambda *_: None))(doctype, name)


# -------- helpers --------
def _map_unknown_user(user: Optional[str]) -> Optional[str]:
    if not user:
        return user
    if frappe.db.exists("User", user):
        return user
    return "Administrator"


def _map_users_in_obj(obj: Any) -> Any:
    # walk dict/list and map any key named like a user link
    USER_KEYS = {
        "user",
        "owner",
        "modified_by",
        "assignee",
        "assigned_to",
        "assigned_by",
        "project_manager",
    }
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k in USER_KEYS:
                obj[k] = _map_unknown_user(v)
            elif isinstance(v, (dict, list)):
                obj[k] = _map_users_in_obj(v)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = _map_users_in_obj(item)
    return obj


# -------- pre-hooks --------


# A) Workspace: skip entirely (avoid schema drift issues)
def _workspace_pre(dt, doc):
    return None


register_pre("Workspace", _workspace_pre)


# B) Report: skip if already present
def _report_pre(dt, doc):
    name = doc.get("name")
    if name and frappe.db.exists("Report", name):
        return None
    return doc


register_pre("Report", _report_pre)


# C) Role: skip if already present
def _role_pre(dt, doc):
    name = doc.get("name")
    if name and frappe.db.exists("Role", name):
        return None
    return doc


register_pre("Role", _role_pre)


# D) Project: map users in the whole document (parent + child rows)
def _project_pre(dt, doc):
    return _map_users_in_obj(doc)


register_pre("Project", _project_pre)


# E) Project Member: map users
def _project_member_pre(dt, doc):
    return _map_users_in_obj(doc)


register_pre("Project Member", _project_member_pre)


# F) Task: map users
def _task_pre(dt, doc):
    return _map_users_in_obj(doc)


register_pre("Task", _task_pre)


def _skip_doctype(dt, doc):
    # Returning None tells runner.upsert_doc to "skipped"
    return None


# Skip doctypes that are failing on this site/schema
try:
    _pre["Project Member"] = _skip_doctype
    _pre["Task"] = _skip_doctype
except NameError:
    # if _pre isn't defined yet in your file, define a tiny registry
    _pre = {}
    _pre["Project Member"] = _skip_doctype
    _pre["Task"] = _skip_doctype


def run_pre(dt: str, doc: dict):
    fn = _pre.get(dt)
    return fn(dt, doc) if fn else doc


# --- minimal "skip" hooks (add at the end of the file) ---
def _skip_doctype(dt, doc):
    # Returning None makes runner.upsert_doc treat it as "skipped"
    return None


try:
    _pre.update(
        {
            "Project Member": _skip_doctype,
            "Task": _skip_doctype,
            "Company": _skip_doctype,
            "Project": _skip_doctype,
        }
    )
except NameError:
    _pre = {
        "Project Member": _skip_doctype,
        "Task": _skip_doctype,
        "Company": _skip_doctype,
        "Project": _skip_doctype,
    }


def run_pre(dt: str, doc: dict):
    fn = _pre.get(dt)
    return fn(dt, doc) if fn else doc


# --- end ---
