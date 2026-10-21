"""Convert Create New Package form rows to ManualLayout columns."""

from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "src" / "Src" / "Create New Package.pa.yaml"
ROWS = [
    "MainContainer6_5",
    "MainContainer6_1",
    "MainContainer6_2",
    "MainContainer6_3",
    "MainContainer6_4",
]


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def block_end(lines: list[str], start: int, base_indent: int) -> int:
    i = start + 1
    while i < len(lines):
        if lines[i].strip() and indent_of(lines[i]) <= base_indent:
            return i
        i += 1
    return len(lines)


def find_key(lines: list[str], start: int, end: int, key: str, key_indent: int) -> int:
    needle = " " * key_indent + key
    for i in range(start, end):
        if lines[i].startswith(needle):
            return i
    raise SystemExit(f"missing {key} between {start} and {end}")


def set_prop(lines: list[str], prop_start: int, prop_end: int, prop_indent: int, key: str, value: str) -> None:
    prefix = " " * prop_indent + key + ":"
    for i in range(prop_start, prop_end):
        if lines[i].startswith(prefix):
            lines[i] = f"{prefix} {value}\n" if value.startswith("=") else f"{prefix} {value}\n"
            return
    lines.insert(prop_end, f"{prefix} {value}\n")


def drop_props(lines: list[str], prop_start: int, prop_end: int, prop_indent: int, keys: set[str]) -> int:
    removed = 0
    i = prop_start
    while i < prop_end:
        stripped = lines[i].strip()
        key = stripped.split(":", 1)[0] if ":" in stripped else ""
        if indent_of(lines[i]) == prop_indent and key in keys:
            del lines[i]
            prop_end -= 1
            removed += 1
            continue
        i += 1
    return prop_end


def direct_children(lines: list[str], children_line: int, child_indent: int, end: int) -> list[int]:
    found = []
    i = children_line + 1
    while i < end:
        if lines[i].strip() and indent_of(lines[i]) == child_indent and lines[i].lstrip().startswith("- "):
            found.append(i)
        i += 1
    return found


def convert_row(lines: list[str], name: str) -> None:
    start = next(i for i, line in enumerate(lines) if line.strip() == f"- {name}:")
    row_indent = indent_of(lines[start])
    end = block_end(lines, start, row_indent)
    props = find_key(lines, start, end, "Properties:", row_indent + 4)
    children = find_key(lines, start, end, "Children:", row_indent + 4)
    prop_indent = row_indent + 6
    children = drop_props(
        lines,
        props + 1,
        children,
        prop_indent,
        {"LayoutWrap", "LayoutOverflowY", "X", "Y", "FillPortions"},
    )
    # children index shifted if we deleted lines before it; re-find
    end = block_end(lines, start, row_indent)
    children = find_key(lines, start, end, "Children:", row_indent + 4)
    for key, value in (
        ("LayoutGap", "=12"),
        ("LayoutMinHeight", "=0"),
        ("LayoutMinWidth", "=0"),
        ("Height", "=76"),
        ("PaddingBottom", "=4"),
        ("PaddingLeft", "=8"),
        ("PaddingRight", "=8"),
        ("PaddingTop", "=4"),
        ("LayoutAlignItems", "=LayoutAlignItems.Start"),
    ):
        set_prop(lines, props + 1, children, prop_indent, key, value)
        end = block_end(lines, start, row_indent)
        children = find_key(lines, start, end, "Children:", row_indent + 4)

    cols = direct_children(lines, children, row_indent + 6, end)
    count = len(cols)
    subtract = 16 + (count - 1) * 12
    if count == 1:
        width = "=Parent.Width - 16"
    else:
        width = f"=(Parent.Width - {subtract}) / {count}"

    # Convert from the end so inserts do not shift earlier column indexes.
    for col in reversed(cols):
        convert_column(lines, col, width)


