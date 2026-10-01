"""Shrink left-panel field rows and restore Excel Image controls."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "Src"


def find_control_range(lines: list[str], control_name: str) -> tuple[int, int]:
    start = None
    base_indent = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith(f"- {control_name}:"):
            start = i
            base_indent = len(line) - len(line.lstrip(" "))
            break
    if start is None:
        raise SystemExit(f"not found: {control_name}")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= base_indent and line.lstrip().startswith("- "):
            end = j
            break
    return start, end


def shrink_body(chunk: str) -> str:
    chunk = chunk.replace("LayoutGap: =4\n", "LayoutGap: =3\n", 1)
    chunk = chunk.replace("PaddingBottom: =6\n", "PaddingBottom: =4\n", 1)
    chunk = chunk.replace("PaddingTop: =6\n", "PaddingTop: =4\n", 1)
    chunk = chunk.replace("Height: =44\n", "Height: =38\n")
    chunk = chunk.replace("LayoutMinHeight: =44\n", "LayoutMinHeight: =38\n")
    chunk = chunk.replace("Height: =28\n", "Height: =24\n")
    chunk = chunk.replace("Height: =12\n", "Height: =11\n")
    # tighter vertical gap inside each row (label + field)
    chunk = chunk.replace("LayoutGap: =2\n", "LayoutGap: =1\n")
    return chunk


EXCEL_IMAGE = """\
                              - {name}:
                                  Control: Image@2.2.3
                                  Properties:
                                    BorderColor: =RGBA(0, 0, 0, 0)
                                    BorderStyle: =BorderStyle.None
                                    DisabledBorderColor: =RGBA(0, 0, 0, 0)
                                    DisabledFill: =RGBA(0, 0, 0, 0)
                                    Height: =22
                                    HoverBorderColor: =RGBA(0, 0, 0, 0)
                                    HoverFill: =RGBA(0, 0, 0, 0)
                                    Image: ='excel-icon-17'
                                    OnSelect: =Launch(varSubcontractsListUrl)
                                    PressedBorderColor: =RGBA(0, 0, 0, 0)
                                    PressedFill: =RGBA(0, 0, 0, 0)
                                    Width: =22
                                    X: =5
                                    Y: =5
"""


def replace_xls_icon(text: str, img_name: str) -> str:
    """Replace Classic/Icon xls control block with Image@2.2.3 excel-icon-17."""
    marker = f"- {img_name}:"
    start = text.find(marker)
    if start < 0:
        raise SystemExit(f"missing {img_name}")
    # back up to line start (indent)
    line_start = text.rfind("\n", 0, start) + 1
    # find end: next sibling at same indent under Children, or end of Children parent
    # The icon block ends before the next line that starts with same indent + "- " OR less indent
    lines = text[line_start:].splitlines(keepends=True)
    first = lines[0]
    indent = len(first) - len(first.lstrip(" "))
    end_rel = len(first)
    for line in lines[1:]:
        if not line.strip():
            end_rel += len(line)
            continue
        i = len(line) - len(line.lstrip(" "))
        if line.lstrip().startswith("- ") and i <= indent:
            break
        if i < indent and line.lstrip():
            break
        end_rel += len(line)
    # Build replacement with correct indent of the - name line
    repl_lines = []
    base = EXCEL_IMAGE.format(name=img_name).splitlines(keepends=True)
    # EXCEL_IMAGE uses 30 spaces before "- name"; normalize to actual indent
    sample_indent = len(base[0]) - len(base[0].lstrip(" "))
    delta = indent - sample_indent
    for bl in base:
        if bl.strip() == "":
            repl_lines.append(bl)
            continue
        if delta >= 0:
            repl_lines.append((" " * delta) + bl)
        else:
            # remove leading spaces
            strip_n = -delta
            if bl.startswith(" " * strip_n):
                repl_lines.append(bl[strip_n:])
            else:
                repl_lines.append(bl.lstrip(" "))
    return text[:line_start] + "".join(repl_lines) + text[line_start + end_rel :]


def main() -> None:
    detail = SRC / "Subcontract Detail.pa.yaml"
    lines = detail.read_text(encoding="utf-8").splitlines(keepends=True)

    # Ensure left panel has constrained height so Scroll works
    text = "".join(lines)
    if "LayoutOverflowY: =LayoutOverflow.Scroll" in text and "Height: =Parent.Height" not in text[
        text.find("- det_left:") : text.find("- det_left:") + 800
    ]:
        text = text.replace(
            """                  - det_left:
                      Control: GroupContainer@1.5.0
                      Variant: AutoLayout
                      Properties:
                        DropShadow: =DropShadow.None
                        Fill: =RGBA(255, 255, 255, 1)
                        FillPortions: =0
                        LayoutAlignItems: =LayoutAlignItems.Stretch
                        LayoutDirection: =LayoutDirection.Vertical
                        LayoutGap: =0
                        LayoutMinHeight: =0
                        LayoutMinWidth: =0
                        LayoutOverflowY: =LayoutOverflow.Scroll
""",
            """                  - det_left:
                      Control: GroupContainer@1.5.0
                      Variant: AutoLayout
                      Properties:
                        DropShadow: =DropShadow.None
                        Fill: =RGBA(255, 255, 255, 1)
                        FillPortions: =0
                        Height: =Parent.Height
                        LayoutAlignItems: =LayoutAlignItems.Stretch
                        LayoutDirection: =LayoutDirection.Vertical
                        LayoutGap: =0
                        LayoutMinHeight: =0
                        LayoutMinWidth: =0
                        LayoutOverflowY: =LayoutOverflow.Scroll
""",
            1,
        )

    lines = text.splitlines(keepends=True)
    for body in ("det_basics_body", "det_people_body"):
        start, end = find_control_range(lines, body)
        chunk = shrink_body("".join(lines[start:end]))
        lines = lines[:start] + chunk.splitlines(keepends=True) + lines[end:]

    text = "".join(lines)
    text = replace_xls_icon(text, "det_xls_img")
    detail.write_text(text, encoding="utf-8")
    print(f"updated {detail.name}")

    for fname, img in (("Home.pa.yaml", "home_xls_img"), ("Register.pa.yaml", "reg_xls_img")):
        path = SRC / fname
        t = path.read_text(encoding="utf-8")
        t = replace_xls_icon(t, img)
        path.write_text(t, encoding="utf-8")
        print(f"updated {fname}")


if __name__ == "__main__":
    main()
