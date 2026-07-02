# Project Dashboard layout spec

Exact measures for `ProcTrack/src/Src/Project Dashboard.pa.yaml`.  
Validated incrementally via Studio import (2026-06-29).

## Screen stack

| Block | Height | FillPortions |
|-------|--------|--------------|
| Header bar | 64 | 0 |
| KPI row | 68 | 0 |
| Toolbar | 40 | 0 |
| Project gallery | remaining | 1 |

## KPI card (each of 4)

| Element | Size / notes |
|---------|----------------|
| Card padding | 8px vertical, 10px horizontal |
| Icon badge | 28×28 ManualLayout, icon 16×16 at X/Y **6**, `AlignInContainer: Center` |
| Text column | `FillPortions: 0`, `LayoutMinHeight: 44` — **do not use FillPortions: 1** (causes stretch + scrollbars) |
| Value | `Label@2.5.1`, Height **28**, Size **16**, Bold |
| Label | `Label@2.5.1`, Height **20**, Size **10** |

Use **Label**, not `Text@0.0.51`, for KPI numbers — Text canvas scrolls when Height < font size.

## Project gallery

| Property | Value |
|----------|-------|
| `TemplateSize` | **210** |
| `WrapCount` | `Max(1, RoundDown((Parent.Width - 16) / 360, 0))` — ~3 cards/row on 1366px |
| `TemplatePadding` | 8 |

### Card content budget (must sum ≤ TemplateSize)

| Section | Height |
|---------|--------|
| Padding top | 8 |
| Accent bar | 3 |
| Gap | 6 |
| Header row | **48** (fixed) |
| Gap | 6 |
| Metrics row 1 | **34** (Packages \| Awarded) |
| Gap | 6 |
| Metrics row 2 | **34** (Delayed \| At risk) |
| Gap | 6 |
| Open button | **30** |
| Padding bottom | 8 |
| **Total** | **189** |

~21px slack inside 210px template.

### Card header (48px fixed)

| Element | Size |
|---------|------|
| Folder icon | 22×22, `FillPortions: 0`, `AlignInContainer: Center` — **no icon wrapper container** |
| Title | `Label@2.5.1`, Height **30**, Size **12**, Bold, `Wrap: true` (max ~2 lines) |
| Project ID | `Label@2.5.1`, Height **12**, Size **9** |
| Logo | 48×28, `FillPortions: 0` |

### Metric chip (each)

| Element | Size |
|---------|------|
| Row height | 34 |
| Value | `Label@2.5.1`, Height **16**, Size **11**, Bold, `Align: Center` |
| Label | `Label@2.5.1`, Height **12**, Size **9**, `Align: Center` |
| Label width inside chip | `=dash_metric_<name>.Width - 12` — **never** `Parent.Width` (resolves to row width, clips right column) |
| Metric row width | `=Parent.Width - 20` (card inner width, matches accent bar) |
| Chip container | `LayoutMinWidth: 0`, `LayoutAlignItems: Stretch` |

### Metric layout (2 rows — same visual as 50/50 columns)

Row 1: Packages (left half) + Awarded (right half)  
Row 2: Delayed (left half) + At risk (right half)  
Each chip: `FillPortions: 1` in its horizontal row. **Avoid** nested vertical column containers.

## Known bugs we hit

1. **KPI scrollbars** — `Text@0.0.51` Height 22 + Size 18, or `FillPortions: 1` on text column.
2. **Pink vertical bar on cards** — `dash_card_icon_wrap` ManualLayout inside header that grows with wrapped title; cross-axis stretch fills card height.
3. **Metrics clipped** — `TemplateSize` too large vs content OR header growing unbounded with `AutoHeight` + `Wrap` on Text canvas.
4. **Metrics only top row visible / huge chips** — vertical column layout lets first child (Packages/Awarded) stretch; use **two horizontal rows** instead.
5. **Right metrics clipped ("Awar", "At r")** — labels used `Width: =Parent.Width` which resolved to the **row** width, not the chip; use `=dash_metric_awarded.Width - 12` etc.

## Data formulas

KPIs and card metrics read from **`colPermittedPackages`** / **`colPermittedProjects`** (preloaded with delegable per-project filters). See [delegation.md](./delegation.md). Do not change layout properties when tuning formulas.
