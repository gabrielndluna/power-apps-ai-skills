# YAML pack & Studio import (validated 2026-07-08)

RoleFit incremental build confirmed these patterns. Update after each Studio import.

## What works

| Pattern | Notes |
|---------|--------|
| `pac canvas pack` without `--disable-load-from-yaml` | `packed.json` → `"LoadFromYaml": true` |
| Incremental screen adds | Home only (~37 KB) imported; full app (~49 KB) after fixes |
| Classic controls only in YAML packs | Buttons, galleries, GroupContainer AutoLayout |
| SharePoint-only seed | 9 `KI_*` lists on CivilPlanningteam |
| Screen names with spaces | `All Roles`, `Role Workspace`, `Talent Pool` |

## What breaks import (`ErrOpeningDocument_UnknownError`)

| Cause | Fix |
|-------|-----|
| Stale `*.msapr` with old connectors | Re-unpack from current seed before pack |
| `CanvasComponent` in YAML-only pack | Replace with `Classic/Button@2.2.0` until Studio-validated export |
| `--disable-load-from-yaml` on pack | Never use; Studio ignores `Src/*.pa.yaml` |
| Large jump in screens/components at once | Bisect; test import after each step |
| Unicode in formula strings | Use ASCII (`Y`, `~`, `-`) in display text |

## ProcTrack vs RoleFit pack

| | ProcTrack `app.msapp` | RoleFit before Studio save |
|--|----------------------|----------------------------|
| Size | ~550 KB | ~35–50 KB |
| `Controls/*.json` | Compiled screens | Only seed `Screen1` stub |
| `Components/*.json` | Compiled | None (YAML components fail) |
| Import | Works immediately | Needs incremental build + classic controls |

ProcTrack was **opened and saved in Studio** after pack. That compiles YAML → Controls.

## User seed requirements

- Blank canvas app + SharePoint lists connected
- **Remove unused connectors** in Data panel (e.g. Office 365 Users) before export
- Deleting Screen1 controls is fine; removing **connections** requires re-export
- No need to build screens in Studio — agent builds YAML

## Bisect packages (debug only)

When import fails, pack subsets to isolate the screen:

```powershell
pac canvas pack --sources ./src_subset --msapp ./app_test.msapp --layout SourceCode --overwrite
```

Do not commit `src_bisect_*` or `app_*.msapp` test artifacts.

## Related

- Agent skill: `.cursor/skills/canvas-yaml-pack/SKILL.md`
- Import steps: `RoleFit/IMPORT_INSTRUCTIONS.md`
- Layout: `layout-autolayout.md`
