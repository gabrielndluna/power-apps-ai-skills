"""Wire Settings navigation, permission joins, remove column overlay."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "Src"

CAN_EDIT = (
    "varIsAdmin || !IsBlank(LookUp(Split(Coalesce(varUserPerm.Edit_Projects, \"\"), \";\"), "
    "Trim(Value) = Self.Selected.projectid))"
)
CAN_EDIT_THIS = (
    "varIsAdmin || !IsBlank(LookUp(Split(Coalesce(varUserPerm.Edit_Projects, \"\"), \";\"), "
    "Trim(Value) = ThisItem.projectid))"
)
CAN_EDIT_VAR = (
    "varIsAdmin || !IsBlank(LookUp(Split(Coalesce(varUserPerm.Edit_Projects, \"\"), \";\"), "
    "Trim(Value) = varSelectedProject.projectid))"
)

PKG_FILTER_SELF = (
    "ProjectID = Self.Selected.projectid || projectidentifier = Self.Selected.projectidentifier"
)
PKG_FILTER_VAR = (
    "ProjectID = varSelectedProject.projectid || projectidentifier = varSelectedProject.projectidentifier"
)
PKG_FILTER_THIS = (
    "ProjectID = ThisItem.projectid || projectidentifier = ThisItem.projectidentifier"
)

PROJECT_ONCHANGE = f'''=If(
    !IsBlank(Self.Selected),
    Set(varSelectedProject, Self.Selected);
    ClearCollect(
        colProjectPackages,
        Filter(
            'ProcTrack - Packages',
            {PKG_FILTER_SELF}
        )
    );
    Set(
        varCanEditCurrentProject,
        {CAN_EDIT}
    )
)'''

DASH_ONVISIBLE = f'''=Set(varPackageFilter, "all");
Set(varSelectedProject, Blank());
Set(varUserPerm, LookUp('ProcTrack - Permissions', Title = varCurrentUserEmail));
Set(varIsAdmin, Coalesce(varUserPerm.IsAdmin, false));
ClearCollect(
    colMyProjectIds,
    Distinct(
        Filter(
            Split(
                Coalesce(varUserPerm.Edit_Projects, "") & ";" & Coalesce(varUserPerm.View_Projects, ""),
                ";"
            ),
            !IsBlank(Trim(ThisRecord.Value))
        ),
        Value
    )
);
Clear(colPermittedProjects);
ForAll(
    colMyProjectIds As idRow,
    Collect(
        colPermittedProjects,
        LookUp('ProcTrack - Projects', projectid = Trim(idRow.Value))
    )
);
ClearCollect(
    colPermittedProjects,
    Filter(colPermittedProjects, !IsBlank(projectid))
);
Clear(colPermittedPackages);
ForAll(
    colPermittedProjects As p,
    Collect(
        colPermittedPackages,
        Filter(
            'ProcTrack - Packages',
            ProjectID = p.projectid || projectidentifier = p.projectidentifier
        )
    )
)'''

WELCOME_ONVISIBLE = f'''=Set(varPackageFilter, "all");
If(
    !IsBlank(varSelectedProject),
    ClearCollect(
        colProjectPackages,
        Filter(
            'ProcTrack - Packages',
            {PKG_FILTER_VAR}
        )
    );
    Set(
        varCanEditCurrentProject,
        {CAN_EDIT_VAR}
    )
)'''

OPEN_PROJECT = f'''=Set(varSelectedProject, ThisItem);
ClearCollect(
    colProjectPackages,
    Filter(
        colPermittedPackages,
        {PKG_FILTER_THIS}
    )
);
Set(
    varCanEditCurrentProject,
    {CAN_EDIT_THIS}
);
Navigate('Welcome screen', ScreenTransition.Fade)'''


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def update_editor_state() -> None:
    path = SRC / "_EditorState.pa.yaml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"  ScreensOrder:\n(?:    - .+\n)+",
        "  ScreensOrder:\n"
        "    - Project Dashboard\n"
        "    - Welcome screen\n"
        "    - Create New Package\n"
        "    - Package Details\n"
        "    - Settings\n",
        text,
        count=1,
    )
    write(path, text)
    print("updated _EditorState")


def update_welcome() -> None:
    path = SRC / "Welcome screen.pa.yaml"
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r"(  Welcome screen:\n    Properties:\n      Fill: =RGBA\(214, 221, 224, 1\)\n      LoadingSpinnerColor: =RGBA\(0, 120, 212, 1\)\n      OnVisible: \|-\n)(?:        .*\n)+",
        r"\1" + "".join("        " + line + "\n" for line in WELCOME_ONVISIBLE.splitlines()),
        text,
        count=1,
    )

    text = text.replace(
        "OnSelect: =Set(varShowSettings, true)",
        "OnSelect: =Navigate(Settings, ScreenTransition.Fade)",
    )

    # Replace project combobox OnChange (quoted formula)
    text = re.sub(
        r'OnChange: "=If\\(\\r\\n    !IsBlank\\(Self\\.Selected\\),.*?\\r\\n\\)"',
        "OnChange: |-\n" + "".join("                                      " + line + "\n" for line in PROJECT_ONCHANGE.splitlines()),
        text,
        count=1,
        flags=re.S,
    )
    # Also handle non-escaped variant if present
    text = re.sub(
        r"OnChange: \"=If\(\n    !IsBlank\(Self\.Selected\),.*?\n\)\"",
        "OnChange: |-\n" + "".join("                                      " + line + "\n" for line in PROJECT_ONCHANGE.splitlines()),
        text,
        count=1,
        flags=re.S,
    )

    # Remove column-settings overlay starting at - Container29:
    marker = "      - Container29:"
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit("Welcome Container29 overlay not found")
    # overlay is last top-level child under Welcome screen Children; trim to end before final structure
    # Find previous sibling end - everything from Container29 to EOF of children (file end after overlay)
    # Keep everything before Container29, ensure file ends cleanly
    head = text[:idx].rstrip() + "\n"
    write(path, head)
    print("updated Welcome screen (overlay removed)")


def update_package_details() -> None:
    path = SRC / "Package Details.pa.yaml"
    text = path.read_text(encoding="utf-8")
    # Quoted OnChange with \n
    new_on = "OnChange: |-\n" + "".join(
        "                                      " + line + "\n" for line in PROJECT_ONCHANGE.splitlines()
    )
    text2, n = re.subn(
        r'OnChange: "=If\\n    !IsBlank\\(Self\\.Selected\\),.*?\\n\)"',
        new_on.rstrip(),
        text,
        count=1,
        flags=re.S,
    )
    if n == 0:
        text2, n = re.subn(
            r"OnChange: \"=If\(\n    !IsBlank\(Self\.Selected\),.*?\n\)\"",
            new_on.rstrip(),
            text,
            count=1,
            flags=re.S,
        )
    if n == 0:
        raise SystemExit("Package Details project OnChange not found")
    write(path, text2)
    print("updated Package Details")


def update_create_new() -> None:
    path = SRC / "Create New Package.pa.yaml"
    text = path.read_text(encoding="utf-8")
    new_on = "OnChange: |-\n" + "".join(
        "                                      " + line + "\n" for line in PROJECT_ONCHANGE.splitlines()
    )
    text2, n = re.subn(
        r'OnChange: "=If\\n    !IsBlank\\(Self\\.Selected\\),.*?\\n\)"',
        new_on.rstrip(),
        text,
        count=1,
        flags=re.S,
    )
    if n == 0:
        text2, n = re.subn(
            r"OnChange: \"=If\(\n    !IsBlank\(Self\.Selected\),.*?\n\)\"",
            new_on.rstrip(),
            text,
            count=1,
            flags=re.S,
        )
    if n == 0:
        raise SystemExit("Create New Package project OnChange not found")

    # Inject ProjectID into package create Patch record if missing
    if "ProjectID:" not in text2 and "projectidentifier:" in text2:
        text2 = text2.replace(
            "projectidentifier:",
            "ProjectID: current_project_selected.Selected.projectid,\r\n                                    projectidentifier:",
            1,
        )
    write(path, text2)
    print("updated Create New Package")


def update_dashboard() -> None:
    path = SRC / "Project Dashboard.pa.yaml"
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r"(  Project Dashboard:\n    Properties:\n      Fill: =RGBA\(245, 245, 245, 1\)\n      LoadingSpinnerColor: =RGBA\(0, 120, 212, 1\)\n      OnVisible: \|-\n)(?:        .*\n)+",
        r"\1" + "".join("        " + line + "\n" for line in DASH_ONVISIBLE.splitlines()),
        text,
        count=1,
    )

    # Insert settings gear before dash_header_user_col
    gear = """                  - dash_settings_wrap:
                      Control: GroupContainer@1.5.0
                      Variant: ManualLayout
                      Properties:
                        AlignInContainer: =AlignInContainer.Center
                        DropShadow: =DropShadow.None
                        Fill: =RGBA(255, 255, 255, 0.18)
                        FillPortions: =0
                        Height: =32
                        LayoutMinHeight: =32
                        LayoutMinWidth: =32
                        RadiusBottomLeft: =16
                        RadiusBottomRight: =16
                        RadiusTopLeft: =16
                        RadiusTopRight: =16
                        Width: =32
                      Children:
                        - dash_settings_icon:
                            Control: Classic/Icon@2.5.0
                            Properties:
                              Color: =RGBA(255, 255, 255, 1)
                              Height: =18
                              HoverColor: =RGBA(255, 255, 255, 0.85)
                              Icon: =Icon.Settings
                              OnSelect: =Navigate(Settings, ScreenTransition.Fade)
                              Width: =18
                              X: =7
                              Y: =7
