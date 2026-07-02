# Power Apps Icons (`Icon.*`)

Use **Classic/Icon@2.5.0** in YAML. Only use names confirmed in a Studio import unless marked "likely".

Official enum (not all work in every app):  
https://learn.microsoft.com/en-us/power-platform/power-fx/reference/function-icons

## Validated in ProcTrack (imported successfully)

| Icon | Used for | Screen / component |
|------|----------|-------------------|
| `Icon.Add` | Add actions | Welcome screen, Create New Package |
| `Icon.ArrowDown` | Timeline flow | Package Details |
| `Icon.BackArrow` | Back navigation | BackButton component |
| `Icon.CalendarBlank` | Date fields | Package Details |
| `Icon.Cancel` | Cancel / clear | Welcome screen, Package Details |
| `Icon.CancelBadge` | Incomplete step | Package Details, Project Dashboard |
| `Icon.CheckBadge` | Complete / awarded | Package Details, Project Dashboard |
| `Icon.ChevronRight` | Forward / open | ButtonMain, Welcome screen |
| `Icon.Clock` | Schedule / at-risk | Create New Package, Package Details, Project Dashboard |
| `Icon.Folder` | Project / package group | Create New Package, Project Dashboard |
| `Icon.Information` | Info hint | Package Details |
| `Icon.Message` | Comments | Package Details |
| `Icon.OpenInNewWindow` | External link / Power BI dashboard | Package Details, Welcome screen |
| `Icon.People` | Contacts / leads | Create New Package, Package Details |
| `Icon.Save` | Save action | Package Details |
| `Icon.Search` | Search | Search_Bar, Project Dashboard |
| `Icon.Settings` | Settings | Welcome screen |
| `Icon.Text` | Text / package count | Create New Package, Project Dashboard |
| `Icon.Home` | Dashboard header | Project Dashboard |
| `Icon.Warning` | Attention / risk | Package Details, Project Dashboard |

## Invalid (Studio error: "isn't recognized")

| Icon | Error context | Date |
|------|---------------|------|
| `Icon.ViewList` | Project Dashboard header | 2026-06-29 |
| `Icon.Documents` | Project Dashboard KPI + metrics | 2026-06-29 |

## Replacements we use

| Instead of | Use | Notes |
|------------|-----|-------|
| `Icon.ViewList` | `Icon.Home` | Dashboard header; validated in ProcTrack |
| `Icon.Documents` | `Icon.Text` | Package counts; already validated elsewhere |

## Likely valid (Power Fx enum, not yet imported here)

`Icon.Note`, `Icon.Journal`, `Icon.Import`, `Icon.Filter`, `Icon.Edit`, `Icon.Mail`, `Icon.Upload`, `Icon.Trash`, `Icon.Check`, `Icon.ChevronDown`, `Icon.ChevronLeft`

Mark as **Validated** only after a successful Studio import.

## Tips

- Grep the repo: `Icon\.\w+` in `*.pa.yaml` for usage in working screens.
- Modern fluent icons differ from `Classic/Icon`; stick to `Classic/Icon@2.5.0` for YAML edits.
- Component `ButtonMain` expects an `Icon` custom property passed as `Icon.SomeName`.
