# Office 365 Users search patterns

Use `ModernCombobox@1.1.2` for every new or rebuilt people picker. Skill: `.cursor/skills/office365-users-combobox/SKILL.md`.

Validated on Dayaway Aecon, ProcTrack `technical_lead_input`, and Staffclock Mactaquac Settings `Dropdown_SettingsEmployee` (2026-11-03).

## Modern combobox (use this)

`Classic/ComboBox` `DisplayFields` and `SearchFields` often import blank. Search stays dead until someone opens the property in Studio, deletes the formula, and types the same formula again. The next YAML pack drops it again.

`ModernCombobox` keeps `ItemDisplayText` and `Items`, so search works on import.

```powerfx
// ItemDisplayText
ThisItem.DisplayName & " - " & ThisItem.Mail

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
```

Also set `SelectMultiple = false`. Do not set `DisplayFields`, `SearchFields`, or `IsSearchable`.

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

## Default selected person

`DefaultSelectedItems` must be a table with the same five columns as `Items`. Map `Office365Users.UserProfileV2` (`id`, `displayName`, `mail`, `userPrincipalName`, `department`) into `Id`, `DisplayName`, `Mail`, `UserPrincipalName`, `Department`. Return `[]` when the email is blank. Dayaway `ComboBox3_1` is the reference.

## Connector metadata

When Office 365 Users is added to a Studio-exported `.msapp`, unpack that export and refresh the app's `src/*.msapr` before packing. Editing YAML alone does not add the connector metadata.

## Old pattern

`Classic/ComboBox@2.4.0` with `DisplayFields = ["DisplayName"]` and `SearchFields = ["DisplayName", "Mail"]` was the Staffclock YNSE pattern (2026-07-16). Leave an existing classic control alone only if it was saved in Studio and you are not repacking that screen. Any new picker, or any picker that needs the formula retyped after import, is the modern control above.
