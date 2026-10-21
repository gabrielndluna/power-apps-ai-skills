---
name: canvas-yaml-pack
description: >-
  Pack and import Power Apps Canvas apps from YAML source using pac canvas
  unpack/pack. Use when building or editing .pa.yaml screens, packing app.msapp,
  fixing ErrOpeningDocument_UnknownError, or validating incremental Studio imports.
  Also use when laying out form inputs, columns, or cards inside nested containers.
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

For a Studio export with newly added connectors, unpack to a temporary folder first and copy the refreshed `.msapr` into the working `src/` so current YAML edits are not overwritten. For Office 365 Users search formulas, follow `_canvas-notes/office365-users.md`. For SharePoint file upload/view UI, follow `_canvas-notes/attachments.md` (Form + ClassicAttachmentsEdit — do not fake attachments with Patch).

### Office 365 Users ComboBox (validated Staffclock YNSE)

People search ComboBoxes must use this exact pattern (do not "improve" it without Studio re-validation):

```powerfx
DisplayFields = ["DisplayName"]
SearchFields = ["DisplayName", "Mail"]   // only these two
Items =
If(
    !IsBlank(Trim(Self.SearchText)),
    ShowColumns(
        Office365Users.SearchUser(
            { searchTerm: Trim(Self.SearchText), top: 15 }
        ),
        Id, DisplayName, Mail, UserPrincipalName, Department
    )
)
```

Known failures:

- `DisplayFields = ["UserLabel"]` or any custom `AddColumns` label → search/display breaks
- `SearchFields` including `UserPrincipalName` → search stops returning results
- Calling `SearchUser` when `SearchText` is blank → noisy / empty behavior

OnChange should store `Lower(Coalesce(Selected.Mail, Selected.UserPrincipalName))` and filter **local collections** with `Lower(Employee) = varEmail`, not SharePoint directly. Full notes: `_canvas-notes/office365-users.md`.

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

### Form inputs inside nested containers (validated Dayaway YNSE, 2026-10-13)

Inputs were clipped and borders disappeared whenever a child was sized from a flexible parent. Studio confirmed the fix below. Follow it for every new text input, date picker, and card. Do not go back to `FillPortions` columns or `Width: =column.Width`.

What failed:

- `Width: =Parent.Width` on an input inside a column. Inside a nested column this is the **row** width, so the input is wider than its column and the column clips it.
- `Width: =wrap_EmpFirst.Width` when that column is flexible (`FillPortions: 1`, no explicit Width). The property is larger than the box on screen. Same clip.
- A card whose `Height` equals its row. AutoLayout clips children, so the card border and the checkbox disappear.

What works. The column is ManualLayout and has an explicit width, so `Parent.Width` inside it matches the drawn box. The input is 8px narrower than that box.

```
row   AutoLayout, horizontal, LayoutGap 12, Height 76
      LayoutMinWidth 0, LayoutMinHeight 0
  column   ManualLayout, Height 68
           Width: =(Parent.Width - 12) / 2
           no FillPortions
    label  X: =4  Y: =4   Height: =18  Width: =Parent.Width - 8
    input  X: =4  Y: =26  Height: =36  Width: =Parent.Width - 8
```

Two columns plus the 12px gap equal the row. One full-width column uses `Width: =Parent.Width` on the ManualLayout column, and the input is still `Parent.Width - 8`.

Cards in a row (Access checks): the row is taller than the card and has vertical padding. The card does not set a width; `FillPortions: 1` shares the row. The checkbox has no Width.

```
row    Height 64, PaddingTop 8, PaddingBottom 8, LayoutAlignItems Center
  card Height 40, FillPortions 1, LayoutMinWidth 0, LayoutMinHeight 0
    checkbox  Height 28, FillPortions 1, LayoutMinWidth 0, no Width
```

Full write-up: `_canvas-notes/layout-autolayout.md`.

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
- [ ] Form inputs sit inside a ManualLayout column with an explicit Width, inset by 8px. Do not size them from a flexible parent's .Width (see `_canvas-notes/layout-autolayout.md`)
- [ ] Large SharePoint loads are bounded by delegable date/status filters (see `_canvas-notes/delegation.md`)
- [ ] Attachment upload uses Form + ClassicAttachmentsEdit (see `_canvas-notes/attachments.md`)
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
