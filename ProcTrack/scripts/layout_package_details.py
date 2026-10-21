"""Keep Package Details stage columns inside the path-to-award row."""

from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "src" / "Src" / "Package Details.pa.yaml"

# portion, or a fixed width when portion is 0
HEADER = [(17, None), (13, None), (18, None), (18, None), (18, None), (15, None)]
STAGE = [
    (17, None),
    (8, None),
    (0, 16),
    (0, 36),
    (18, None),
    (18, None),
    (18, None),
    (0, 20),
    (15, None),
]
ONSITE = [
    (17, None),
    (8, None),
    (0, 16),
    (0, 36),
    (18, None),
    (18, None),
    (18, None),
    (15, None),
]
ROWS = {
    "Container11": HEADER,
    "Container20": STAGE,
    "Container20_1": STAGE,
    "Container20_2": STAGE,
    "Container20_3": STAGE,
    "Container20_4": STAGE,
    "Container20_5": ONSITE,
}


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def block_end(lines: list[str], start: int, base_indent: int) -> int:
    i = start + 1
    while i < len(lines):
        if lines[i].strip() and indent_of(lines[i]) <= base_indent:
            return i
        i += 1
    return len(lines)


def direct_children(lines: list[str], children_line: int, child_indent: int, end: int) -> list[int]:
    found = []
    i = children_line + 1
    while i < end:
        if lines[i].strip() and indent_of(lines[i]) == child_indent and lines[i].lstrip().startswith("- "):
            found.append(i)
        i += 1
    return found


def strip_position(lines: list[str], prop_start: int, prop_end: int, prop_indent: int) -> int:
    i = prop_start
    while i < prop_end:
        if lines[i].strip() and indent_of(lines[i]) == prop_indent:
            key, _, val = lines[i].strip().partition(":")
            if key in {"Width", "X", "Y"}:
                del lines[i]
                prop_end -= 1
                if val.strip() in {"|", "|-", "|+"}:
                    while i < prop_end and (not lines[i].strip() or indent_of(lines[i]) > prop_indent):
                        del lines[i]
                        prop_end -= 1
                continue
        i += 1
    return prop_end


def set_prop(lines: list[str], prop_start: int, prop_end: int, prop_indent: int, key: str, value: str) -> int:
    prefix = " " * prop_indent + key + ":"
    for i in range(prop_start, prop_end):
        if lines[i].startswith(prefix):
            lines[i] = f"{prefix} {value}\n"
            return prop_end
    lines.insert(prop_end, f"{prefix} {value}\n")
    return prop_end + 1


def convert_row(lines: list[str], name: str, spec: list[tuple[int, int | None]]) -> None:
    start = next(i for i, line in enumerate(lines) if line.strip() == f"- {name}:")
    row_indent = indent_of(lines[start])
    end = block_end(lines, start, row_indent)
    props = next(i for i in range(start, end) if lines[i].startswith(" " * (row_indent + 4) + "Properties:"))
    children = next(i for i in range(props, end) if lines[i].startswith(" " * (row_indent + 4) + "Children:"))
    prop_indent = row_indent + 6
    for key, value in (
        ("LayoutGap", "=4"),
        ("LayoutMinWidth", "=0"),
        ("LayoutMinHeight", "=0"),
    ):
        children = set_prop(lines, props + 1, children, prop_indent, key, value)
        end = block_end(lines, start, row_indent)
    kids = direct_children(lines, children, row_indent + 6, end)
    if len(kids) != len(spec):
        raise SystemExit(f"{name} has {len(kids)} children, expected {len(spec)}")
    for kid, (portion, fixed) in reversed(list(zip(kids, spec))):
        kid_indent = indent_of(lines[kid])
        kid_end = block_end(lines, kid, kid_indent)
        kprops = next(i for i in range(kid, kid_end) if lines[i].startswith(" " * (kid_indent + 4) + "Properties:"))
        kchildren = None
        for i in range(kprops + 1, kid_end):
            if lines[i].startswith(" " * (kid_indent + 4) + "Children:"):
                kchildren = i
                break
        prop_end = kchildren if kchildren is not None else kid_end
        prop_end = strip_position(lines, kprops + 1, prop_end, kid_indent + 6)
        prop_end = set_prop(lines, kprops + 1, prop_end, kid_indent + 6, "FillPortions", f"={portion}")
        prop_end = set_prop(lines, kprops + 1, prop_end, kid_indent + 6, "LayoutMinWidth", "=0")
        if fixed is not None:
            set_prop(lines, kprops + 1, prop_end, kid_indent + 6, "Width", f"={fixed}")


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    text = text.replace("Control: ModernCombobox@1.1.0", "Control: ModernCombobox@1.1.2")
    lines = text.splitlines(keepends=True)
    # Process later rows first so earlier indexes stay valid.
    for name in reversed(list(ROWS)):
        convert_row(lines, name, ROWS[name])
    PATH.write_text("".join(lines), encoding="utf-8")
    print("grid updated")


if __name__ == "__main__":
    main()
