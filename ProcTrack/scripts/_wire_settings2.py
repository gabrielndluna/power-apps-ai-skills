"""Finish wiring after partial _wire_settings.py run."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "Src"
PA = Path(__file__).resolve().parents[2] / "PostAward" / "src" / "Src" / "App.pa.yaml"

NEW_ONCHANGE = """OnChange: |-
                                      =If(
                                          !IsBlank(Self.Selected),
                                          Set(varSelectedProject, Self.Selected);
                                          ClearCollect(
                                              colProjectPackages,
                                              Filter(
                                                  'ProcTrack - Packages',
                                                  ProjectID = Self.Selected.projectid || projectidentifier = Self.Selected.projectidentifier
                                              )
                                          );
                                          Set(
                                              varCanEditCurrentProject,
                                              varIsAdmin || !IsBlank(LookUp(Split(Coalesce(varUserPerm.Edit_Projects, ""), ";"), Trim(Value) = Self.Selected.projectid))
                                          )
                                      )"""


def replace_project_onchange(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    # Match the one-line quoted OnChange that still uses colUserPermissions / Edit_allowed
    pattern = re.compile(
        r'OnChange: "=If\((?:\\r\\n|\\n)    !IsBlank\(Self\.Selected\),.*?Edit_allowed = \\"yes\\".*?\)(?:\\r\\n|\\n)"',
        re.S,
    )
    text2, n = pattern.subn(NEW_ONCHANGE, text, count=1)
    if n == 0:
        raise SystemExit(f"project OnChange not found in {path.name}")
    path.write_text(text2, encoding="utf-8", newline="\n")
    print(f"updated OnChange in {path.name}")


def update_dashboard() -> None:
    path = SRC / "Project Dashboard.pa.yaml"
    text = path.read_text(encoding="utf-8")

    dash_onvisible = """=Set(varPackageFilter, "all");
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
        )
"""
    text = re.sub(
        r"(  Project Dashboard:\n    Properties:\n      Fill: =RGBA\(245, 245, 245, 1\)\n      LoadingSpinnerColor: =RGBA\(0, 120, 212, 1\)\n      OnVisible: \|-\n)(?:        .*\n)+",
        r"\1" + "".join("        " + line + "\n" if line else "\n" for line in dash_onvisible.splitlines()),
        text,
        count=1,
    )

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

    open_project = """=Set(varSelectedProject, ThisItem);
                                ClearCollect(
                                    colProjectPackages,
                                    Filter(
                                        colPermittedPackages,
                                        ProjectID = ThisItem.projectid || projectidentifier = ThisItem.projectidentifier
                                    )
                                );
                                Set(
                                    varCanEditCurrentProject,
                                    varIsAdmin || !IsBlank(LookUp(Split(Coalesce(varUserPerm.Edit_Projects, ""), ";"), Trim(Value) = ThisItem.projectid))
                                );
                                Navigate('Welcome screen', ScreenTransition.Fade)"""

    text2, n = re.subn(
        r"OnSelect: \|-\n(?:                                .*\n)+?                                Navigate\('Welcome screen', ScreenTransition\.Fade\)",
        "OnSelect: |-\n" + "".join("                                " + line + "\n" for line in open_project.splitlines()),
        text,
        count=1,
    )
    if n == 0:
        raise SystemExit("Dashboard Open project OnSelect not found")
    path.write_text(text2, encoding="utf-8", newline="\n")
    print("updated Project Dashboard")


def update_create_projectid() -> None:
    path = SRC / "Create New Package.pa.yaml"
    text = path.read_text(encoding="utf-8")
    if "ProjectID:" not in text:
        # inject near projectidentifier in create patch - first occurrence in OnPressAction
        old = "projectidentifier:"
        # only replace inside OnPressAction if possible - first projectidentifier: in file in create context
        idx = text.find("OnPressAction:")
        if idx < 0:
            raise SystemExit("OnPressAction not found")
        sub = text[idx:]
        # find packaged create fields - look for projectidentifier: after OnPressAction
        j = sub.find("projectidentifier:")
        if j < 0:
            # maybe escaped differently
            j = sub.find("projectidentifier")
            print("debug around", repr(sub[j:j+80]) if j>=0 else "none")
            raise SystemExit("projectidentifier in create not found")
        # Determine delimiter style around it
        chunk = sub[j:j+40]
        if "projectidentifier:" in chunk:
            inj = "ProjectID: current_project_selected.Selected.projectid, "
            # if using \r\n style inside string
            if "\\r\\n" in sub[j-20:j+80] or "\r\n" in text[idx+j-5:idx+j+5]:
                pass
            text = text[: idx + j] + "ProjectID: current_project_selected.Selected.projectid,\r\n                                    " + text[idx + j :]
        path.write_text(text, encoding="utf-8", newline="\n")
        print("injected ProjectID into Create New Package")
    else:
        print("Create New Package already has ProjectID")


def update_postaward() -> None:
    text = PA.read_text(encoding="utf-8")
    if "Edit_Projects" in text:
        print("PostAward already updated")
        return
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
    new = """      Set(varCurrentUserEmail, Lower(varCurrentUserEmail));
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
        raise SystemExit("PostAward block not found")
    PA.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
    print("updated PostAward App.OnStart")


def patch_datasources() -> None:
    import json
    import shutil
    import tempfile
    import zipfile

    root = Path(__file__).resolve().parents[1]
    msapr = next((root / "src").glob("*.msapr"))
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
        print("patched msapr DataSources")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def verify_welcome() -> None:
    path = SRC / "Welcome screen.pa.yaml"
    text = path.read_text(encoding="utf-8")
    assert "Navigate(Settings" in text, "Welcome gear not wired"
    assert "Container29" not in text, "overlay still present"
    assert "Edit_allowed" not in text or "colUserPermissions" not in text
    # OnVisible should mention ProjectID or varUserPerm edit
    if "Edit_allowed" in text or "colUserPermissions" in text:
        raise SystemExit("Welcome still has old permission refs")
    print("Welcome verified")


def main() -> None:
    replace_project_onchange(SRC / "Welcome screen.pa.yaml")
    replace_project_onchange(SRC / "Package Details.pa.yaml")
    replace_project_onchange(SRC / "Create New Package.pa.yaml")
    update_create_projectid()
    update_dashboard()
    update_postaward()
    patch_datasources()
    verify_welcome()
    # welcome onvisible check
    w = (SRC / "Welcome screen.pa.yaml").read_text(encoding="utf-8")
    if "ProjectID = varSelectedProject.projectid" not in w:
        print("WARNING: Welcome OnVisible may still use old filter")
    print("done")


if __name__ == "__main__":
    main()
