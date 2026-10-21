"""Build Permissions + Packages seed CSVs for the new projectid model."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ProcTrack" / "seed_data"
OUT.mkdir(exist_ok=True)

with open(ROOT / "PostAward" / "ProcTrack - Projects.csv", encoding="utf-8-sig", newline="") as f:
    projects = list(csv.DictReader(f))

id_by_ident = {
    (p.get("projectidentifier") or "").strip(): (p.get("projectid") or "").strip()
    for p in projects
}

# Packages: add ProjectID from projectidentifier
src = ROOT / "PostAward" / "ProcTrack - Packages.csv"
with open(src, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    cols = list(reader.fieldnames or [])
    rows = list(reader)

if "ProjectID" not in cols:
    if "projectidentifier" in cols:
        i = cols.index("projectidentifier") + 1
        cols = cols[:i] + ["ProjectID"] + cols[i:]
    else:
        cols = ["ProjectID"] + cols

missing: dict[str, int] = {}
filled = 0
for r in rows:
    ident = (r.get("projectidentifier") or "").strip()
    pid = id_by_ident.get(ident, "")
    r["ProjectID"] = pid
    if pid:
        filled += 1
    else:
        missing[ident] = missing.get(ident, 0) + 1

pkg_out = OUT / "ProcTrack - Packages.csv"
with open(pkg_out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)

# Permissions: collapse old one-row-per-project export into one row per user
perm_src = Path.home() / "Downloads" / "ProcTrack - Permissions.csv"
if not perm_src.exists():
    raise SystemExit(f"Missing old Permissions export: {perm_src}")

with open(perm_src, encoding="utf-8-sig", newline="") as f:
    old_perms = list(csv.DictReader(f))

users: dict[str, dict] = defaultdict(
    lambda: {"Name": "", "Entra_ID": "", "IsAdmin": False, "edit": set(), "view": set()}
)
unmapped: list[tuple[str, str]] = []
for r in old_perms:
    email = (r.get("Title") or "").strip().lower()
    if not email:
        continue
    u = users[email]
    name = (r.get("Name") or "").strip()
    if name:
        u["Name"] = name
    entra = (r.get("Entra_ID") or "").strip()
    if entra and not u["Entra_ID"]:
        u["Entra_ID"] = entra
    if (r.get("IsAdmin") or "").strip().lower() in ("true", "yes", "1"):
        u["IsAdmin"] = True
    ident = (r.get("Project") or "").strip()
    pid = id_by_ident.get(ident, "")
    if ident and not pid:
        unmapped.append((email, ident))
        continue
    if not pid:
        continue
    if (r.get("Edit_allowed") or "").strip().lower() in ("yes", "true", "1"):
        u["edit"].add(pid)
        u["view"].discard(pid)
    elif pid not in u["edit"]:
        u["view"].add(pid)

perm_cols = ["Title", "Name", "IsAdmin", "Entra_ID", "Edit_Projects", "View_Projects"]
perm_rows = []
for email, u in sorted(users.items()):
    edit = sorted(u["edit"])
    view = sorted(u["view"] - u["edit"])
    perm_rows.append(
        {
            "Title": email,
            "Name": u["Name"],
            "IsAdmin": "Yes" if u["IsAdmin"] else "No",
            "Entra_ID": u["Entra_ID"],
            "Edit_Projects": ";".join(edit),
            "View_Projects": ";".join(view),
        }
    )

perm_out = OUT / "ProcTrack - Permissions.csv"
with open(perm_out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=perm_cols)
    w.writeheader()
    w.writerows(perm_rows)

lookup_lines = "\n".join(
    f"- `{p.get('projectidentifier')}` → `{p.get('projectid')}` ({p.get('projectname')})"
    for p in projects
)

readme = OUT / "README.md"
readme.write_text(
    f"""# ProcTrack seed data (new permission model)

## SharePoint columns

### ProcTrack - Permissions (1 row per user)

| Column | Type | Notes |
|---|---|---|
| Title | Single line text | email lowercase, unique |
| Name | Single line text | display name |
| IsAdmin | Yes/No | manage Users + Projects |
| Entra_ID | Single line text | Azure AD object id (optional; app can fill) |
| Edit_Projects | Multiple lines of text | `;`-separated **projectid** GUIDs |
| View_Projects | Multiple lines of text | `;`-separated **projectid** GUIDs |

Old columns to stop using: `Project`, `Edit_allowed` (and any one-row-per-project layout).

### ProcTrack - Packages

| Column | Type | Notes |
|---|---|---|
| ProjectID | Single line text | = Projects.projectid (GUID) |
| projectidentifier | text | keep for display / legacy |

## How to load

1. Projects already has `projectid` (done).
2. Packages: add `ProjectID` if missing → import/update from `ProcTrack - Packages.csv`.
3. Permissions: set columns above → replace sample emails in `ProcTrack - Permissions.csv` → import (1 row per user). Use **projectid** GUIDs in Edit/View, not A02180.
4. Studio: refresh SharePoint connections for Permissions + Packages.

## projectid lookup

{lookup_lines}

## Generated

- Packages: {filled}/{len(rows)} rows got ProjectID
- Unmapped package identifiers: {missing or "none"}
""",
    encoding="utf-8",
)

print("packages:", pkg_out, f"filled {filled}/{len(rows)}", "missing", missing)
print("permissions:", perm_out)
print("readme:", readme)