def convert_column(lines: list[str], col: int, width: str) -> None:
    col_indent = indent_of(lines[col])
    end = block_end(lines, col, col_indent)
    variant = find_key(lines, col, end, "Variant:", col_indent + 4)
    lines[variant] = " " * (col_indent + 4) + "Variant: ManualLayout\n"
    props = find_key(lines, col, end, "Properties:", col_indent + 4)
    children_idx = None
    for i in range(props + 1, end):
        if lines[i].startswith(" " * (col_indent + 4) + "Children:"):
            children_idx = i
            break
    if children_idx is None:
        raise SystemExit(f"column {col} has no children")
    prop_indent = col_indent + 6
    children_idx = drop_props(
        lines,
        props + 1,
        children_idx,
        prop_indent,
        {
            "LayoutAlignItems",
            "LayoutDirection",
            "LayoutGap",
            "LayoutJustifyContent",
            "FillPortions",
            "AlignInContainer",
        },
    )
    end = block_end(lines, col, col_indent)
    for i in range(props + 1, end):
        if lines[i].startswith(" " * (col_indent + 4) + "Children:"):
            children_idx = i
            break
    for key, value in (
        ("Height", "=76"),
        ("LayoutMinHeight", "=0"),
        ("LayoutMinWidth", "=0"),
        ("Width", width),
    ):
        set_prop(lines, props + 1, children_idx, prop_indent, key, value)
        end = block_end(lines, col, col_indent)
        for i in range(props + 1, end):
            if lines[i].startswith(" " * (col_indent + 4) + "Children:"):
                children_idx = i
                break

    kids = direct_children(lines, children_idx, col_indent + 6, end)
    inputs_seen = 0
    classified = []
    for kid in kids:
        is_container = False
        look = kid + 1
        kid_end = block_end(lines, kid, indent_of(lines[kid]))
        while look < kid_end:
            if lines[look].strip().startswith("Control:"):
                is_container = "GroupContainer" in lines[look]
                break
            look += 1
        if is_container:
            classified.append((kid, "=4", "=20"))
        else:
            y = "=4" if inputs_seen == 0 else "=26"
            height = "=18" if inputs_seen == 0 else "=36"
            classified.append((kid, y, height))
            inputs_seen += 1
    for kid, y, height in reversed(classified):
        place_control(lines, kid, y=y, height=height, width="=Parent.Width - 8")


def place_control(lines: list[str], kid: int, y: str, height: str, width: str) -> None:
    kid_indent = indent_of(lines[kid])
    end = block_end(lines, kid, kid_indent)
    props = None
    children_idx = None
    for i in range(kid + 1, end):
        if lines[i].startswith(" " * (kid_indent + 4) + "Properties:"):
            props = i
        elif lines[i].startswith(" " * (kid_indent + 4) + "Children:"):
            children_idx = i
            break
    if props is None:
        return
    prop_end = children_idx if children_idx is not None else end
    prop_indent = kid_indent + 6
    prop_end = drop_props(lines, props + 1, prop_end, prop_indent, {"AlignInContainer", "Width"})
    end = block_end(lines, kid, kid_indent)
    children_idx = None
    for i in range(props + 1, end):
        if lines[i].startswith(" " * (kid_indent + 4) + "Children:"):
            children_idx = i
            break
    prop_end = children_idx if children_idx is not None else end
    for key, value in (
        ("X", "=4"),
        ("Y", y),
        ("Height", height),
        ("Width", width),
        ("LayoutMinWidth", "=0"),
        ("LayoutMinHeight", "=0"),
    ):
        set_prop(lines, props + 1, prop_end, prop_indent, key, value)
        end = block_end(lines, kid, kid_indent)
        children_idx = None
        for i in range(props + 1, end):
            if lines[i].startswith(" " * (kid_indent + 4) + "Children:"):
                children_idx = i
                break
        prop_end = children_idx if children_idx is not None else end


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = text.replace("Control: ModernCombobox@1.1.0", "Control: ModernCombobox@1.1.2")
    lines = text.splitlines(keepends=True)
    for name in ROWS:
        convert_row(lines, name)
    PATH.write_text("".join(lines), encoding="utf-8")
    print("updated", PATH)


if __name__ == "__main__":
    main()
