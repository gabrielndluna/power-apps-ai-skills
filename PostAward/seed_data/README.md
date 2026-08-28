# PostAward seed data

Generated from ProcTrack Packages/Projects exports (awarded packages only).

## Import order (SharePoint)

1. Open list **PostAward - Subcontracts** → Integrate → Excel / or List settings → Import spreadsheet / or paste via Edit in grid view.
   Easiest: **Edit in grid view** → paste columns, or use **Import from Excel/CSV** if available in your tenant.
2. Then import **PostAward - Changes**.

## Columns to create / update (required for Detail feedback release)

### `PostAward - Subcontracts` — add these columns

| Internal name | Type | Choices / notes |
|---|---|---|
| `sapvendornumber` | Single line of text | |
| `revisedenddate` | Date and time (Date only) | Revised Subcontract End Date |
| `currencycode` | Choice | `CAD`, `USD` (default CAD). Do **not** name it `currency` (SharePoint Currency = number). |
| `indigenouscontribution` | Choice | `0`, `5`, `10`, `15`, `20`, `25`, `50`, `100` |
| `worktype` | Choice | `Boots on ground`, `Supply only`, `Consulting` |
| `operationalowner` | Single line of text | Display name |
| `operationalowneremail` | Single line of text | Lowercased mail/UPN for view access |

**Subcontract End Date** continues to use existing `completiondate` (UI label only).

### `PostAward - Changes` — add / update

| Internal name | Type | Notes |
|---|---|---|
| `datereceived` | Date | |
| `datefullyexecuted` | Date | |
| `initialvalue` | Currency or Number | |
| `finalvalue` | Currency or Number | Drives KPIs / rollups |
| `reason` Choice | add **New Scope** | keep Design Change, Scope Gap, Variation, Acceleration |
| `status` Choice | add **Canceled** | keep Approved, Pending, Potential, Rejected |

Keep existing `value` for a transition period; the app prefers `finalvalue` and falls back with `Coalesce(finalvalue, value)`.

## Notes

- `subcontractid` on Changes = `packageidentifier` on Subcontracts (must match).
- `currentlyactive`: `Yes` / `No` (SharePoint Yes/No column). **Closed-out status is only from `closeoutstatus = Closed`**, not from Active = No.
- Choice columns must match list choices exactly:
  - holdback: Applicable | Not applicable
  - closeoutstatus: In progress | Close-out pending | Holdback to process | Closed
  - changetype: Change Order | Claim | Change Directive
  - reason: Design Change | Scope Gap | Variation | Acceleration | New Scope
  - status: Approved | Pending | Potential | Rejected | Canceled
  - currencycode: CAD | USD
  - indigenouscontribution: 0 | 5 | 10 | 15 | 20 | 25 | 50 | 100
  - worktype: Boots on ground | Supply only | Consulting
- One subcontract is seeded with high invoicedtodate so it shows **Over Budget**.
- One subcontract is **Closed**.

## Files

- `PostAward - Subcontracts.csv`
- `PostAward - Changes.csv`
