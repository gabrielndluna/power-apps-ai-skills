"""Tighten Subcontract Detail left-panel rows, inset field borders, center rollup bars."""
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src" / "Src" / "Subcontract Detail.pa.yaml"
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)


def find_control_range(control_name: str) -> tuple[int, int]:
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


def transform_body(chunk: list[str]) -> list[str]:
    text = "".join(chunk)
    text = text.replace("LayoutGap: =6\n", "LayoutGap: =4\n", 1)
    text = text.replace("PaddingBottom: =10\n", "PaddingBottom: =6\n", 1)
    text = text.replace("PaddingTop: =8\n", "PaddingTop: =6\n", 1)
    text = text.replace("Height: =52\n", "Height: =44\n")
    text = text.replace("LayoutMinHeight: =52\n", "LayoutMinHeight: =44\n")
    text = text.replace("Height: =34\n", "Height: =28\n")
    text = text.replace("Height: =14\n", "Height: =12\n")
    # Half-cols: keep sharing row width via FillPortions (set below).
    text = text.replace("Width: =(det_left.Width - 24) / 2\n", "Width: =Parent.Width\n")
    text = text.replace("Width: =det_left.Width - 24\n", "Width: =Parent.Width\n")

    clines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(clines):
        line = clines[i]
        is_row = any(line.lstrip().startswith(f"- {rn}:") for rn in ROW_NAMES)
        is_col = line.lstrip().startswith("- det_col_")
        out.append(line)
        i += 1
        if not (is_row or is_col):
            continue

        # Walk until Properties, then edit props until Children / sibling
        while i < len(clines):
            cur = clines[i]
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
                    props.append(pl)
                    i += 1
                if prop_indent is None:
                    prop_indent = (len(line) - len(line.lstrip(" "))) + 4

                joined = "".join(props)
                if is_row:
                    if "PaddingLeft:" not in joined:
                        props.append(" " * prop_indent + "PaddingLeft: =6\n")
                    else:
                        props = [
                            (" " * prop_indent + "PaddingLeft: =6\n")
                            if p.lstrip().startswith("PaddingLeft:")
                            else p
                            for p in props
                        ]
                    if "PaddingRight:" not in joined:
                        props.append(" " * prop_indent + "PaddingRight: =6\n")
                    else:
                        props = [
                            (" " * prop_indent + "PaddingRight: =6\n")
                            if p.lstrip().startswith("PaddingRight:")
                            else p
                            for p in props
                        ]
                if is_col:
                    # Two cols + gap 8 inside row with side padding 6+6.
                    rewritten = []
                    for p in props:
                        if p.lstrip().startswith("Width:"):
                            rewritten.append(
                                " " * prop_indent + "Width: =(Parent.Width - 20) / 2\n"
                            )
                        elif p.lstrip().startswith("FillPortions:"):
                            rewritten.append(" " * prop_indent + "FillPortions: =0\n")
                        else:
                            rewritten.append(p)
                    props = rewritten
                out.extend(props)
                break
            out.append(cur)
            i += 1
            # safety: stop if we hit a sibling control at same indent
            if cur.lstrip().startswith("- ") and (
                len(cur) - len(cur.lstrip(" "))
            ) == (len(line) - len(line.lstrip(" "))):
                break
    return out


b_start, b_end = find_control_range("det_basics_body")
p_start, p_end = find_control_range("det_people_body")
print(f"basics {b_start + 1}-{b_end} people {p_start + 1}-{p_end}")

new_basics = transform_body(lines[b_start:b_end])
# people starts after basics; rebuild carefully
lines = lines[:b_start] + new_basics + lines[b_end:]
# re-find people after basics rewrite (length may change)
p_start, p_end = find_control_range("det_people_body")
new_people = transform_body(lines[p_start:p_end])
lines = lines[:p_start] + new_people + lines[p_end:]


