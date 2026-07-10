# AutoLayout & gallery layout notes

Validated through ProcTrack development (2026-06-29).

## FillPortions: the #1 layout bug

In a **horizontal** AutoLayout container, children default to stretching unless constrained.

| Child role | Set |
|------------|-----|
| Fixed-size icon badge | `FillPortions: =0` + explicit `Width` / `Height` |
| Icon wrapper (ManualLayout) | `FillPortions: =0` — **without this, the colored circle grows across the card** |
| KPI label column next to icon | `FillPortions: =1` + explicit text `Height` values |
| Spacer / flex grow | `FillPortions: =1` |
| Gallery in vertical screen stack | `FillPortions: =1` — fills remaining height |
| Header / KPI row / toolbar | `FillPortions: =0` + fixed `Height` |

### Symptom we hit

KPI cards showed huge pastel squares with numbers pushed to the right edge. Cause: icon wrapper containers had no `FillPortions: =0`, so AutoLayout expanded them.

## Screen vertical stack pattern

```
main_container (vertical AutoLayout, Height = Parent.Height)
  header          FillPortions: 0, Height: 64
  kpi_row         FillPortions: 0, Height: 68
  toolbar         FillPortions: 0, Height: 40
  gallery         FillPortions: 1   ← takes remaining space
  empty_state     FillPortions: 0, Visible when no items
```

**Avoid** `Height: =Parent.Height - 300` on the gallery when siblings use AutoLayout — leaves a large dead zone.

## Gallery cards

| Property | Guidance |
|----------|----------|
| `TemplateSize` | ~242px for dashboard cards (2×2 metrics + button + wrapped title) |
| Card `Height` | `=Parent.TemplateHeight - 4` — match template, do not use a smaller fixed height |
| `WrapCount` | `Max(1, RoundDown((Parent.Width - 16) / 340, 0))` — ~340px min card width |
| `TemplatePadding` | 8–10px between cards |

### KPI label clipping / scrollbars

`Text@0.0.51` with a fixed `Height` smaller than the font line box shows **vertical scrollbars**. Prefer `Label@2.5.1` for numeric KPI values.

Also: `FillPortions: =1` on the KPI **text column** (vertical container inside horizontal KPI card) can stretch the column and trigger scrollbars. Use `FillPortions: =0` on the text column.

| Control | Height | Size |
|---------|--------|------|
| KPI value (Label) | 26 | 17 bold |
| KPI label (Label) | 18 | 10 |

### Metric chips in cards (validated layout)

Use **two horizontal rows** (not nested vertical columns):

```
metrics_row1 (34px, horizontal, gap 8) → Packages | Awarded
metrics_row2 (34px, horizontal, gap 8) → Delayed  | At risk
```

Each chip: `FillPortions: 1`, `LayoutMinWidth: 0`, `LayoutAlignItems: Stretch`, vertical stack inside (value + label).

| Property | Value |
|----------|-------|
| Row `Width` | `=Parent.Width - 20` (card inner width) |
| Label `Width` | `=dash_metric_<chip>.Width - 12` — **never** `Parent.Width` (resolves to row, clips right column) |
| Value label | `Label@2.5.1`, Height 16, Size 11, Bold, `Align: Center` |
| Caption label | `Label@2.5.1`, Height 12, Size 9, `Align: Center` |

**Do not** nest `dash_metrics_left_col` / `dash_metrics_right_col` vertical containers — first child stretches and hides the second row.

### Card header

- **Fixed Height: 48** — do not rely on `LayoutMinHeight` + `AutoHeight` title alone.
- **No ManualLayout icon wrapper** in header — place `Classic/Icon` with `FillPortions: 0`; wrappers stretch when title wraps (pink bar bug).
- Project name: `Label@2.5.1`, Height **30**, `Wrap: true`, Size 12.
- Project ID: `Label@2.5.1`, Height 12, Size 9.

### Gallery sizing

| Property | Value |
|----------|-------|
| `TemplateSize` | **210** |
| `WrapCount` | `Max(1, RoundDown((Parent.Width - 16) / 360, 0))` |

Full pixel budget: [dashboard-spec.md](./dashboard-spec.md)

## Text controls

- Use `AutoHeight: =true` only when the parent container can grow with the text.
- For project titles in gallery cards: `Wrap: =true`, no fixed height on the header row — only `LayoutMinHeight`.
- Avoid `Width: =400` on header text — causes excess horizontal pressure; use ~200–260 or `FillPortions`.
- **Gallery cards use a uniform `TemplateSize`** for every row — size it for ~2 wrapped title lines (~242px) or accept whitespace on short titles.

## ManualLayout inside AutoLayout

Icon-in-circle pattern:

```
wrapper: ManualLayout, FillPortions: 0, Width/Height: 32
  icon: Classic/Icon, X/Y centered manually
```

## Controls that work well together

| Pattern | Controls |
|---------|----------|
| Search | `Search_Bar` canvas component |
| Primary CTA | `Classic/Button@2.2.0` or `ButtonMain` component |
| Section title | `Text@0.0.51` with `Weight: Bold` |
| Card surface | `GroupContainer@1.5.0` AutoLayout, white fill, `DropShadow.Light`, radius 8–10 |

### AddColumns column names

In `AddColumns(source, columnName, formula)`, the new column name is an **identifier**, not a string:

```powerapps
AddColumns(colWsRoleCands, attStatus, ...)
```

Do **not** write `"attStatus"` — Studio flags it as an error.

### Status indicator dots

Use `Rectangle@2.3.0` (8×8) for pill dots. `GroupContainer` ManualLayout 7×7 renders as a **broken control** (red X) in Studio.

### Page titles and gallery cards (RoleFit)

| Control | Height | Size |
|---------|--------|------|
| Page title | 34 | 22 bold |
| Page subtitle | 20–40 | 12–13, Wrap if long |
| Tab button | 40 | 12 semibold |
| Gallery row card | `=Parent.TemplateHeight - 4` |
| Label in card | explicit Height; `Width: =Parent.Width` inside card columns |

## RoleFit screen stack

Match ProcTrack Project Dashboard. Do **not** use `Height: =Parent.Height - N` on galleries inside AutoLayout — use `FillPortions: =1` on `content`, tab panels, and galleries.

```
main (vertical, FillPortions: 1)
  topbar   FillPortions: 0, Height: 56
  content  FillPortions: 1
    gallery FillPortions: 1, TemplatePadding: 8, Width: Parent.Width
```

Nav rail on every screen: **RoleFit** brand (no subtitle), left-aligned nav buttons, user block at bottom.

`pac canvas pack` with SourceCode layout does not catch invalid icons or layout issues. Always validate with a **small import** in Studio.
