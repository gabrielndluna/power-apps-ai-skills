# RoleFit seed data

Import these CSVs into SharePoint **in this order**:

1. `KI_reference_guides.csv`
2. `KI_pillars.csv`
3. `KI_categories.csv`
4. `KI_guide_items.csv`
5. `KI_roles.csv`
6. `KI_role_requirements.csv`
7. `KI_candidates.csv`
8. `KI_role_candidates.csv`
9. `KI_attestations.csv`

## Test accounts

| Email | Role in seed data |
|-------|-------------------|
| `tnierodzik@aecon.com` | Executive sponsor — Pending role (ROLE-NUCLEAR-PD-001) |
| `gduarteluna@aecon.com` | Creator + sponsor on Searching role (ROLE-TRANSIT-001) |
| `kpunno@aecon.com` | Creator — created Transit role; sponsor on Filled role |

## Row counts

- 1 guide, 3 pillars, **33 categories**, **170 guide items** (from Nuclear Assessment Reference Guide Word doc)
- 3 roles (Pending / Searching / Filled)
- **12 role requirements** (Searching role sample only — re-seeded against new itemcodes)
- 4 candidates, 3 role-candidate links
- **0 attestations** (cleared — old itemcodes no longer valid; re-attest after import)

## Updated from Word guide (re-import these lists)

Replace SharePoint list data for:

1. `KI_categories.csv`
2. `KI_guide_items.csv`
3. `KI_role_requirements.csv` (sample for ROLE-TRANSIT-001)
4. `KI_attestations.csv` (empty — clear existing rows)

Unchanged: `KI_reference_guides`, `KI_pillars` (same 3 pillars), `KI_roles`, `KI_candidates`, `KI_role_candidates`
