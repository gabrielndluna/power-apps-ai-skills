# Office 365 Users search patterns

Validated in Staffclock YNSE (2026-07-16) on `Dropdown_Employee_Weekly`.

## Classic ComboBox people search (validated)

This exact combo works in Studio. Do not invent variants unless re-validated.

```powerfx
// DisplayFields
["DisplayName"]

// Items
If(
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

// SearchFields — keep ONLY these two
["DisplayName", "Mail"]
```

Also set:

```powerfx
IsSearchable = true
SelectMultiple = false
```

### Why these properties matter

| Property | Rule |
|----------|------|
| `DisplayFields` | Must be `["DisplayName"]`. Custom label columns like `UserLabel` break dropdown display/search. |
| `Items` | Call `Office365Users.SearchUser` only when `Self.SearchText` is non-blank. Use plain `ShowColumns` — no `AddColumns` wrapper. |
| `SearchFields` | Must be exactly `["DisplayName", "Mail"]`. Adding `UserPrincipalName` (or other fields) broke search in Studio. |
| `top` | `15` is the validated limit. |

## Capture the selected email

`Mail` may be blank for some directory records, so fall back to `UserPrincipalName`:

```powerfx
Set(
    varWeeklyEmployeeEmail,
    Lower(Coalesce(Self.Selected.Mail, Self.Selected.UserPrincipalName))
);
Set(varWeeklyEmployeeName, Self.Selected.DisplayName)
```

## Filter local collections by selected employee

After a delegable SharePoint load into a collection, filter locally:

```powerfx
IsBlank(varWeeklyEmployeeEmail) ||
Lower(Employee) = varWeeklyEmployeeEmail
```

Do not run `Lower(Employee)` against a large SharePoint source. Load with delegable date/status filters first, then apply the directory-selected email to the local collection.

Blank `varWeeklyEmployeeEmail` means "all employees" (no filter).

## Connector metadata

When Office 365 Users is added to a Studio-exported `.msapp`, unpack that export and refresh the app's `src/*.msapr` before packing. Editing YAML alone does not add the connector metadata.
