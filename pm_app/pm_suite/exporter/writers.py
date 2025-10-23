import json
from pathlib import Path
from typing import Iterable, Dict, Any
from datetime import datetime, date, time


def _json_default(o):
    # make datetime/date/time JSON-safe
    if isinstance(o, (datetime, date, time)):
        return o.isoformat()
    # last resort: string
    return str(o)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, default=_json_default) + "\n")
