# SharePoint hyperlink columns in Canvas Apps

Validated in ProcTrack (2026-07): `dashboard_url` on **ProcTrack - Projects** (SharePoint hyperlink type).

## Use the column directly — not `.Url`

Microsoft docs often show hyperlink fields as `{ Url, Description }` records. In our SharePoint connector setup, **`Launch()` works with the field name alone**:

```powerfx
OnSelect: =Launch(varSelectedProject.dashboard_url)
```

No `If()` wrapper needed when `Visible` already gates blank URLs.

## Visibility

```powerfx
Visible: =!IsBlank(varSelectedProject.dashboard_url)
```

## Pattern (Welcome screen)

- White pill next to project logo: label **Dashboard** + `Icon.OpenInNewWindow` on the right.
- `OnSelect` on both label and icon: `Launch(varSelectedProject.dashboard_url)`.
- URL changes when the user picks a different project in the combobox (`varSelectedProject` updates on `OnChange`).

## Preloaded collections

If projects come from `colPermittedProjects` (loaded via `LookUp` / `ForAll`), the hyperlink column is included automatically when present on the SharePoint list. No `ShowColumns` needed unless you strip fields intentionally.

## Checklist

1. Add hyperlink column in SharePoint; refresh the data source in Studio if the field is missing.
2. Test `varSelectedProject.<columnname>` in a label first.
3. Use `Launch(varSelectedProject.<columnname>)` — avoid `.Url` unless a Studio test proves it necessary.
4. Hide the control when `IsBlank(varSelectedProject.<columnname>)`.
