"""Replace Ungroup package paging with Collect from the SharePoint list."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "Src"
FILES = [
    "Project Home.pa.yaml",
    "Welcome screen.pa.yaml",
    "Create New Package.pa.yaml",
    "Package Details.pa.yaml",
]
START = "Set(varMaxPackageId, Coalesce(First(SortByColumns('ProcTrack - Packages'"
END = "ClearCollect(colProjectPackages, colPackageDeduped)"


def block(indent: str) -> str:
    i = indent
    a = indent + "    "
    b = indent + "        "
    c = indent + "            "
    lines = [
        f"{i}Set(varMaxPackageId, Coalesce(First(SortByColumns('ProcTrack - Packages', \"ID\", SortOrder.Descending)).ID, 0));",
        f"{i}ClearCollect(",
        f"{a}colProjectPackages,",
        f"{a}Filter(",
        f"{b}'ProcTrack - Packages',",
        f"{b}ProjectID = varSelectedProject.projectid && ID >= 1 && ID <= 2000",
        f"{a})",
        f"{i});",
        f"{i}If(",
        f"{a}varMaxPackageId > 2000,",
        f"{a}ForAll(",
        f"{b}Sequence(RoundUp(varMaxPackageId / 2000, 0) - 1),",
        f"{b}Collect(",
        f"{c}colProjectPackages,",
        f"{c}Filter(",
        f"{c}    'ProcTrack - Packages',",
        f"{c}    ProjectID = varSelectedProject.projectid && ID >= Value * 2000 + 1 && ID <= (Value + 1) * 2000",
        f"{c})",
        f"{b})",
        f"{a})",
        f"{i});",
        f"{i}If(",
        f"{a}!IsBlank(varSelectedProject.projectidentifier),",
        f"{a}Collect(",
        f"{b}colProjectPackages,",
        f"{b}Filter(",
        f"{c}'ProcTrack - Packages',",
        f"{c}projectidentifier = varSelectedProject.projectidentifier && ID >= 1 && ID <= 2000",
        f"{b})",
        f"{a});",
        f"{a}If(",
        f"{b}varMaxPackageId > 2000,",
        f"{b}ForAll(",
        f"{c}Sequence(RoundUp(varMaxPackageId / 2000, 0) - 1),",
        f"{c}Collect(",
        f"{c}    colProjectPackages,",
        f"{c}    Filter(",
        f"{c}        'ProcTrack - Packages',",
        f"{c}        projectidentifier = varSelectedProject.projectidentifier && ID >= Value * 2000 + 1 && ID <= (Value + 1) * 2000",
        f"{c}    )",
        f"{c})",
        f"{b})",
        f"{a})",
        f"{i});",
        f"{i}ForAll(",
        f"{a}Distinct(colProjectPackages, ID) As d,",
        f"{a}If(",
        f"{b}CountRows(Filter(colProjectPackages, ID = d.Value)) > 1,",
        f"{b}Remove(colProjectPackages, Last(Filter(colProjectPackages, ID = d.Value)))",
        f"{a})",
        f"{i})",
    ]
    return "\n".join(lines) + "\n"


def replace_blocks(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    count = 0
    while i < len(lines):
        if START in lines[i]:
            indent = lines[i][: len(lines[i]) - len(lines[i].lstrip(" "))]
            j = i
            while j < len(lines) and END not in lines[j]:
                j += 1
            if j >= len(lines):
                raise SystemExit("end marker not found")
            # Keep a trailing semicolon when the original statement had one.
            original_end = lines[j].rstrip()
            replacement = block(indent)
            if original_end.endswith(";"):
                replacement = replacement.rstrip("\n") + ";\n"
            out.append(replacement)
            count += 1
            i = j + 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out), count


def main() -> None:
    for name in FILES:
        path = ROOT / name
        updated, count = replace_blocks(path.read_text(encoding="utf-8"))
        if count == 0:
            raise SystemExit(f"no block in {name}")
        path.write_text(updated, encoding="utf-8")
        print(name, count)


if __name__ == "__main__":
    main()
