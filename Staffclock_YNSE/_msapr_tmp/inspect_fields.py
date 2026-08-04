import json, re

for name in ("Public_Holidays", "Approvers"):
    with open(f"Staffclock_YNSE/_msapr_tmp/{name}_meta.json", encoding="utf-8") as f:
        meta = json.load(f)
    s = json.dumps(meta)
    # SharePoint CDS often uses ApiName / Title style
    for pat in [
        r'"ApiName"\s*:\s*"([^"]+)"',
        r'"Name"\s*:\s*"([^"]+)"',
        r'"DisplayName"\s*:\s*"([^"]+)"',
        r'"Title"\s*:\s*"([^"]+)"',
    ]:
        hits = sorted(set(re.findall(pat, s)))
        print(name, pat, hits[:40])
    # print a small sample around Projects
    idx = s.find("Projects")
    print(name, "Projects context:", s[max(0, idx - 80) : idx + 120] if idx >= 0 else "none")
    idx = s.find('"Date"')
    print(name, "Date context:", s[max(0, idx - 80) : idx + 120] if idx >= 0 else "none")
    idx = s.lower().find("project")
    print(name, "project context:", s[max(0, idx - 80) : idx + 160] if idx >= 0 else "none")
