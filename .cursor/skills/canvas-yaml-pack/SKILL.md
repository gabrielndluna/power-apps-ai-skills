---
name: canvas-yaml-pack
description: >-
  Pack and import Power Apps Canvas apps from YAML source using pac canvas
  unpack/pack. Use when building or editing .pa.yaml screens, packing app.msapp,
  fixing ErrOpeningDocument_UnknownError, or validating incremental Studio imports.
---

# Canvas YAML pack workflow

Validated on **RoleFit** (2026-07-08) and **ProcTrack**. Read `_canvas-notes/yaml-pack-import.md` for failure modes.

## Workflow

1. **Seed** — user exports blank app with connectors only → `<App>/<App>.msapp`
2. **Unpack** — `pac canvas unpack --msapp <App>.msapp --sources <App>/src --layout SourceCode`
3. **Edit** — screens in `<App>/src/Src/*.pa.yaml`, update `_EditorState.pa.yaml`
4. **Pack** — `pac canvas pack --sources <App>/src --msapp <App>/app.msapp --layout SourceCode --overwrite`
   - Do **not** pass `--disable-load-from-yaml` (must stay `LoadFromYaml: true`)
5. **Import** — user opens `app.msapp` in Studio; authorize connectors; Save once

## Critical rules (learned the hard way)

### Refresh `RoleFit.msapr` after seed changes

`pac canvas pack` merges YAML with embedded metadata in `src/*.msapr`. If the user re-exports a seed (e.g. removed Office 365 Users), **re-unpack the seed** before packing. Stale `.msapr` injects phantom connectors → `ErrOpeningDocument_UnknownError`.

```powershell
pac canvas unpack --msapp RoleFit/RoleFit.msapp --sources RoleFit/src --layout SourceCode --overwrite
# then edit Src/*.pa.yaml and pack
```

### No CanvasComponents in YAML-only packs

`CanvasComponent` / custom component `.pa.yaml` files often fail Studio deserialization until the app is opened and saved once in Studio (which compiles components to `Components/*.json`).

**Until user provides a Studio-validated seed:**
- Use `Classic/Button@2.2.0` (and other classic controls) instead of `ButtonMain` etc.
- ProcTrack's distributable works because it was saved in Studio after pack.

### Incremental import strategy

When a large pack fails, bisect screens:

| Step | Add | Verify |
|------|-----|--------|
| 1 | `App.pa.yaml` OnStart + one screen shell | Import |
| 2 | + list screens (Home, All Roles) | Import |
| 3 | + heavy screen (Role Workspace) | Import |
| 4 | Full app | Import |

Round-trip test (unpack seed → pack unchanged) must pass before adding YAML.

### YAML content constraints

- Prefer **ASCII** in formula string literals (`Y`, `~`, `-` not `✓`, `◑`, `–`) — unicode caused import issues in Role Workspace compare matrix
- `AddColumns(col, attStatus, ...)` — column name is an **identifier**, not `"attStatus"` in quotes
- Screen names with spaces are OK (`All Roles`, `Role Workspace`)
- `_EditorState.pa.yaml` must list all screens; remove deleted screens (e.g. `Screen1`)

### Console noise vs real errors

- `csp.microsoft.com/report/PPUX-Hosting` **403** — ignore (CSP telemetry)
- Real import failure: Studio UI `ErrOpeningDocument_UnknownError` with session ID

## Pack checklist

```
- [ ] Fresh unpack from current seed (if connections changed)
- [ ] _EditorState lists all screens, no orphans
- [ ] No CanvasComponent unless Studio-validated seed exists
- [ ] packed.json has LoadFromYaml: true
- [ ] User tests import after each major screen addition
```

## Folder layout (per app)

```
<App>/
  <App>.msapp      # seed from Studio
  app.msapp        # packed output
  src/
    <App>.msapr    # from unpack — do not hand-edit
    Src/
      App.pa.yaml
      _EditorState.pa.yaml
      *.pa.yaml    # screens
```

## After first successful full import

User should **Save as** → `<App>-validated.msapp`. Future packs behave like ProcTrack (compiled Controls + YAML).
