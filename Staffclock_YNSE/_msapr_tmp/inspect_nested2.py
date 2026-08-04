import json

with open("Staffclock_YNSE/_msapr_tmp/Public_Holidays_meta.json", encoding="utf-8") as f:
    meta = json.load(f)

key = next(iter(meta.keys()))
entity = json.loads(meta[key]) if isinstance(meta[key], str) else meta[key]
print("entity type", type(entity), list(entity.keys())[:20] if isinstance(entity, dict) else "")


def walk(o, path=""):
    if isinstance(o, dict):
        if "properties" in o and isinstance(o["properties"], dict):
            print("PROPERTIES at", path)
            for pk, pv in o["properties"].items():
                if isinstance(pv, dict):
                    print(f"  {pk}: type={pv.get('type')} title={pv.get('title')}")
        for kk, vv in o.items():
            walk(vv, path + "/" + str(kk))
    elif isinstance(o, list):
        for i, vv in enumerate(o[:20]):
            walk(vv, path + f"[{i}]")
    elif isinstance(o, str) and o.startswith("{"):
        try:
            walk(json.loads(o), path + "/(json)")
        except Exception:
            pass


walk(entity)

with open("Staffclock_YNSE/_msapr_tmp/Approvers_meta.json", encoding="utf-8") as f:
    meta2 = json.load(f)
key2 = next(iter(meta2.keys()))
entity2 = json.loads(meta2[key2]) if isinstance(meta2[key2], str) else meta2[key2]
print("\n=== APPROVERS ===")
walk(entity2)
