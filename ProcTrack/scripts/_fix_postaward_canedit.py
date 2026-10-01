import re
from pathlib import Path

NEW = (
    'varIsAdmin || !IsBlank(LookUp(Split(Coalesce(varUserPerm.Edit_Projects, ""), ";"), '
    "Trim(Value) = varSelectedProject.projectid))"
)
pat = re.compile(
    r'!IsBlank\(\s*LookUp\(\s*colUserPermissions,\s*'
    r'Project = varSelectedProject\.projectidentifier && Edit_allowed = "yes"\s*\)\s*\)',
    re.S,
)
for rel in ["Home.pa.yaml", "Register.pa.yaml"]:
    p = Path("../PostAward/src/Src") / rel
    t = p.read_text(encoding="utf-8")
    t2, n = pat.subn(NEW, t)
    print(rel, "replacements", n)
    if n == 0:
        raise SystemExit(f"no matches in {rel}")
    p.write_text(t2, encoding="utf-8", newline="\n")