def center_bars(chunk_lines: list[str]) -> list[str]:
    """Make each *_bar Height 20 with AlignInContainer Center; fill Y=5 so track looks centered vs text."""
    out: list[str] = []
    i = 0
    while i < len(chunk_lines):
        line = chunk_lines[i]
        is_bar = (
            line.lstrip().startswith("- det_rs_") or line.lstrip().startswith("- det_rr_")
        ) and line.rstrip().endswith("_bar:")
        out.append(line)
        i += 1
        if not is_bar:
            continue
        # Process until Children of this bar, then fix fill Y
        while i < len(chunk_lines):
            cur = chunk_lines[i]
            if cur.lstrip().startswith("Properties:"):
                out.append(cur)
                i += 1
                props: list[str] = []
                prop_indent = None
                while i < len(chunk_lines):
                    pl = chunk_lines[i]
                    if pl.lstrip().startswith("Children:"):
                        break
                    if pl.strip() and prop_indent is None:
                        prop_indent = len(pl) - len(pl.lstrip(" "))
                    if pl.strip() and prop_indent is not None:
                        pindent = len(pl) - len(pl.lstrip(" "))
                        if pindent < prop_indent:
                            break
                    if pl.lstrip().startswith("Height:"):
                        props.append(" " * (prop_indent or 0) + "Height: =20\n")
                    else:
                        props.append(pl)
                    i += 1
                if prop_indent is None:
                    prop_indent = (len(line) - len(line.lstrip(" "))) + 4
                joined = "".join(props)
                if "AlignInContainer:" not in joined:
                    props.insert(0, " " * prop_indent + "AlignInContainer: =AlignInContainer.Center\n")
                out.extend(props)
                continue
            if cur.lstrip().startswith("Children:"):
                out.append(cur)
                i += 1
                # fix fill child Y inside this bar
                while i < len(chunk_lines):
                    pl = chunk_lines[i]
                    # next sibling of bar at same indent ends the bar
                    if pl.lstrip().startswith("- ") and (
                        len(pl) - len(pl.lstrip(" "))
                    ) == (len(line) - len(line.lstrip(" "))):
                        break
                    if pl.lstrip().startswith("Y:"):
                        indent = len(pl) - len(pl.lstrip(" "))
                        out.append(" " * indent + "Y: =5\n")
                        i += 1
                        continue
                    # Also add a track behind fill: inject before first fill child
                    if (
                        pl.lstrip().startswith("- det_")
                        and pl.rstrip().endswith("_fill:")
                        and "track_injected" not in "".join(out[-5:])
                    ):
                        fill_indent = len(pl) - len(pl.lstrip(" "))
                        fill_name = pl.lstrip()[2:].split(":")[0]  # det_rs_appr_fill
                        track_name = fill_name.replace("_fill", "_track")
                        pi = fill_indent + 4
                        track_block = [
                            " " * fill_indent + f"- {track_name}:\n",
                            " " * (fill_indent + 2) + "Control: Label@2.5.1\n",
                            " " * (fill_indent + 2) + "Properties:\n",
                            " " * pi + "Fill: =RGBA(236, 238, 240, 1)\n",
                            " " * pi + "Height: =10\n",
                            " " * pi + 'Text: =""\n',
                            " " * pi + "Width: =120\n",
                            " " * pi + "X: =0\n",
                            " " * pi + "Y: =5\n",
                        ]
                        out.extend(track_block)
                        # clear parent bar gray fill so only track shows at Y=5 — handled below
                        out.append(pl)
                        i += 1
                        continue
                    out.append(pl)
                    i += 1
                break
            out.append(cur)
            i += 1
            if cur.lstrip().startswith("- ") and (
                len(cur) - len(cur.lstrip(" "))
            ) == (len(line) - len(line.lstrip(" "))):
                break

    # Clear gray Fill on bar containers (track child owns the gray band)
    text = "".join(out)
    # Too broad if we replace all Height 10 fills — instead walk bars again
    return out


# Find rollup section bars by locating first det_rs_appr_bar through last det_rr_newscope_bar
def find_line(prefix: str) -> int:
    for i, line in enumerate(lines):
        if line.lstrip().startswith(prefix):
            return i
    raise SystemExit(f"missing {prefix}")


bar_start = find_line("- det_rs_appr:")
# end after det_rr_newscope block — find det_rr_newscope then next sibling at same indent
rr_start = find_line("- det_rr_newscope:")
base = len(lines[rr_start]) - len(lines[rr_start].lstrip(" "))
bar_end = len(lines)
for j in range(rr_start + 1, len(lines)):
    line = lines[j]
    if not line.strip():
        continue
    indent = len(line) - len(line.lstrip(" "))
    if indent <= base and line.lstrip().startswith("- "):
        bar_end = j
        break

