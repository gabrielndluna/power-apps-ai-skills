"""Turn the Welcome package header and gallery row into aligned AutoLayout columns."""

from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "src" / "Src" / "Welcome screen.pa.yaml"
text = PATH.read_text(encoding="utf-8")
lines = text.splitlines(keepends=True)

HEADER_PORTIONS = {
    "header_package": 12,
    "header_description": 16,
    "header_stage": 12,
    "header_stage_due": 10,
    "header_lead": 16,
    "variable_header_1": 9,
    "variable_header_2": 9,
    "variable_header_3": 9,
    "variable_header_4": 9,
}
HEADER_ORDER = [
    "header_package",
    "header_description",
    "header_stage",
    "header_stage_due",
    "header_lead",
    "variable_header_1",
    "variable_header_2",
    "variable_header_3",
    "variable_header_4",
]
ROW_PORTIONS = {
    "gallery_package": 12,
    "gallery_description": 16,
    "gallery_current_stage": 12,
    "gallery_due": 10,
    "gallery_lead": 8,
    "opslead": 8,
    "variable_row_1": 9,
    "variable_row_2": 9,
    "variable_row_3": 9,
    "variable_row_4": 9,
    "gallery_arrow_details": 0,
}
ROW_ORDER = [
    "gallery_package",
    "gallery_description",
    "gallery_current_stage",
    "gallery_due",
    "gallery_lead",
    "opslead",
    "variable_row_1",
    "variable_row_2",
    "variable_row_3",
    "variable_row_4",
    "gallery_arrow_details",
]
HIDE = {
    "Separator24",
    "gallery_row_bg",
    "Circle2",
    "lead_image",
    "opslead_image",
    "gallery_status_label",
}


def block_name(block):
    first = block[0].lstrip()
    return first.split(":", 1)[0].lstrip("- ").strip()


def split_blocks(start, end, marker_prefix):
    indexes = [i for i in range(start, end) if lines[i].startswith(marker_prefix)]
    blocks = {}
    for n, i in enumerate(indexes):
        j = indexes[n + 1] if n + 1 < len(indexes) else end
        name = block_name(lines[i:j])
        blocks[name] = lines[i:j]
    return blocks


def strip_xy_width(block):
    kept = []
    for line in block:
        stripped = line.strip()
        if stripped.startswith("X:") or stripped.startswith("Y:") or stripped.startswith("Width:"):
            continue
        kept.append(line)
    return kept


def ensure_props(block, extra_lines, indent):
    # Insert before the last line if the block ends at the next sibling; props sit under Properties.
    # Append extra property lines just before the block ends, at the Properties indent.
    out = strip_xy_width(block)
    existing = "".join(out)
    for extra in extra_lines:
        key = extra.strip().split(":", 1)[0]
        if f"{key}:" not in existing:
            out.append(f"{indent}{extra}\n")
    return out


# --- header children ---
header_children = next(i for i, line in enumerate(lines) if line.startswith("                      Children:") and i > 0 and "headers_container" in "".join(lines[max(0, i - 20):i]))
gallery_line = next(i for i, line in enumerate(lines) if line.startswith("                  - Gallery2:"))
header_blocks = split_blocks(header_children + 1, gallery_line, "                        - ")
header_indent = "                          "
new_header = []
for name in HEADER_ORDER:
    block = header_blocks[name]
    extras = [
        f"FillPortions: ={HEADER_PORTIONS[name]}",
        "Height: =32",
        "LayoutMinWidth: =0",
        "PaddingBottom: =0",
        "PaddingLeft: =0",
        "PaddingRight: =4",
        "PaddingTop: =0",
        "Wrap: =true",
    ]
    new_header.extend(ensure_props(block, extras, header_indent))
new_header.append(
    "                        - header_arrow_gap:\n"
    "                            Control: Label@2.5.1\n"
    "                            Properties:\n"
    "                              FillPortions: =4\n"
    "                              Height: =32\n"
    "                              LayoutMinWidth: =0\n"
    "                              Text: =\"\"\n"
)
lines[header_children + 1:gallery_line] = new_header

