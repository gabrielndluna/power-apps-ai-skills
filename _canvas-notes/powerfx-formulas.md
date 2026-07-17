# Power Fx formula gotchas (validated)

## SortByColumns / Sort — use SortOrder enum

Always qualify sort direction:

```powerfx
SortByColumns(col, "ColumnName", SortOrder.Ascending)
SortByColumns(col, "ColumnName", SortOrder.Descending)
Sort(col, ColumnName, SortOrder.Ascending)
```

Bare `Ascending` / `Descending` is **invalid** — Studio error:  
`Name isn't valid. 'Ascending' isn't recognized` (expects `SortOrder.Ascending`).

## Confirm dialogs — prefer custom overlay in Canvas

`Confirm(Message, {Title: "..."})` often falls back to the **browser** confirm in Studio / hosted authoring. Browsers force a host line like:

> An embedded page at authoring.*.powerapps.com says:

That host text **cannot** be replaced. Title options do not override it.

For titled warnings (e.g. Approve All without date filter):

1. `Set(varShowMyDialog, true)` on the action button
2. Full-screen `GroupContainer` overlay (`Visible: =varShowMyDialog`) with card title + message + Cancel/Confirm buttons
3. Confirm runs the real action; Cancel only clears the flag

Init `Set(varShowMyDialog, false)` in `App.OnStart`.

## Bulk SharePoint updates — Patch(table), not ForAll(Patch(LookUp))

Slow (N LookUps + N Patches):

```powerfx
ForAll(
    colRows As TargetRow,
    Patch(List, LookUp(List, ID = TargetRow.ID), { Status: "Approved" })
)
```

Fast (one Patch with ID + changed columns only):

```powerfx
ClearCollect(
    colRows,
    ForAll(
        Filter(colLocal, Status = "Pending" /* + same gallery filters */) As TargetRow,
        { ID: TargetRow.ID, Status: "Approved" }
    )
);
Patch(List, colRows)
```

There is no SharePoint “update where” from Canvas. Always filter a **local** collection (same rules as the gallery), then bulk `Patch`. Used for Staffclock Approve All (weekly + daily) and week row Approve/Reject.
