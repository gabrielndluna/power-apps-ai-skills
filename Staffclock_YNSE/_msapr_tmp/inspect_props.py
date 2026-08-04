import json, re

with open("Staffclock_YNSE/_msapr_tmp/Public_Holidays_meta.json", encoding="utf-8") as f:
    s = json.dumps(json.load(f))

# property keys from swagger-like schema
props = re.findall(r'"([A-Za-z0-9_ /]+)":\{"type":"[^"]+","title":"([^"]+)"', s)
print("Public_Holidays props:")
for a, b in props:
    print(f"  {a!r} -> {b!r}")

with open("Staffclock_YNSE/_msapr_tmp/Approvers_meta.json", encoding="utf-8") as f:
    s2 = json.dumps(json.load(f))
props2 = re.findall(r'"([A-Za-z0-9_ /]+)":\{"type":"[^"]+","title":"([^"]+)"', s2)
print("Approvers props:")
for a, b in props2:
    print(f"  {a!r} -> {b!r}")
