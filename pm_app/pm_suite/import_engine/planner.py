def plan_import(manifest: dict):
    # preserve manifest order for now (export already planned dependencies)
    return [i["doctype"] for i in manifest.get("items", [])]
