"""Remove accidental padding on nested controls; keep spacing only on rows."""
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


def clean_body(chunk: list[str]) -> list[str]:
    """Keep Padding* only on det_row_* Properties; strip from nested controls/cols."""
    out: list[str] = []
    i = 0
    while i < len(chunk):
        line = chunk[i]
        is_row = any(line.lstrip().startswith(f"- {rn}:") for rn in ROW_NAMES)
        out.append(line)
        i += 1
        if not is_row:
            # strip padding from any non-row property blocks we encounter at top of body? 
            # handled below when walking nested under rows; also strip cols/labels outside
            continue

        row_indent = len(line) - len(line.lstrip(" "))
        saw_row_props = False
        while i < len(chunk):
            cur = chunk[i]
            if cur.lstrip().startswith("- ") and (len(cur) - len(cur.lstrip(" "))) == row_indent:
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
                    props.append(pl)
                    i += 1

                if not saw_row_props:
                    # first Properties = the row itself — ensure correct paddings
                    saw_row_props = True
                    if prop_indent is None:
                        prop_indent = row_indent + 4
                    cleaned: list[str] = []
                    for p in props:
                        s = p.lstrip()
                        if s.startswith("PaddingLeft:"):
                            cleaned.append(" " * prop_indent + "PaddingLeft: =8\n")
                        elif s.startswith("PaddingRight:"):
                            cleaned.append(" " * prop_indent + "PaddingRight: =8\n")
                        elif s.startswith("PaddingBottom:"):
                            cleaned.append(" " * prop_indent + "PaddingBottom: =3\n")
                        elif s.startswith("PaddingTop:"):
                            continue  # drop
                        else:
                            cleaned.append(p)
                    joined = "".join(cleaned)
                    if "PaddingLeft:" not in joined:
                        cleaned.append(" " * prop_indent + "PaddingLeft: =8\n")
                    if "PaddingRight:" not in joined:
                        cleaned.append(" " * prop_indent + "PaddingRight: =8\n")
                    if "PaddingBottom:" not in joined:
                        cleaned.append(" " * prop_indent + "PaddingBottom: =3\n")
                    out.extend(cleaned)
                else:
                    # nested Properties (cols, labels, inputs) — strip Padding*
                    for p in props:
                        s = p.lstrip()
                        if s.startswith("PaddingLeft:") or s.startswith("PaddingRight:") or s.startswith(
                            "PaddingBottom:"
                        ) or s.startswith("PaddingTop:"):
                            # keep PaddingLeft: =8 on readonly value fills that already had content padding
                            if s.startswith("PaddingLeft: =8") and "Fill:" in "".join(props):
                                # ambiguous — keep only classic content PaddingLeft: =8 on value labels
                                # Heuristic: if this block looks like a value label (has Fill grey or TextInput)
                                pass
                            if s.startswith("PaddingLeft: =8\n") or s.startswith("PaddingLeft: =8"):
                                # preserve horizontal text inset on filled labels / text inputs only
                                block = "".join(props)
                                if (
                                    "Fill: =RGBA(220, 224, 226, 1)" in block
                                    or "Control: Classic/TextInput" in "".join(out[-8:])
                                    or "TextInput@" in "".join(out[-8:])
                                ):
                                    out.append(p)
                                    continue
                            continue
                        out.append(p)
                continue

            out.append(cur)
            i += 1
    return out


def strip_nested_padding_simple(chunk: list[str]) -> list[str]:
    """Second pass: within bodies, remove PaddingLeft/Right/Bottom from anything that is NOT a det_row_*."""
    out: list[str] = []
    i = 0
    current_owner = None  # 'row' | 'other'
    prop_indent = None
    in_props = False
    owner_indent = None

    while i < len(chunk):
        line = chunk[i]
        stripped = line.lstrip()
        indent = len(line) - len(line.lstrip(" "))

        if stripped.startswith("- "):
            name = stripped[2:].split(":")[0]
            if name in ROW_NAMES:
                current_owner = "row"
                owner_indent = indent
            else:
                current_owner = "other"
                owner_indent = indent
            in_props = False
            prop_indent = None
            out.append(line)
            i += 1
            continue

        if stripped.startswith("Properties:"):
            in_props = True
            prop_indent = None
            out.append(line)
            i += 1
            continue

        if in_props:
            if stripped.startswith("Children:"):
                in_props = False
                out.append(line)
                i += 1
                continue
            if stripped and prop_indent is None:
                prop_indent = indent
            if stripped and prop_indent is not None and indent < prop_indent:
                in_props = False
                # fall through to reprocess
                continue

            if current_owner == "other" and (
                stripped.startswith("PaddingLeft:")
                or stripped.startswith("PaddingRight:")
                or stripped.startswith("PaddingBottom:")
                or stripped.startswith("PaddingTop:")
            ):
                # Keep only PaddingLeft: =8 on grey readonly value labels and text inputs
                keep = False
                if stripped.startswith("PaddingLeft: =8"):
                    # look ahead/back in out for Fill grey or we'll check next few - use lookback
                    lookback = "".join(out[-20:])
                    if "Fill: =RGBA(220, 224, 226, 1)" in lookback:
                        keep = True
                    # TextInput PaddingLeft often set with other props before PaddingLeft in file order
                    # For TextInputs PaddingLeft comes after Default etc; keep all PaddingLeft: =8 under TextInput
                    if "TextInput@" in lookback or "Classic/TextInput" in lookback:
                        keep = True
                if not keep:
                    i += 1
                    continue

            out.append(line)
            i += 1
            continue

        out.append(line)
        i += 1

    return out


for body in ("det_basics_body", "det_people_body"):
    s, e = find_range(body)
    cleaned = strip_nested_padding_simple(lines[s:e])
    lines = lines[:s] + cleaned + lines[e:]
    print(f"cleaned {body}")

# Ensure DatePickers still have Size: =9 and no bogus paddings
text = "".join(lines)
path.write_text(text, encoding="utf-8")

# verify sample
sample = path.read_text(encoding="utf-8")
# count PaddingBottom under det_l_sub
idx = sample.find("- det_l_sub:")
snippet = sample[idx : idx + 500]
print("--- det_l_sub snippet ---")
print(snippet)
idx2 = sample.find("- det_start:")
print("--- det_start snippet ---")
print(sample[idx2 : idx2 + 450])