print(f"bars region {bar_start + 1}-{bar_end}")


def transform_bars(chunk: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(chunk):
        line = chunk[i]
        name = line.lstrip()[2:].split(":")[0] if line.lstrip().startswith("- ") else ""
        is_bar = name.endswith("_bar") and (name.startswith("det_rs_") or name.startswith("det_rr_"))
        out.append(line)
        i += 1
        if not is_bar:
            continue

        bar_indent = len(line) - len(line.lstrip(" "))
        # consume until end of this bar control
        while i < len(chunk):
            cur = chunk[i]
            if cur.lstrip().startswith("- ") and (len(cur) - len(cur.lstrip(" "))) == bar_indent:
                break

            if cur.lstrip().startswith("Properties:"):
                out.append(cur)
                i += 1
                props: list[str] = []
                prop_indent = None
                while i < len(chunk):
                    pl = chunk[i]
                    if pl.lstrip().startswith("Children:"):
                        break
                    if pl.strip() and prop_indent is None:
                        prop_indent = len(pl) - len(pl.lstrip(" "))
                    if pl.strip() and prop_indent is not None:
                        pindent = len(pl) - len(pl.lstrip(" "))
                        if pindent < prop_indent:
                            break
                    if pl.lstrip().startswith("Height:"):
                        props.append(" " * prop_indent + "Height: =20\n")
                    elif pl.lstrip().startswith("Fill:"):
                        # transparent parent; gray track is a child
                        props.append(" " * prop_indent + "Fill: =RGBA(0, 0, 0, 0)\n")
                    elif pl.lstrip().startswith("AlignInContainer:"):
                        props.append(
                            " " * prop_indent + "AlignInContainer: =AlignInContainer.Center\n"
                        )
                    else:
                        props.append(pl)
                    i += 1
                if prop_indent is None:
                    prop_indent = bar_indent + 4
                if "AlignInContainer:" not in "".join(props):
                    props.insert(
                        0, " " * prop_indent + "AlignInContainer: =AlignInContainer.Center\n"
                    )
                out.extend(props)
                continue

            if cur.lstrip().startswith("Children:"):
                out.append(cur)
                i += 1
                # inject track then rewrite fill Y
                fill_seen = False
                while i < len(chunk):
                    pl = chunk[i]
                    if pl.lstrip().startswith("- ") and (len(pl) - len(pl.lstrip(" "))) == bar_indent:
                        break
                    if (
                        not fill_seen
                        and pl.lstrip().startswith("- ")
                        and "_fill:" in pl
                    ):
                        fill_indent = len(pl) - len(pl.lstrip(" "))
                        fill_name = pl.lstrip()[2:].split(":")[0]
                        track_name = fill_name.replace("_fill", "_track")
                        pi = fill_indent + 4
                        out.extend(
                            [
                                " " * fill_indent + f"- {track_name}:\n",
                                " " * (fill_indent + 2) + "Control: Label@2.5.1\n",
                                " " * (fill_indent + 2) + "Properties:\n",
                                " " * pi + "Fill: =RGBA(236, 238, 240, 1)\n",
                                " " * pi + "Height: =10\n",
                                " " * pi + 'Text: =""\n',
                                " " * pi + "Width: =120\n",
                                " " * pi + "X: =0\n",
                                " " * pi + "Y: =5\n",
                            ]
                        )
                        fill_seen = True
                        out.append(pl)
                        i += 1
                        continue
                    if fill_seen and pl.lstrip().startswith("Y:"):
                        indent = len(pl) - len(pl.lstrip(" "))
                        out.append(" " * indent + "Y: =5\n")
                        i += 1
                        continue
                    out.append(pl)
                    i += 1
                break

            out.append(cur)
            i += 1
    return out


new_bars = transform_bars(lines[bar_start:bar_end])
lines = lines[:bar_start] + new_bars + lines[bar_end:]

path.write_text("".join(lines), encoding="utf-8")
print(f"Wrote {path}")
