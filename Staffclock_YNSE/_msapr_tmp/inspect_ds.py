import zipfile, json, re

p = r"Staffclock_YNSE/_msapr_tmp/Staffclock - YNSE  - DEV.msapr"
z = zipfile.ZipFile(p)
ds = json.loads(z.read("msapp/References/DataSources.json"))["DataSources"]
for item in ds:
    if item.get("Name") in ("Public_Holidays", "Approvers"):
        meta = item.get("DataEntityMetadataJson")
        if isinstance(meta, str):
            meta = json.loads(meta)
        print("====", item["Name"], type(meta))
        if isinstance(meta, dict):
            print("keys", list(meta.keys())[:30])
        s = json.dumps(meta)
        names = sorted(set(re.findall(r'"(?:Name|LogicalName|DisplayName)"\s*:\s*"([^"]+)"', s)))
        for n in names:
            if any(
                x in n.lower()
                for x in ("project", "date", "title", "email", "name", "clean")
            ):
                print(" ", n)
        out = f"Staffclock_YNSE/_msapr_tmp/{item['Name']}_meta.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print("wrote", out)
