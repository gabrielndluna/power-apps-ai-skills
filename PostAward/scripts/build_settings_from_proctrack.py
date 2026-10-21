"""Build PostAward Settings from ProcTrack Settings (Users + Projects only)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "ProcTrack" / "src" / "Src" / "Settings.pa.yaml"
OUT = ROOT / "PostAward" / "src" / "Src" / "Settings.pa.yaml"

lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)


def find_ctrl(name: str) -> int:
    key = f"- {name}:"
    for i, line in enumerate(lines):
        if line.lstrip().startswith(key):
            return i
    raise SystemExit(f"missing {name}")


def indent_of(i: int) -> int:
    return len(lines[i]) - len(lines[i].lstrip(" "))


def ctrl_end(start: int) -> int:
    base = indent_of(start)
    i = start + 1
    while i < len(lines):
        s = lines[i]
        if s.strip() == "":
            i += 1
            continue
        ind = indent_of(i)
        if ind <= base and s.lstrip().startswith("- "):
            return i
        if ind < base:
            return i
        i += 1
    return len(lines)


idx_tab = find_ctrl("set_tab_columns")
end_tab = ctrl_end(idx_tab)
idx_cols = find_ctrl("set_columns_panel")
end_cols = ctrl_end(idx_cols)
assert idx_tab < idx_cols

text = "".join(lines[:idx_tab] + lines[end_tab:idx_cols] + lines[end_cols:])
text = text.replace(
    'Set(varSettingsTab, If(varIsAdmin, "users", "columns"));',
    'Set(varSettingsTab, "users");',
)

old_close = """                                          Set(varSettingsEditProject, Blank());
                                          Reset(set_proj_id);
                                          Reset(set_proj_name);
                                          Reset(set_proj_code);
                                          Set(varShowProjectModal, false)"""

new_close = """                                          Clear(colPermittedPackages);
                                          ForAll(
                                              colPermittedProjects As p,
                                              Collect(
                                                  colPermittedPackages,
                                                  Filter(
                                                      'ProcTrack - Packages',
                                                      ProjectID = p.projectid || projectidentifier = p.projectidentifier
                                                  )
                                              )
                                          );
                                          Set(varSettingsEditProject, Blank());
                                          Reset(set_proj_id);
                                          Reset(set_proj_name);
                                          Reset(set_proj_code);
                                          Set(varShowProjectModal, false)"""

if old_close not in text:
    raise SystemExit("proj save close block not found")
text = text.replace(old_close, new_close, 1)

assert "set_tab_columns" not in text
assert "set_columns_panel" not in text
assert "set_users_panel" in text and "set_projects_panel" in text

OUT.write_text(text, encoding="utf-8")
print(f"wrote {OUT} lines={text.count(chr(10)) + 1}")
