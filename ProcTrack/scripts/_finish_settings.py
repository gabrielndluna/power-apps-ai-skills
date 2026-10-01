import json
import shutil
import tempfile
import zipfile
from pathlib import Path

SRC = Path("src/Src")

# Finish Welcome OnVisible if needed
wpath = SRC / "Welcome screen.pa.yaml"
w = wpath.read_text(encoding="utf-8")
if "ProjectID = varSelectedProject.projectid" not in w:
    old_vis_filter = """                Filter(
                    'ProcTrack - Packages',
                    projectidentifier = varSelectedProject.projectidentifier
                )"""
    new_vis_filter = """                Filter(
                    'ProcTrack - Packages',
                    ProjectID = varSelectedProject.projectid || projectidentifier = varSelectedProject.projectidentifier
                );
                Set(
                    varCanEditCurrentProject,
                    varIsAdmin || !IsBlank(LookUp(Split(Coalesce(varUserPerm.Edit_Projects, ""), ";"), Trim(Value) = varSelectedProject.projectid))
                )"""
    if old_vis_filter in w:
        wpath.write_text(w.replace(old_vis_filter, new_vis_filter, 1), encoding="utf-8", newline="\n")
        print("Welcome OnVisible updated")
    else:
        print("WARNING Welcome OnVisible not patched")
else:
    print("Welcome OnVisible OK")

# Patch msapr datasources
msapr = next(Path("src").glob("*.msapr"))
tmp = Path(tempfile.mkdtemp())
with zipfile.ZipFile(msapr, "r") as z:
    z.extractall(tmp)
ds_path = tmp / "msapp" / "References" / "DataSources.json"
data = json.loads(ds_path.read_text(encoding="utf-8"))
sources = data["DataSources"] if isinstance(data, dict) else data
for ds in sources:
    nm = ds.get("ConnectedDataSourceInfoNameMapping")
    if not isinstance(nm, dict):
        continue
    if ds.get("Name") == "ProcTrack - Permissions":
        nm["IsAdmin"] = "IsAdmin"
        nm["Edit_Projects"] = "Edit_Projects"
        nm["View_Projects"] = "View_Projects"
        print("permissions mapping updated")
    elif ds.get("Name") == "ProcTrack - Projects":
        nm["projectid"] = "projectid"
        print("projects mapping updated")
    elif ds.get("Name") == "ProcTrack - Packages":
        nm["ProjectID"] = "ProjectID"
        print("packages mapping updated")
ds_path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")

# Ensure AddPicture template exists for Settings
tpl_path = tmp / "msapp" / "References" / "Templates.json"
raw = tpl_path.read_text(encoding="utf-8")
print("AddPicture in templates:", "AddPicture" in raw)

out = msapr.with_suffix(".msapr.new")
with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for f in tmp.rglob("*"):
        if f.is_file():
            z.write(f, f.relative_to(tmp).as_posix())
out.replace(msapr)
shutil.rmtree(tmp, ignore_errors=True)
print("msapr patched")

for name in [
    "Welcome screen.pa.yaml",
    "Package Details.pa.yaml",
    "Create New Package.pa.yaml",
    "Project Dashboard.pa.yaml",
    "Settings.pa.yaml",
    "App.pa.yaml",
    "_EditorState.pa.yaml",
]:
    t = (SRC / name).read_text(encoding="utf-8")
    flags = []
    if "Edit_allowed" in t:
        flags.append("Edit_allowed")
    if "colUserPermissions" in t:
        flags.append("colUserPermissions")
    if name == "Settings.pa.yaml":
        flags.append("tabs=" + ",".join(
            x for x in ["users", "projects", "columns"] if f'"{x}"' in t or f"= \"{x}\"" in t or f'"{x}"' in t
        ))
    print(f"{name}: {'OK' if not any(f.startswith('Edit') or f.startswith('colU') for f in flags) else flags} | Navigate={('Navigate(Settings' in t)} | ProjectID refs={t.count('ProjectID')}")

print("PostAward Edit_Projects", "Edit_Projects" in Path("../PostAward/src/Src/App.pa.yaml").read_text(encoding="utf-8"))
