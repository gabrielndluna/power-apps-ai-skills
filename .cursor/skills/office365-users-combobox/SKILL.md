---
name: office365-users-combobox
description: >-
  Build Office 365 Users people-search comboboxes in Canvas YAML with
  ModernCombobox so search works on import. Use when adding or fixing an
  approver, employee, or person picker, Office365Users.SearchUser,
  Classic/ComboBox DisplayFields or SearchFields, or when a people combo only
  works after deleting and retyping the same property in Studio.
---

# Office 365 Users combobox

People search in a YAML pack must be `ModernCombobox@1.1.2`. Search lives in `Items`. Do not use `Classic/ComboBox` for `Office365Users.SearchUser`.

Validated on Dayaway Aecon, ProcTrack (`technical_lead_input`), and Staffclock Mactaquac Settings (`Dropdown_SettingsEmployee`). Full notes: `_canvas-notes/office365-users.md`.

## Why classic fails after pack

`Classic/ComboBox` `DisplayFields` and `SearchFields` often arrive blank after `pac canvas pack` and Studio import. The box looks fine and the formula is still in YAML, but search returns nothing until someone opens the property in Studio, deletes it, and types the same formula again. That touch is not a fix. The next pack brings the bug back.

`ModernCombobox` has no `DisplayFields` or `SearchFields`. `ItemDisplayText` and `Items` survive import, so search works without opening the formula bar.

## Pattern

Copy this. Do not add `DisplayFields`, `SearchFields`, `IsSearchable`, or an `AddColumns` label.

```yaml
Control: ModernCombobox@1.1.2
Properties:
  BorderThickness: =1
  Height: =36
  InputTextPlaceholder: ="Search by name or email"
  ItemDisplayText: =ThisItem.DisplayName & " - " & ThisItem.Mail
  Items: |+
    =If(
        !IsBlank(Trim(Self.SearchText)),
        ShowColumns(
            Office365Users.SearchUser(
                { searchTerm: Trim(Self.SearchText), top: 15 }
            ),
            Id,
            DisplayName,
            Mail,
            UserPrincipalName,
            Department
        )
    )
  LayoutMinHeight: =0
  LayoutMinWidth: =0
  OnChange: |-
    =Set(
        varPersonEmail,
        Lower(Coalesce(Self.Selected.Mail, Self.Selected.UserPrincipalName))
    );
    Set(varPersonName, Self.Selected.DisplayName)
  SelectMultiple: =false
  Width: =320
```

## Rules

- Call `SearchUser` only when `Trim(Self.SearchText)` is not blank.
- `ShowColumns` only: `Id`, `DisplayName`, `Mail`, `UserPrincipalName`, `Department`. No `AddColumns` / `UserLabel`.
- `ItemDisplayText` reads `ThisItem.DisplayName` and `ThisItem.Mail`. A custom label column breaks the list.
- `top` is `15`.
- Store `Lower(Coalesce(Selected.Mail, Selected.UserPrincipalName))`. `Mail` is blank on some directory records.
- Filter a local collection with `Lower(Employee) = varPersonEmail`. Do not run `Lower()` against SharePoint.
- `DefaultSelectedItems`, when needed, must be a table with those same five columns. Use `Office365Users.UserProfileV2` and map `id`, `displayName`, `mail`, `userPrincipalName`, `department`. See Dayaway `ComboBox3_1`.

## Do not

- `Classic/ComboBox@2.4.0` plus `DisplayFields` / `SearchFields` for directory search.
- `SearchFields` that include `UserPrincipalName`.
- `ComboBox@0.0.51` (`DisplayFields` is an unknown property, PA2108).
- Asking the user to click, delete, and retype a property after import. Switch the control to this pattern instead.
