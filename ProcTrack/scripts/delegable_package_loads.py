"""Replace non-delegable ID paging with project equality plus identifier prefixes.

SharePoint delegates only '=' on the built-in ID column, so ID ranges scan the
first data-row page and a project stays at 500. projectidentifier and
packageidentifier delegate '=' and StartsWith. A hex prefix splits one project
into buckets that each fit in that page, including packages created on the
same day.
"""

from pathlib import Path


PREFIXES = [str(digit) for digit in range(10)] + list("abcdefABCDEF")


def prefix_collects(indent: int, key_test: str) -> list[str]:
    pad = " " * indent
    lines = []
    for index, prefix in enumerate(PREFIXES):
        comma = ";" if index < len(PREFIXES) - 1 else ""
        lines.append(
            f"{pad}Collect(colPermittedPackages, Filter('ProcTrack - Packages', {key_test}, StartsWith(packageidentifier, \"{prefix}\"))){comma}"
        )
    return lines


def load_block(indent: int, trailing_semicolon: bool) -> str:
    pad = " " * indent
    inner = " " * (indent + 4)
    deep = " " * (indent + 8)
    end = ";" if trailing_semicolon else ""
    lines = [
        f"{pad}// One delegable query per project. Do not filter colPermittedProjects inside this loop.",
        f"{pad}If(",
        f"{inner}CountRows(colPermittedProjects) > 0,",
        f"{inner}ClearCollect(",
        f"{deep}colPermittedPackages,",
        f"{deep}Filter(",
        f"{deep}    'ProcTrack - Packages',",
        f"{deep}    projectidentifier = First(colPermittedProjects).projectidentifier ||",
        f"{deep}    ProjectID = First(colPermittedProjects).projectid",
        f"{deep})",
        f"{inner});",
        f"{inner}If(",
        f"{deep}CountRows(colPermittedProjects) > 1,",
        f"{deep}ForAll(",
        f"{deep}    colPermittedProjects As proj,",
        f"{deep}    If(",
        f"{deep}        proj.projectidentifier <> First(colPermittedProjects).projectidentifier ||",
        f"{deep}        proj.projectid <> First(colPermittedProjects).projectid,",
        f"{deep}        Collect(",
        f"{deep}            colPermittedPackages,",
        f"{deep}            Filter(",
        f"{deep}                'ProcTrack - Packages',",
        f"{deep}                projectidentifier = proj.projectidentifier || ProjectID = proj.projectid",
        f"{deep}            )",
        f"{deep}        )",
        f"{deep}    )",
        f"{deep})",
        f"{inner})",
        f"{pad}){end}",
    ]
    return "\n".join(lines) + "\n"
    pad = " " * indent
    inner = " " * (indent + 4)
    deep = " " * (indent + 8)
    code_lines = prefix_collects(indent + 16, "projectidentifier = proj.projectidentifier")
    id_lines = prefix_collects(indent + 16, "ProjectID = proj.projectid")
    end = ";" if trailing_semicolon else ""
    lines = [
        f"{pad}// SharePoint only delegates '=' on ID. projectidentifier and StartsWith do delegate.",
        f"{pad}If(",
        f"{inner}CountRows(colPermittedProjects) > 0 &&",
        f"{inner}(",
        f"{deep}IsBlank(varPackageLoadTick) ||",
        f"{deep}DateDiff(varPackageLoadTick, Now(), TimeUnit.Seconds) > 30 ||",
        f"{deep}CountRows(colPermittedPackages) = 0",
        f"{inner}),",
        f"{inner}ClearCollect(",
        f"{deep}colPermittedPackages,",
        f"{deep}Filter(",
        f"{deep}    'ProcTrack - Packages',",
        f"{deep}    projectidentifier = \"___none___\"",
        f"{deep})",
        f"{inner});",
        f"{inner}ForAll(",
        f"{deep}colPermittedProjects As proj,",
        f"{deep}Collect(",
        f"{deep}    colPermittedPackages,",
        f"{deep}    Filter(",
        f"{deep}        'ProcTrack - Packages',",
        f"{deep}        projectidentifier = proj.projectidentifier",
        f"{deep}    )",
        f"{deep});",
        f"{deep}If(",
        f"{deep}    CountRows(",
        f"{deep}        Filter(",
        f"{deep}            colPermittedPackages,",
        f"{deep}            projectidentifier = proj.projectidentifier",
        f"{deep}        )",
        f"{deep}    ) >= 500,",
        *code_lines,
        f"{deep});",
        f"{deep}Collect(",
        f"{deep}    colPermittedPackages,",
        f"{deep}    Filter(",
        f"{deep}        'ProcTrack - Packages',",
        f"{deep}        ProjectID = proj.projectid",
        f"{deep}    )",
        f"{deep});",
        f"{deep}If(",
        f"{deep}    CountRows(",
        f"{deep}        Filter(",
        f"{deep}            colPermittedPackages,",
        f"{deep}            ProjectID = proj.projectid",
        f"{deep}        )",
        f"{deep}    ) >= 500,",
        *id_lines,
        f"{deep})",
        f"{inner});",
        f"{inner}Clear(colPackagePage);",
        f"{inner}ForAll(",
        f"{deep}colPermittedPackages,",
        f"{deep}If(",
        f"{deep}    IsBlank(LookUp(colPackagePage, ID = ThisRecord.ID)),",
        f"{deep}    Collect(colPackagePage, ThisRecord)",
        f"{deep})",
        f"{inner});",
        f"{inner}ClearCollect(colPermittedPackages, colPackagePage);",
        f"{inner}Clear(colPackagePage);",
        f"{inner}Set(varPackageLoadTick, Now())",
        f"{pad}){end}",
    ]
    return "\n".join(lines) + "\n"


def replace_block(
    text: str,
    start_pat: str,
    end_pat: str,
    replacement: str,
    walk_back_to_clearcollect: bool,
) -> str:
    lines = text.splitlines(keepends=True)
    start = next(index for index, line in enumerate(lines) if start_pat in line)
    if walk_back_to_clearcollect:
        while start > 0 and "ClearCollect(" not in lines[start]:
            start -= 1
    end = next(index for index, line in enumerate(lines) if index >= start and end_pat in line)
    if end + 1 < len(lines) and lines[end + 1].strip() in {")", ");"}:
        end += 1
    return "".join(lines[:start] + [replacement] + lines[end + 1 :])


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    app = root / "src" / "Src" / "App.pa.yaml"
    dashboard = root / "src" / "Src" / "Project Dashboard.pa.yaml"
    app.write_text(
        replace_block(
            app.read_text(encoding="utf-8"),
            "SharePoint only delegates",
            "Set(varPackageLoadTick, Now())",
            load_block(6, True),
            False,
        ),
        encoding="utf-8",
    )
    dashboard.write_text(
        replace_block(
            dashboard.read_text(encoding="utf-8"),
            "SharePoint only delegates",
            "Set(varPackageLoadTick, Now())",
            load_block(8, False),
            False,
        ),
        encoding="utf-8",
    )
    print("rewrote package loads")


if __name__ == "__main__":
    main()