# Recompute gallery children start after the replacement.
text_mid = "".join(lines)
lines = text_mid.splitlines(keepends=True)
gallery_children = None
for i, line in enumerate(lines):
    if line.startswith("                  - Gallery2:"):
        for j in range(i, len(lines)):
            if lines[j].startswith("                      Children:"):
                gallery_children = j
                break
        break
if gallery_children is None:
    raise SystemExit("gallery children not found")

row_blocks = split_blocks(gallery_children + 1, len(lines), "                        - ")
missing = [n for n in ROW_ORDER if n not in row_blocks]
if missing:
    raise SystemExit(f"missing row controls: {missing}")

prop_indent = "                                  "
row_parts = []
for name in ROW_ORDER:
    extras = [
        f"FillPortions: ={ROW_PORTIONS[name]}",
        "LayoutMinWidth: =0",
        "PaddingBottom: =0",
        "PaddingLeft: =0",
        "PaddingRight: =0",
        "PaddingTop: =0",
    ]
    if name == "gallery_description":
        extras += ["Height: =40", "Wrap: =true", "VerticalAlign: =VerticalAlign.Top"]
    elif name == "gallery_arrow_details":
        extras += ["Height: =28", "Width: =28"]
    elif name == "gallery_package":
        extras += ["Height: =36", "Wrap: =true", "VerticalAlign: =VerticalAlign.Top"]
    else:
        extras += ["Height: =36", "Wrap: =true"]
    block = ensure_props(row_blocks[name], extras, prop_indent)
    # Re-indent the block from 24 spaces to 32 spaces (8 more).
    shifted = []
    for line in block:
        if line.strip() == "":
            shifted.append(line)
        else:
            shifted.append("        " + line)
    row_parts.extend(shifted)

status = row_blocks.get("gallery_status_label")
status_out = []
if status:
    status = strip_xy_width(status)
    status = ensure_props(
        status,
        [
            "Height: =20",
            "LayoutMinWidth: =0",
            "PaddingBottom: =0",
            "PaddingLeft: =8",
            "PaddingRight: =8",
            "PaddingTop: =0",
            "Size: =10",
            "Wrap: =true",
            "Width: =Parent.Width",
        ],
        "                              ",
    )
    for line in status:
        status_out.append("    " + line if line.strip() else line)

card = []
card.append("                        - gallery_card:\n")
card.append("                            Control: GroupContainer@1.5.0\n")
card.append("                            Variant: AutoLayout\n")
card.append("                            Properties:\n")
card.append("                              DropShadow: =DropShadow.None\n")
card.append("                              Height: =Parent.TemplateHeight\n")
card.append("                              LayoutDirection: =LayoutDirection.Vertical\n")
card.append("                              LayoutGap: =2\n")
card.append("                              LayoutMinHeight: =0\n")
card.append("                              LayoutMinWidth: =0\n")
card.append("                              Width: =Parent.TemplateWidth\n")
card.append("                            Children:\n")
card.append("                              - gallery_row:\n")
card.append("                                  Control: GroupContainer@1.5.0\n")
card.append("                                  Variant: AutoLayout\n")
card.append("                                  Properties:\n")
card.append("                                    DropShadow: =DropShadow.None\n")
card.append("                                    FillPortions: =1\n")
card.append("                                    LayoutAlignItems: =LayoutAlignItems.Start\n")
card.append("                                    LayoutDirection: =LayoutDirection.Horizontal\n")
card.append("                                    LayoutGap: =6\n")
card.append("                                    LayoutMinHeight: =0\n")
card.append("                                    LayoutMinWidth: =0\n")
card.append("                                    PaddingLeft: =8\n")
card.append("                                    PaddingRight: =8\n")
card.append("                                    PaddingTop: =6\n")
card.append("                                  Children:\n")
card.extend(row_parts)
card.extend(status_out)

# TemplateSize bump
for i, line in enumerate(lines):
    if line.strip() == "TemplateSize: =75":
        lines[i] = line.replace("TemplateSize: =75", "TemplateSize: =88")
        break

lines[gallery_children + 1:] = card
PATH.write_text("".join(lines), encoding="utf-8")
print("rewrote", PATH)
