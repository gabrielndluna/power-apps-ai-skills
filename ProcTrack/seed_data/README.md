# ProcTrack seed data (new permission model)

## SharePoint columns

### ProcTrack - Permissions (1 row per user)

| Column | Type | Notes |
|---|---|---|
| Title | Single line text | email lowercase, unique |
| Name | Single line text | display name |
| IsAdmin | Yes/No | manage Users + Projects |
| Entra_ID | Single line text | Azure AD object id (optional; app can fill) |
| Edit_Projects | Multiple lines of text | `;`-separated **projectid** GUIDs |
| View_Projects | Multiple lines of text | `;`-separated **projectid** GUIDs |

Old columns to stop using: `Project`, `Edit_allowed` (and any one-row-per-project layout).

### ProcTrack - Packages

| Column | Type | Notes |
|---|---|---|
| ProjectID | Single line text | = Projects.projectid (GUID) |
| projectidentifier | text | keep for display / legacy |

## How to load

1. Projects already has `projectid` (done).
2. Packages: add `ProjectID` if missing → import/update from `ProcTrack - Packages.csv`.
3. Permissions: import `ProcTrack - Permissions.csv` (43 users collapsed from Downloads export: Edit_allowed=yes → Edit_Projects; blank → View_Projects; IsAdmin if any old row was True).
4. Studio: refresh SharePoint connections for Permissions + Packages.

## projectid lookup

- `A02180` → `5bcbf3f3-f05e-41d4-b33c-0ed5a10e5a19` (DNNP)
- `A814` → `0307b3a6-0b62-42f9-a1ba-d5421d729930` (Aecon Hamilton LRT Partnership)
- `A819` → `bf395612-4879-43db-bad4-a718f6124afd` (Arctic Over the Horizon Radar)
- `9147` → `c94cd94d-5d8b-4ba5-99be-e2558fe6e5c2` (North End Connectors)
- `A502` → `91be07a2-5885-43e0-8ec3-1551dfccde1d` (ECWE Elevated Guideway)

## Generated

- Packages: 636/636 rows got ProjectID
- Unmapped package identifiers: none
