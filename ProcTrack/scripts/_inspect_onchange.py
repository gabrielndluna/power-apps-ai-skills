from pathlib import Path

for name in ["Welcome screen.pa.yaml", "Package Details.pa.yaml", "Create New Package.pa.yaml"]:
    text = (Path("src/Src") / name).read_text(encoding="utf-8")
    idx = text.find("colUserPermissions")
    print("====", name, "idx", idx)
    if idx < 0:
        print("no colUserPermissions")
        continue
    start = text.rfind("OnChange:", 0, idx)
    # end at next property line after the quoted string closes
    # find the closing " that ends the OnChange value - after Edit_allowed
    end = text.find('"\n', idx)
    snippet = text[start : end + 1]
    print("start", start, "end", end, "len", len(snippet))
    print(repr(snippet[:200]))
    print("---")
    print(repr(snippet[-120:]))
    Path(f"_onchange_{name.replace(' ', '_')}.txt").write_text(snippet, encoding="utf-8")
