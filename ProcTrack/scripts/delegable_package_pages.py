"""Load packages in fixed ID windows so each Filter stays delegable."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "Src"
PAGES = [(lo, lo + 1999) for lo in range(1, 30001, 2000)]
START = "Set(varMaxPackageId, Coalesce(First(SortByColumns('ProcTrack - Packages'"
END_MARK = "Remove(colProjectPackages, Last(Filter(colProjectPackages, ID = d.Value)))"


def windows(indent: str, target: str) -> str:
    lines = []
    pad = indent + "    "
    inner = indent + "        "
    for index, (lo, hi) in enumerate(PAGES):
        fn = "ClearCollect" if index == 0 else "Collect"
        lines.extend(
            [
                f"{indent}{fn}(",
                f"{pad}{target},",
                f"{pad}Filter(",
                f"{inner}'ProcTrack - Packages',",
                f"{inner}ID >= {lo} && ID <= {hi}",
                f"{pad})",
                f"{indent});",
            ]
        )
    return "\n".join(lines)


def permitted_tail(indent: str) -> str:
    a = indent + "    "
    b = indent + "        "
    c = indent + "            "
    return "\n".join(
        [
            f"{indent}ClearCollect(",
            f"{a}colPermittedPackages,",
            f"{a}Filter(",
            f"{b}colPackagePage As pkg,",
            f"{b}!IsBlank(",
            f"{c}LookUp(",
            f"{c}    colPermittedProjects,",
            f"{c}    projectid = pkg.ProjectID || projectidentifier = pkg.projectidentifier",
            f"{c})",
            f"{b})",
            f"{a})",
            f"{indent});",
            f"{indent}Clear(colPackagePage)",
        ]
    )


def replace_from_marker(text: str, start_pat: str, end_pat: str, replacement: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if start_pat in line)
    if start > 0 and lines[start - 1].strip() == "Set(":
        start -= 1
    end = next(i for i, line in enumerate(lines) if i >= start and end_pat in line)
    while end + 1 < len(lines):
        end += 1
        stripped = lines[end].strip()
        nxt = lines[end + 1].strip() if end + 1 < len(lines) else ""
        if stripped.endswith(";") or (stripped == ")" and nxt.startswith("Children:")):
            break
    block = replacement if replacement.endswith("\n") else replacement + "\n"
    return "".join(lines[:start] + [block] + lines[end + 1 :])


def local_project(indent: str, semicolon: bool) -> str:
    a = indent + "    "
    b = indent + "        "
    tail = ";" if semicolon else ""
    return "\n".join(
        [
            f"{indent}ClearCollect(",
            f"{a}colProjectPackages,",
            f"{a}Filter(",
            f"{b}colPermittedPackages,",
            f"{b}ProjectID = varSelectedProject.projectid || projectidentifier = varSelectedProject.projectidentifier",
            f"{a})",
            f"{indent}){tail}",
        ]
    ) + "\n"


def replace_project_blocks(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    count = 0
    while i < len(lines):
        if START in lines[i]:
            indent = lines[i][: len(lines[i]) - len(lines[i].lstrip(" "))]
            j = i
            while j < len(lines) and END_MARK not in lines[j]:
                j += 1
            if j >= len(lines):
                raise SystemExit("project block end not found")
            # Closing lines after the Remove call: ) and );
            j += 1
            while j < len(lines) and "ForAll" not in lines[j] and not lines[j].strip().startswith(");"):
                j += 1
            if j < len(lines) and lines[j].strip().startswith(");"):
                semicolon = True
                j += 1
            else:
                semicolon = True
            out.append(local_project(indent, semicolon))
            count += 1
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "".join(out), count


def main() -> None:
    app = ROOT / "App.pa.yaml"
    app_text = app.read_text(encoding="utf-8")
    app_load = windows("      ", "colPackagePage") + "\n" + permitted_tail("      ") + ";\n"
    app.write_text(
        replace_from_marker(
            app_text,
            "Each SharePoint request returns at most 2,000 rows",
            "projectid = pkg.ProjectID",
            "      // Fixed ID windows stay delegable. Each window is at most 2,000 rows.\n" + app_load,
        ),
        encoding="utf-8",
    )
    print("app")

    dash = ROOT / "Project Dashboard.pa.yaml"
    dash_text = dash.read_text(encoding="utf-8")
    dash_load = windows("        ", "colPackagePage") + "\n" + permitted_tail("        ") + "\n"
    dash.write_text(
        replace_from_marker(
            dash_text,
            "SortByColumns('ProcTrack - Packages'",
            "projectid = pkg.ProjectID",
            dash_load,
        ),
        encoding="utf-8",
    )
    print("dashboard")

    for name in [
        "Project Home.pa.yaml",
        "Welcome screen.pa.yaml",
        "Create New Package.pa.yaml",
        "Package Details.pa.yaml",
    ]:
        path = ROOT / name
        updated, count = replace_project_blocks(path.read_text(encoding="utf-8"))
        if count == 0:
            raise SystemExit(f"no project block in {name}")
        path.write_text(updated, encoding="utf-8")
        print(name, count)

    create = ROOT / "Create New Package.pa.yaml"
    text = create.read_text(encoding="utf-8")
    old = "Navigate('Package Details', ScreenTransition.Fade)"
    new = (
        "Collect(colPermittedPackages, newRecord); "
        "Collect(colProjectPackages, newRecord); "
        "Navigate('Package Details', ScreenTransition.Fade)"
    )
    if old not in text:
        raise SystemExit("navigate marker missing")
    if "Collect(colPermittedPackages, newRecord)" not in text:
        text = text.replace(old, new, 1)
        create.write_text(text, encoding="utf-8")
        print("create collect")


if __name__ == "__main__":
    main()
