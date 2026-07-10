# RoleFit import instructions

## Quick path

1. Import **`RoleFit/app.msapp`** in Power Apps Studio (File → Open → Browse)
2. Authorize **SharePoint** (CivilPlanningteam / 9 `KI_*` lists)
3. Wait for YAML compile (1–2 min on first open)
4. **Save** and **Publish**

## Seed data

Import CSVs from `lists_csv_exports/seed_data/` before functional testing (see `seed_data/README.md`).

## Test accounts

| Email | Role |
|-------|------|
| `gduarteluna@aecon.com` | Creator + sponsor |
| `kpunno@aecon.com` | Creator / assessor |
| `tnierodzik@aecon.com` | Executive sponsor only |

## If import fails

See `_canvas-notes/yaml-pack-import.md` and `.cursor/skills/canvas-yaml-pack/SKILL.md`.

Common fixes:
- Re-export seed after changing Data connections → replace `RoleFit.msapp` → agent re-unpacks
- `ErrOpeningDocument_UnknownError` after large YAML change → import previous working `app.msapp`, then smaller incremental pack

## After successful import

**File → Save as → This computer** → `RoleFit-validated.msapp` (optional; speeds future imports).
