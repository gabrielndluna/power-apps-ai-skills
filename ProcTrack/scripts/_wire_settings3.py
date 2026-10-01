from pathlib import Path

SRC = Path("src/Src")
NEW = """OnChange: |-
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


def replace_from_dump(yaml_name: str, dump_name: str) -> None:
    path = SRC / yaml_name
    text = path.read_text(encoding="utf-8")
    old = Path(dump_name).read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"dump snippet not found in {yaml_name}")
    path.write_text(text.replace(old, NEW, 1), encoding="utf-8", newline="\n")
    print("replaced", yaml_name)


def main() -> None:
    replace_from_dump("Welcome screen.pa.yaml", "_onchange_Welcome_screen.pa.yaml.txt")
    replace_from_dump("Package Details.pa.yaml", "_onchange_Package_Details.pa.yaml.txt")
    replace_from_dump("Create New Package.pa.yaml", "_onchange_Create_New_Package.pa.yaml.txt")

    # Create New Package ProjectID inject
    path = SRC / "Create New Package.pa.yaml"
    text = path.read_text(encoding="utf-8")
    if "ProjectID:" not in text:
        marker = "projectidentifier:"
        # prefer occurrence inside OnPressAction
        idx = text.find("OnPressAction:")
        j = text.find(marker, idx)
        if j < 0:
            raise SystemExit("projectidentifier not in create action")
        text = (
            text[:j]
            + "ProjectID: current_project_selected.Selected.projectid,\r\n                                    "
            + text[j:]
        )
        path.write_text(text, encoding="utf-8", newline="\n")
        print("injected ProjectID")
    else:
        print("ProjectID already present")

    # Dashboard
    import re

    path = SRC / "Project Dashboard.pa.yaml"
    text = path.read_text(encoding="utf-8")
    dash_body = """=Set(varPackageFilter, "all");
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
    text2, n = re.subn(
        r"(      OnVisible: \|-\n)(?:        .*\n)+?(    Children:)",
        r"\1" + "".join(("        " + line + "\n") for line in dash_body.splitlines()) + r"\2",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"dashboard OnVisible replace failed {n}")
    text = text2

    if "dash_settings_wrap:" not in text:
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
        text = text.replace(
            "                  - dash_header_user_col:",
            gear + "                  - dash_header_user_col:",
            1,
        )

    open_sel = """OnSelect: |-
                                =Set(varSelectedProject, ThisItem);
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
    text3, n = re.subn(
        r"OnSelect: \|-\n(?:                                .*\n)+?                                Navigate\('Welcome screen', ScreenTransition\.Fade\)",
        open_sel,
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"open project replace failed {n}")
    path.write_text(text3, encoding="utf-8", newline="\n")
    print("dashboard updated")

    # PostAward
    pa = Path("../PostAward/src/Src/App.pa.yaml")
    t = pa.read_text(encoding="utf-8")
    if "Edit_Projects" not in t:
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
        if old not in t:
            raise SystemExit("PostAward old block missing")
        pa.write_text(t.replace(old, new), encoding="utf-8", newline="\n")
        print("PostAward updated")
    else:
        print("PostAward already ok")

    # datasources
    import json, shutil, tempfile, zipfile

    msapr = next(Path("src").glob("*.msapr"))
    tmp = Path(tempfile.mkdtemp())
    with zipfile.ZipFile(msapr, "r") as z:
        z.extractall(tmp)
    ds_path = tmp / "References" / "DataSources.json"
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
        elif ds.get("Name") == "ProcTrack - Projects":
            nm["projectid"] = "projectid"
        elif ds.get("Name") == "ProcTrack - Packages":
            nm["ProjectID"] = "ProjectID"
    ds_path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    out = msapr.with_suffix(".msapr.new")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in tmp.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(tmp).as_posix())
    out.replace(msapr)
    shutil.rmtree(tmp, ignore_errors=True)
    print("msapr patched")

    # Welcome OnVisible ensure ProjectID
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
        if old_vis_filter not in w:
            print("WARNING Welcome OnVisible filter not found as expected")
        else:
            wpath.write_text(w.replace(old_vis_filter, new_vis_filter, 1), encoding="utf-8", newline="\n")
            print("Welcome OnVisible updated")
    else:
        print("Welcome OnVisible already uses ProjectID")

    # sanity
    for name in ["Welcome screen.pa.yaml", "Package Details.pa.yaml", "Create New Package.pa.yaml", "Project Dashboard.pa.yaml"]:
        t = (SRC / name).read_text(encoding="utf-8")
        bad = []
        if "Edit_allowed" in t:
            bad.append("Edit_allowed")
        if "colUserPermissions" in t:
            bad.append("colUserPermissions")
        print(name, "OK" if not bad else "STILL HAS " + ",".join(bad))
    print("Settings exists", (SRC / "Settings.pa.yaml").exists())
    print("EditorState", (SRC / "_EditorState.pa.yaml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
