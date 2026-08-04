import json

with open("Staffclock_YNSE/_msapr_tmp/Public_Holidays_meta.json", encoding="utf-8") as f:
    meta = json.load(f)

key = next(iter(meta.keys()))
entity = meta[key]
print("entity keys", entity.keys() if isinstance(entity, dict) else type(entity))

# often WadlMetadata or CdpSchema is a string
for k, v in entity.items() if isinstance(entity, dict) else []:
    print(k, type(v).__name__, (str(v)[:120] if not isinstance(v, (dict, list)) else ""))
    if isinstance(v, str) and ("Projects" in v or "Date" in v):
        try:
            inner = json.loads(v)
            print(" parsed", k, type(inner))
            # walk for properties
            def walk(o, path=""):
                if isinstance(o, dict):
                    if "properties" in o and isinstance(o["properties"], dict):
                        print("PROPERTIES at", path)
                        for pk, pv in o["properties"].items():
                            title = pv.get("title") if isinstance(pv, dict) else None
                            typ = pv.get("type") if isinstance(pv, dict) else None
                            print(f"  {pk}: type={typ} title={title}")
                    for kk, vv in o.items():
                        walk(vv, path + "/" + kk)
                elif isinstance(o, list):
                    for i, vv in enumerate(o[:5]):
                        walk(vv, path + f"[{i}]")

            walk(inner)
        except Exception as e:
            print("parse fail", e)
