# SharePoint attachments (Canvas YAML)

Validated in **PRTrack** (PR Detail, 2026-09) on requisition item attachments.

## Rule of thumb

To let users **upload / view / remove files** on a SharePoint list item, use a **Form** bound to that list with a **Classic Attachments** data card. Do **not** invent a fake attach UI (labels, buttons that only `Notify`, or `Patch` of attachment blobs). SharePoint’s Attachments column is not a normal Patch field in Canvas YAML.

## Where files live (PRTrack)

| Approach | List / field | Use |
|----------|----------------|-----|
| **Native item attachments (preferred for upload UI)** | `PRTrack - Requisitions` → `{Attachments}` | Form + `Attachments@2.3.0` control. Files stored on the **PR (requisition) item**. |
| Metadata list (preload only) | `PRTrack - Attachments` (`parentid`, `parenttype`, …) | Optional index/preload via `colAllAttachments` / `colAttachments`. **Not** the upload control. |

PRTrack attaches at **PR level only** (not per line / Project Controls). Open the pane from the tab bar (“Attach files”) or after New PR submit (`varOpenAttachOnDetail`).

## UI pattern that works

1. Full-screen dimmed overlay (`ManualLayout`, `Visible = varShowAttachmentPane`).
2. Centered card (~460px tall, ~480px max width) — the Attachments control needs **real height** (~260–300px) or the “Attach file” affordance is unusable.
3. Inside the card: title + close, short hint, **Form**, Cancel / Save files.
4. Open: `EditForm(frm…); Set(varShowAttachmentPane, true)`.
5. Save: `SubmitForm(frm…)`.
6. Cancel / close: `ResetForm(frm…); Set(varShowAttachmentPane, false)`.
7. `OnSuccess`: refresh the selected record (`LookUp` again), notify, close pane.

Reference screen: `PRTrack/src/Src/PR Detail.pa.yaml` → `pd_attach_overlay` / `frmPRAttachments`.

## Minimal Form + Attachments card (copy this shape)

```yaml
- frmPRAttachments:
    Control: Form@2.4.4
    Layout: Vertical
    Properties:
      DataSource: ='PRTrack - Requisitions'   # list that owns the files
      DefaultMode: =FormMode.Edit
      Item: =LookUp('PRTrack - Requisitions', Title = varSelectedPR.Title)
      NumberOfColumns: =1
      Height: =300
      FillPortions: =1
      OnFailure: =Notify("Could not save attachments. Try again.", NotificationType.Error)
      OnSuccess: |-
        =Set(varSelectedPR, LookUp('PRTrack - Requisitions', Title = varSelectedPR.Title));
        Notify("Attachments saved.", NotificationType.Success);
        Set(varShowAttachmentPane, false)
    Children:
      - Attachments_DataCard_PR:
          Control: TypedDataCard@1.0.7
          Variant: ClassicAttachmentsEdit
          Properties:
            DataField: ="{Attachments}"
            Default: =ThisItem.Attachments
            DisplayName: ="Attachments"
            Required: =false
            Update: =DataCardValue_PRAttach.Attachments
            Height: =280
            Width: =Parent.Width
          Children:
            - DataCardKey_PRAttach:
                Control: Label@2.5.1
                MetadataKey: FieldName
                Properties:
                  Text: ="Supporting documents"
                  Visible: =false
            - DataCardValue_PRAttach:
                Control: Attachments@2.3.0
                MetadataKey: FieldValue
                Properties:
                  Items: =Parent.Default
                  MaxAttachments: =10
                  Height: =260
                  Width: =Parent.Width - 16
                  DisplayMode: =If(varCurrentRole = "Requester" || varIsAdmin, DisplayMode.Edit, DisplayMode.View)
                  Tooltip: ="Attach file"
            - ErrorMessage_PRAttach:
                Control: Label@2.5.1
                MetadataKey: ErrorMessage
                Properties:
                  Text: =Parent.Error
                  Visible: =And(..., !IsBlank(Parent.Error))
            - StarVisible_PRAttach:
                Control: Label@2.5.1
                MetadataKey: FieldRequired
                Properties:
                  Text: ="*"
                  Visible: =false
```

Save button outside the form:

```powerfx
SubmitForm(frmPRAttachments)
```

## Required pieces (do not omit)

| Piece | Why |
|-------|-----|
| `Form@2.4.4` + `Item` = the SharePoint row | Attachments only submit through the form |
| `TypedDataCard` + `Variant: ClassicAttachmentsEdit` | Studio-recognized attachments card |
| `DataField: ="{Attachments}"` | Exact special field name |
| `Default: =ThisItem.Attachments` | Loads existing files |
| `Update: =<AttachmentsControl>.Attachments` | Writes on `SubmitForm` |
| `Attachments@2.3.0` with `MetadataKey: FieldValue` | Actual upload control |
| Sibling labels with `MetadataKey: FieldName`, `ErrorMessage`, `FieldRequired` | Form card contract; keep even if hidden |
| Generous height on card / control | Tiny height → broken UX |
| `EditForm` before showing | Puts form in edit mode with current item |

## Role / permissions

Gate edit vs view on the Attachments control and hide Save when view-only:

```powerfx
DisplayMode: =If(varCurrentRole = "Requester" || varIsAdmin, DisplayMode.Edit, DisplayMode.View)
```

Other roles can still open the pane to **view** existing files.

## New PR → attach flow

1. After create, set `varSelectedPR` to the new requisition.
2. Set `varOpenAttachOnDetail = true` (and navigate to PR Detail).
3. On PR Detail `OnVisible`, if that flag is set: open pane + `EditForm(frmPRAttachments)`, then clear the flag.

That way attachments always bind to a **saved** list item (forms need an existing `Item`).

## What not to do

- Do not `Patch(..., { Attachments: ... })` from YAML for user uploads.
- Do not put Attachments controls on line-item galleries unless you bind a Form to **that** line’s list item and give it enough height.
- Do not rely on a separate Attachments **list** for the upload UI unless you intentionally build a different storage model (document library / Power Automate). Native item attachments are the standard connector path.
- Do not shrink the overlay so the Attachments control is clipped — users need to click **Attach file** inside the control.

## Preloading the Attachments list (optional)

If the app also has `PRTrack - Attachments` as a list connector, preload like other lists (delegation-friendly):

```powerfx
ForAll(
    colPermittedPRs As pr,
    If(
        !IsBlank(pr.Title),
        Collect(colAllAttachments, Filter('PRTrack - Attachments', parentid = pr.Title))
    )
);
ClearCollect(colAttachments, Filter(colAllAttachments, parentid in colProjectPRs.Title))
```

This does **not** replace the Form upload pattern above.

## Checklist for a new app/screen

1. Decide which SharePoint list item owns the files (parent record).
2. Ensure that list is connected and has Attachments enabled in SharePoint.
3. Add overlay + Form + ClassicAttachmentsEdit card as above.
4. Wire open (`EditForm` + show), save (`SubmitForm`), cancel (`ResetForm`).
5. Refresh `Item` / selected record on success.
6. Pack, import in Studio, authorize SharePoint, click **Attach file** once end-to-end.
7. If import fails on the Form card, re-check `DataField`, `Variant`, and `MetadataKey` siblings — do not invent alternate control trees without Studio validation.
