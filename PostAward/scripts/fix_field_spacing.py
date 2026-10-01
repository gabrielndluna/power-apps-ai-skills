"""Improve left-panel field spacing, borders, and DatePicker font size."""
from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src" / "Src" / "Subcontract Detail.pa.yaml"
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

ROW_NAMES = {
    "det_row_sub_po",
    "det_row_vendor_scope",
    "det_row_bundle",
    "det_row_start",
    "det_row_end",
    "det_row_revised",
    "det_row_sap",
    "det_row_currency",
    "det_row_indigenous",
    "det_row_worktype",
    "det_row_ca",
    "det_row_backup",
    "det_row_owner",
    "det_row_active",
    "det_row_hb",
    "det_row_close",
}


def find_range(name: str) -> tuple[int, int]:
    start = base = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith(f"- {name}:"):
            start = i
            base = len(line) - len(line.lstrip(" "))
            break
    if start is None:
        raise SystemExit(f"missing {name}")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        line = lines[j]
        if not line.strip():
            continue
        ind = len(line) - len(line.lstrip(" "))
        if ind <= base and line.lstrip().startswith("- "):
            end = j
            break
    return start, end


def fix_body(chunk_lines: list[str]) -> list[str]:
    text = "".join(chunk_lines)
    text = text.replace("LayoutGap: =3\n", "LayoutGap: =6\n", 1)
    text = text.replace("PaddingBottom: =4\n", "PaddingBottom: =10\n", 1)
    text = text.replace("PaddingTop: =4\n", "PaddingTop: =8\n", 1)
    # room under control so bottom border is not clipped (was exact fill)
    text = text.replace("Height: =40\n", "Height: =48\n")
    text = text.replace("LayoutMinHeight: =40\n", "LayoutMinHeight: =48\n")
    text = text.replace("LayoutGap: =2\n", "LayoutGap: =4\n")
    text = text.replace("Height: =14\n", "Height: =15\n")
    # 15 + 4 + 26 = 45 inside row 48 (+ padding bottom)
    text = text.replace("Height: =24\n", "Height: =26\n")
    text = text.replace("Size: =10\n", "Size: =9\n")
    # half-cols: side padding now 8+8 + gap 8
    text = text.replace(
        "Width: =(Parent.Width - 20) / 2\n",
        "Width: =(Parent.Width - 24) / 2\n",
    )

    clines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(clines):
        line = clines[i]
        is_row = any(line.lstrip().startswith(f"- {rn}:") for rn in ROW_NAMES)
        out.append(line)
        i += 1
        if not is_row:
            continue
        row_indent = len(line) - len(line.lstrip(" "))
        while i < len(clines):
            cur = clines[i]
            if cur.lstrip().startswith("- ") and (len(cur) - len(cur.lstrip(" "))) == row_indent:
                break
            if cur.lstrip().startswith("Properties:"):
                out.append(cur)
                i += 1
                props: list[str] = []
                prop_indent = None
                while i < len(clines):
                    pl = clines[i]
                    if pl.lstrip().startswith("Children:"):
                        break
                    if pl.strip() and prop_indent is None:
                        prop_indent = len(pl) - len(pl.lstrip(" "))
                    if pl.strip() and prop_indent is not None:
                        pindent = len(pl) - len(pl.lstrip(" "))
                        if pindent < prop_indent:
                            break
                    if pl.lstrip().startswith("PaddingLeft:"):
                        props.append(" " * prop_indent + "PaddingLeft: =8\n")
                    elif pl.lstrip().startswith("PaddingRight:"):
                        props.append(" " * prop_indent + "PaddingRight: =8\n")
                    elif pl.lstrip().startswith("PaddingBottom:"):
                        props.append(" " * prop_indent + "PaddingBottom: =3\n")
                    else:
                        props.append(pl)
                    i += 1
                if prop_indent is None:
                    prop_indent = row_indent + 4
                joined = "".join(props)
                if "PaddingBottom:" not in joined:
                    props.append(" " * prop_indent + "PaddingBottom: =3\n")
                if "PaddingLeft:" not in joined:
                    props.append(" " * prop_indent + "PaddingLeft: =8\n")
                if "PaddingRight:" not in joined:
                    props.append(" " * prop_indent + "PaddingRight: =8\n")
                out.extend(props)
                continue
            out.append(cur)
            i += 1
    return out


def add_datepicker_sizes(all_lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(all_lines):
        line = all_lines[i]
        out.append(line)
        i += 1
        if "Control: Classic/DatePicker@" not in line:
            continue
        # Consume until Properties, then ensure Size
        while i < len(all_lines):
            cur = all_lines[i]
            out.append(cur)
            i += 1
            if not cur.lstrip().startswith("Properties:"):
                continue
            props: list[str] = []
            prop_indent = None
            has_size = False
            while i < len(all_lines):
                pl = all_lines[i]
                if pl.strip() and prop_indent is None:
                    # first content line under Properties
                    if pl.lstrip().startswith("Children:") or pl.lstrip().startswith("- "):
                        break
                    prop_indent = len(pl) - len(pl.lstrip(" "))
                if pl.strip() and prop_indent is not None:
                    pindent = len(pl) - len(pl.lstrip(" "))
                    if pindent < prop_indent:
                        break
                    if pl.lstrip().startswith("Children:") or pl.lstrip().startswith("- "):
                        break
                if pl.lstrip().startswith("Size:"):
                    has_size = True
                    props.append(" " * (prop_indent or 0) + "Size: =9\n")
                else:
                    props.append(pl)
                i += 1
            if prop_indent is None:
                prop_indent = 48
            if not has_size:
                inserted = False
                new_props: list[str] = []
                for p in props:
                    new_props.append(p)
                    if (not inserted) and p.lstrip().startswith("Font:"):
                        new_props.append(" " * prop_indent + "Size: =9\n")
                        inserted = True
                if not inserted:
                    new_props.insert(0, " " * prop_indent + "Size: =9\n")
                props = new_props
            out.extend(props)
            break
    return out


for body in ("det_basics_body", "det_people_body"):
    s, e = find_range(body)
    lines = lines[:s] + fix_body(lines[s:e]) + lines[e:]
    print(f"fixed {body}")

lines = add_datepicker_sizes(lines)
path.write_text("".join(lines), encoding="utf-8")
print(f"wrote {path}")
