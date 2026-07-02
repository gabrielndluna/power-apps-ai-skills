# SharePoint delegation notes

Validated through ProcTrack (SharePoint lists, 500+ packages per tenant).  
Delegation limits how much data Power Apps fetches server-side; non-delegable filters cap at **2,000 rows** and can show wrong counts.

Official reference: [Understand delegation in a canvas app](https://learn.microsoft.com/en-us/power-platform/power-apps/delegation-overview)

## Delegable vs non-delegable (SharePoint connector)

| Delegable | Not delegable |
|-----------|---------------|
| `=`, `<>`, `<`, `>`, `<=`, `>=` on indexed columns | `in` with a collection (`projectidentifier in col.Project`) |
| `And`, `Or`, `Not` combining delegable clauses | `Search()`, most string functions (`Len`, `Mid`, …) |
| `StartsWith`, `EndsWith` (indexed text) | `CountRows(Filter(largeList, nonDelegableClause))` |
| `IsBlank` on some column types | `AddColumns` + filter on computed column against source |
| Date compare: `colDate < Today()` | `in` / `exactin` against multi-value without index |

Always check **Settings → Upcoming features → Data row limits** and the blue-underline warning in Studio formulas.

## ProcTrack pattern: preload, then filter locally

Permissions are a **small** collection (`colUserPermissions`). Packages are **large**.  
Do **not** filter packages with `projectidentifier in colUserPermissions.Project` — that `in` is not delegable.

### OnStart / screen refresh (delegable)

Run one **equality** filter per permitted project (delegable), merge into local collections:

```powerfx
ClearCollect(
    colPermittedProjects,
    ForAll(
        colUserPermissions As perm,
        LookUp('ProcTrack - Projects', projectidentifier = perm.Project)
    )
);

ClearCollect(colPermittedPackages, Blank());
ForAll(
    colUserPermissions As perm,
    Collect(
        colPermittedPackages,
        Filter('ProcTrack - Packages', projectidentifier = perm.Project)
    )
);
```

- `LookUp(..., projectidentifier = perm.Project)` — delegable  
- `Filter('ProcTrack - Packages', projectidentifier = perm.Project)` — delegable  
- `ForAll` over permissions runs N small server queries (N = user's project count, typically &lt; 20)

Refresh `colPermittedPackages` on **Project Dashboard `OnVisible`** so counts stay current after edits elsewhere.

### UI formulas (local collections — no delegation cap)

| Use case | Formula |
|----------|---------|
| KPI total packages | `CountRows(colPermittedPackages)` |
| KPI awarded | `CountRows(Filter(colPermittedPackages, !IsBlank(actualawarddate)))` |
| KPI needs attention | `CountRows(Filter(colPermittedPackages, IsBlank(actualawarddate) && !IsBlank(revisedplannedawarddate) && (revisedplannedawarddate < Today() \|\| (revisedplannedawarddate >= Today() && revisedplannedawarddate <= Today() + 30))))` |
| Active projects KPI | `CountRows(colPermittedProjects)` |
| Project gallery items | `colPermittedProjects` (+ local `Filter` for search text) |
| Card metric (per project) | `CountRows(Filter(colPermittedPackages, projectidentifier = ThisItem.projectidentifier && …))` |
| Project combobox items | `AddColumns(colPermittedProjects, Display, projectname)` |
| Welcome package grid | `Filter(colProjectPackages, …)` — already local after `ClearCollect` |

Search (`_q in projectname`) on a **local** collection is fine — delegation only applies to connector sources.

### Single-project fetch (delegable)

When the user picks one project:

```powerfx
ClearCollect(
    colProjectPackages,
    Filter('ProcTrack - Packages', projectidentifier = Self.Selected.projectidentifier)
);
```

Equality on `projectidentifier` is delegable. Prefer reusing `Filter(colPermittedPackages, projectidentifier = …)` when the collection is already warm.

## Anti-patterns we removed

```powerfx
// BAD — non-delegable; silently truncates at 2000 packages
CountRows(Filter('ProcTrack - Packages', projectidentifier in colUserPermissions.Project))

// BAD — 4 metrics × N gallery cards = 4N server round-trips per render
CountRows(Filter('ProcTrack - Packages', projectidentifier = ThisItem.projectidentifier))
```

## When preloading is not enough

If a user has many projects and package volume exceeds comfortable memory:

1. Keep dashboard KPIs on `colPermittedPackages` (refresh on visible).
2. Load `colProjectPackages` only when a project is opened (already done).
3. Consider SharePoint indexed columns for any remaining server-side filters.
4. For very large tenants, evaluate Dataverse or a view narrowed in SharePoint.

## Checklist for new formulas

1. Is the data source SharePoint (or another connector with limits)?
2. Does the filter use only delegable operators?
3. If not delegable, can you `ClearCollect` once and filter the collection in the UI?
4. For gallery templates, avoid repeated `Filter` on the connector — use a preloaded collection.
5. After changes, open **App checker → Performance** and confirm no delegation warnings on hot paths.
