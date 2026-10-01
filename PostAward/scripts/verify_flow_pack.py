import re
import zipfile

with zipfile.ZipFile("PostAward/app.msapp") as z:
    ds = z.read("References/DataSources.json").decode("utf-8", errors="replace")
    print("has PostAward-Excelexport:", "PostAward-Excelexport" in ds)
    for m in re.finditer(r'"Name": "[^"]*Excel[^"]*"', ds):
        print(m.group(0))
    for n in ["Src/Register.pa.yaml", "Src/Subcontract Detail.pa.yaml"]:
        t = z.read(n).decode("utf-8", errors="replace")
        for line in t.splitlines():
            if "Excelexport" in line or "Excel export" in line and ".Run" in line:
                print(n + ":", line.strip()[:100])
