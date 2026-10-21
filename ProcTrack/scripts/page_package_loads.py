"""Replace capped SharePoint package collects with ID-window paging."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src" / "Src"
FILES = [
    "Project Home.pa.yaml",
    "Welcome screen.pa.yaml",
    "Create New Package.pa.yaml",
    "Package Details.pa.yaml",
]

OLD_START = "ClearCollect(\n"
MARKER = "'ProcTrack - Packages'"


def paged_block(indent: str) -> str:
    i = indent
    n = indent + "    "
    return (
        f"{i}Clear(colProjectPackages);\n"
        f"{i}If(\n"
        f"{n}!IsBlank(varSelectedProject.projectid),\n"
        f"{n}Collect(\n"
        f"{n}    colProjectPackages,\n"
        f"{n}    Ungroup(\n"
        f"{n}        ForAll(\n"
        f"{n}            Sequence(Max(1, RoundUp(Coalesce(varMaxPackageId, 1) / 2000, 0))) As page,\n"
        f"{n}            {{\n"
        f"{n}                recs: Filter(\n"
        f"{n}                    'ProcTrack - Packages',\n"
        f"{n}                    ProjectID = varSelectedProject.projectid &&\n"
        f"{n}                    ID >= (page.Value - 1) * 2000 + 1 &&\n"
        f"{n}                    ID <= page.Value * 2000\n"
        f"{n}                )\n"
        f"{n}            }}\n"
        f"{n}        ),\n"
        f"{n}        \"recs\"\n"
        f"{n}    )\n"
        f"{n})\n"
        f"{i});\n"
        f"{i}If(\n"
        f"{n}!IsBlank(varSelectedProject.projectidentifier),\n"
        f"{n}Collect(\n"
        f"{n}    colProjectPackages,\n"
        f"{n}    Ungroup(\n"
        f"{n}        ForAll(\n"
        f"{n}            Sequence(Max(1, RoundUp(Coalesce(varMaxPackageId, 1) / 2000, 0))) As page,\n"
        f"{n}            {{\n"
        f"{n}                recs: Filter(\n"
        f"{n}                    'ProcTrack - Packages',\n"
        f"{n}                    projectidentifier = varSelectedProject.projectidentifier &&\n"
        f"{n}                    ID >= (page.Value - 1) * 2000 + 1 &&\n"
        f"{n}                    ID <= page.Value * 2000\n"
        f"{n}                )\n"
        f"{n}            }}\n"
        f"{n}        ),\n"
        f"{n}        \"recs\"\n"
        f"{n}    )\n"
        f"{n})\n"
        f"{i});\n"
        f"{i}Clear(colPackageDeduped);\n"
        f"{i}ForAll(\n"
        f"{n}Distinct(colProjectPackages, ID) As d,\n"
        f"{n}Collect(colPackageDeduped, LookUp(colProjectPackages, ID = d.Value))\n"
        f"{i});\n"
        f"{i}ClearCollect(colProjectPackages, colPackageDeduped)"
    )


def replace_collects(text: str) -> tuple[str, int]:
    count = 0
    out = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("ClearCollect(") and i + 6 < len(lines):
            window = "".join(lines[i : i + 8])
            if "colProjectPackages" in window and MARKER in window and "ProjectID =" in window:
                indent = lines[i][: len(lines[i]) - len(lines[i].lstrip(" "))]
                # Consume through the closing ");" of this ClearCollect.
                j = i
                depth = 0
                while j < len(lines):
                    depth += lines[j].count("(") - lines[j].count(")")
                    if j > i and depth <= 0:
                        j += 1
                        break
                    j += 1
                block = paged_block(indent)
                # Keep a trailing semicolon if the original statement had one.
                original = "".join(lines[i:j])
                if original.rstrip().endswith(";") and not block.rstrip().endswith(";"):
                    block += ";"
                if lines[j - 1].endswith("\n"):
                    block += "\n"
                out.append(block)
                count += 1
                i = j
                continue
        out.append(lines[i])
        i += 1
    return "".join(out), count


def add_max_id(path: Path) -> None:
    set_line = (
        'Set(varMaxPackageId, Coalesce(First(SortByColumns(\'ProcTrack - Packages\', "ID", SortOrder.Descending)).ID, 0));'
    )
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out = []
    for line in lines:
        if line.strip() == "Clear(colProjectPackages);":
            indent = line[: len(line) - len(line.lstrip(" "))]
            out.append(indent + set_line + "\n")
        out.append(line)
    path.write_text("".join(out), encoding="utf-8")


def main() -> None:
    for name in FILES:
        path = ROOT / name
        text, count = replace_collects(path.read_text(encoding="utf-8"))
        if count == 0:
            raise SystemExit(f"no collects replaced in {name}")
        path.write_text(text, encoding="utf-8")
        print(name, count)


if __name__ == "__main__":
    main()
