import re
import zipfile
from pathlib import Path

p = Path(r"PostAward/PostAward.msapp")
print("size", p.stat().st_size)
with zipfile.ZipFile(p) as z:
    for n in z.namelist():
        data = z.read(n)
        interesting = (
            b"PowerAppV2" in data
            or b"filelink" in data
            or b"Excel export" in data
            or b"Excel export" in data
            or (b"workflow" in data.lower() and b"ParseJSON" in data)
        )
        if not interesting:
            continue
        if not any(
            x in n
            for x in ("DataSource", "Properties", "Controls", "Src/", ".yaml", ".json")
        ):
            continue
        print("===", n)
        t = data.decode("utf-8", errors="replace")
        for pat in [
            r"PowerAppV2.{0,160}",
            r"PostAward.{0,60}[Ee]xcel.{0,60}",
            r"workflowDisplayName.{0,160}",
            r"['\"]Name['\"]\s*:\s*['\"][^'\"]*Excel[^'\"]*['\"]",
            r"['\"]Name['\"]\s*:\s*['\"]PowerAppV2[^'\"]*['\"]",
        ]:
            for m in re.finditer(pat, t):
                print(" ", m.group(0)[:220])