"""
    if "dash_settings_wrap:" not in text:
        text = text.replace(
            "                  - dash_header_user_col:",
            gear + "                  - dash_header_user_col:",
            1,
        )

    text2, n = re.subn(
        r"OnSelect: \|-\n(?:                                .*\n)+?                                Navigate\('Welcome screen', ScreenTransition\.Fade\)",
        "OnSelect: |-\n" + "".join("                                " + line + "\n" for line in OPEN_PROJECT.splitlines()),
        text,
        count=1,
    )
    if n == 0:
        raise SystemExit("Dashboard Open project OnSelect not found")
    write(path, text2)
    print("updated Project Dashboard")


def update_postaward() -> None:
    path = Path(__file__).resolve().parents[2] / "PostAward" / "src" / "Src" / "App.pa.yaml"
    text = path.read_text(encoding="utf-8")
    old = """      ClearCollect(
          colUserPermissions,
          Filter('ProcTrack - Permissions', Title = varCurrentUserEmail)
      );
      If(
          CountRows(colUserPermissions) = 0,
          Notify(
              "No ProcTrack - Permissions rows for " & varCurrentUserEmail,
              NotificationType.Warning
          )
      );

      ClearCollect(
          colPermittedProjects,
          Filter(
              ForAll(
                  colUserPermissions As perm,
                  LookUp('ProcTrack - Projects', projectidentifier = perm.Project)
              ),
              !IsBlank(projectidentifier)
          )
      );
      If(
          CountRows(colPermittedProjects) = 0,
          Notify(
              "colPermittedProjects is empty (check Permissions.Project vs Projects.projectidentifier).",
              NotificationType.Warning
          )
      );

      ClearCollect(
          colOwnerSubs,
          Filter(
              'PostAward - Subcontracts',
              !IsBlank(operationalowneremail) &&
              Lower(Trim(operationalowneremail)) = Lower(Trim(varCurrentUserEmail))
          )
      );
      ForAll(
          colOwnerSubs As os,
          If(
              !IsBlank(os.projectidentifier) &&
              IsBlank(
                  LookUp(
                      colPermittedProjects,
                      projectidentifier = os.projectidentifier
                  )
              ),
              Collect(
                  colPermittedProjects,
                  LookUp(
                      'ProcTrack - Projects',
                      projectidentifier = os.projectidentifier
                  )
              )
          )
      );

      Clear(colPermittedPackages);
      ForAll(
          colUserPermissions As perm,
          Collect(
              colPermittedPackages,
              Filter('ProcTrack - Packages', projectidentifier = perm.Project)
          )
      );"""
    new = """      Set(varCurrentUserEmail, Lower(User().Email));
      Set(
          varUserPerm,
          LookUp('ProcTrack - Permissions', Title = varCurrentUserEmail)
      );
      Set(varIsAdmin, Coalesce(varUserPerm.IsAdmin, false));
      If(
          IsBlank(varUserPerm),
          Notify(
              "No ProcTrack - Permissions row for " & varCurrentUserEmail,
              NotificationType.Warning
          )
      );

      ClearCollect(
          colMyProjectIds,
          Distinct(
              Filter(
                  Split(
                      Coalesce(varUserPerm.Edit_Projects, "") & ";" & Coalesce(varUserPerm.View_Projects, ""),
                      ";"
                  ),
                  !IsBlank(Trim(ThisRecord.Value))
              ),
              Value
          )
      );
      Clear(colPermittedProjects);
      ForAll(
          colMyProjectIds As idRow,
          Collect(
              colPermittedProjects,
              LookUp('ProcTrack - Projects', projectid = Trim(idRow.Value))
          )
      );
      ClearCollect(
          colPermittedProjects,
          Filter(colPermittedProjects, !IsBlank(projectid))
      );
      If(
          CountRows(colPermittedProjects) = 0,
          Notify(
              "colPermittedProjects is empty (check Permissions Edit_Projects/View_Projects vs Projects.projectid).",
              NotificationType.Warning
          )
      );

      ClearCollect(
          colOwnerSubs,
          Filter(
              'PostAward - Subcontracts',
              !IsBlank(operationalowneremail) &&
              Lower(Trim(operationalowneremail)) = Lower(Trim(varCurrentUserEmail))
          )
      );
      ForAll(
          colOwnerSubs As os,
          If(
              !IsBlank(os.projectidentifier) &&
              IsBlank(
                  LookUp(
                      colPermittedProjects,
                      projectidentifier = os.projectidentifier
                  )
              ),
              Collect(
                  colPermittedProjects,
                  LookUp(
                      'ProcTrack - Projects',
                      projectidentifier = os.projectidentifier
                  )
              )
          )
      );

      Clear(colPermittedPackages);
      ForAll(
          colPermittedProjects As p,
          Collect(
              colPermittedPackages,
              Filter(
                  'ProcTrack - Packages',
                  ProjectID = p.projectid || projectidentifier = p.projectidentifier
              )
          )
      );"""
    if old not in text:
        raise SystemExit("PostAward App.OnStart block not found exactly")
    # Avoid duplicate Set(varCurrentUserEmail) at top - PostAward already sets it earlier
    text = text.replace(old, new.replace("      Set(varCurrentUserEmail, Lower(User().Email));\n", "      Set(varCurrentUserEmail, Lower(varCurrentUserEmail));\n", 1))
    write(path, text)
    print("updated PostAward App.OnStart")


def patch_datasources() -> None:
    """Best-effort NameMapping updates inside msapr so new fields resolve."""
    import json
    import zipfile
    import tempfile
    import shutil

    msapr = next((ROOT / "src").glob("*.msapr"))
    tmp = Path(tempfile.mkdtemp())
    try:
        with zipfile.ZipFile(msapr, "r") as z:
            z.extractall(tmp)
        ds_path = tmp / "References" / "DataSources.json"
        data = json.loads(ds_path.read_text(encoding="utf-8"))
        sources = data["DataSources"] if isinstance(data, dict) else data
        for ds in sources:
            name = ds.get("Name")
            nm = ds.get("ConnectedDataSourceInfoNameMapping")
            if not isinstance(nm, dict):
                continue
            if name == "ProcTrack - Permissions":
                nm["IsAdmin"] = "IsAdmin"
                nm["Edit_Projects"] = "Edit_Projects"
                nm["View_Projects"] = "View_Projects"
            elif name == "ProcTrack - Projects":
                nm["projectid"] = "projectid"
            elif name == "ProcTrack - Packages":
                nm["ProjectID"] = "ProjectID"
        ds_path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        out = msapr.with_suffix(".msapr.new")
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for f in tmp.rglob("*"):
                if f.is_file():
                    z.write(f, f.relative_to(tmp).as_posix())
        out.replace(msapr)
        print("patched msapr DataSources NameMapping")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    update_editor_state()
    update_welcome()
    update_package_details()
    update_create_new()
    update_dashboard()
    update_postaward()
    patch_datasources()
    print("done")


if __name__ == "__main__":
    main()
