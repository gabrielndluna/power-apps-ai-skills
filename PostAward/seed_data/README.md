# PostAward seed data

Generated from ProcTrack Packages/Projects exports (awarded packages only).

## Import order (SharePoint)

1. Open list **PostAward - Subcontracts** → Integrate → Excel / or List settings → Import spreadsheet / or paste via Edit in grid view.
   Easiest: **Edit in grid view** → paste columns, or use **Import from Excel/CSV** if available in your tenant.
2. Then import **PostAward - Changes**.

## Notes

- `subcontractid` on Changes = `packageidentifier` on Subcontracts (must match).
- `currentlyactive`: `Yes` / `No` (SharePoint Yes/No column).
- Choice columns must match list choices exactly:
  - holdback: Applicable | Not applicable
  - closeoutstatus: In progress | Close-out pending | Holdback to process | Closed
  - changetype: Change Order | Claim | Change Directive
  - reason: Design Change | Scope Gap | Variation | Acceleration
  - status: Approved | Pending | Potential | Rejected
- One subcontract is seeded with high invoicedtodate so it shows **Over Budget**.
- One subcontract is **Closed**.

## Files

- `PostAward - Subcontracts.csv`
- `PostAward - Changes.csv`
