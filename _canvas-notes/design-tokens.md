# ProcTrack design tokens

Colors and spacing used across ProcTrack screens. Keep new screens consistent.

## Brand colors

| Token | RGBA | Usage |
|-------|------|-------|
| Aecon red (primary) | `RGBA(214, 12, 48, 1)` | Headers, primary buttons, accents |
| Aecon red hover | `RGBA(192, 0, 0, 1)` | Button hover |
| Red tint 10% | `RGBA(214, 12, 48, 0.1)` | Icon backgrounds on cards |
| Red tint 12% | `RGBA(214, 12, 48, 0.12)` | KPI icon backgrounds |

## Neutrals

| Token | RGBA | Usage |
|-------|------|-------|
| Page background | `RGBA(245, 245, 245, 1)` | Screen / main container fill |
| Card background | `RGBA(255, 255, 255, 1)` | Cards, KPI tiles |
| Header strip (Welcome) | `RGBA(214, 221, 224, 1)` | Alternate screen background |
| Table header | `RGBA(237, 237, 237, 1)` | Column headers |
| Text primary | `RGBA(33, 33, 33, 1)` | Titles, KPI values |
| Text secondary | `RGBA(48, 48, 48, 1)` | Body |
| Text muted | `RGBA(106, 122, 127, 1)` | Labels, hints |
| Border default | `RGBA(214, 221, 224, 1)` | Inputs, dividers |

## Status colors

| Status | RGBA | Icon |
|--------|------|------|
| Awarded / success | `RGBA(16, 124, 65, 1)` | `Icon.CheckBadge` |
| Success background | `RGBA(232, 246, 238, 1)` | Metric chip fill |
| Info / link | `RGBA(0, 120, 212, 1)` | KPI packages accent |
| Warning / at risk | `RGBA(255, 140, 0, 1)` | `Icon.Warning`, `Icon.Clock` |
| Warning background | `RGBA(255, 244, 229, 1)` | Metric chip fill |
| Delayed / error | `RGBA(214, 12, 48, 1)` | `Icon.CancelBadge` |
| Delayed background | `RGBA(253, 236, 236, 1)` | Metric chip fill |
| Neutral metric | `RGBA(245, 247, 250, 1)` | Package count chip |

## Typography (`Text@0.0.51`)

| Role | Size | Weight |
|------|------|--------|
| Screen title (header) | 20 | Bold |
| KPI value | 18 | Bold |
| Section label | 14 | Semibold |
| Card title | 15 | Bold |
| Body / metric | 11–12 | Regular |
| Caption / ID | 10–11 | Regular |

Font for classic controls: `Font.'Segoe UI'`

## Spacing

| Element | Value |
|---------|-------|
| Screen padding | 16px (12 top/bottom on dashboard) |
| Section gap (`LayoutGap`) | 10px |
| KPI row height | 64px |
| Header height | 64px |
| Card padding | 12px |
| Card radius | 8–10px |
| Icon badge size (KPI) | 32×32 |
| Icon badge size (card) | 32×32 |

## Header pattern (red bar)

Used on Welcome screen, Create New Package, Package Details, Project Dashboard:

- `Fill: RGBA(214, 12, 48, 1)`
- `Radius: 8`, horizontal AutoLayout
- White text; subtitle at ~82% opacity

### Welcome screen (two-tier, 108px)

Also used on **Create New Package** and **Package Details** (without Excel export or Settings).

| Row | Height | Contents |
|-----|--------|----------|
| Top | 44px | Same brand block as dashboard: frosted home icon (36×36) + ProcTrack 20 / subtitle 12 + signed-in user |
| Bottom | 32px | White strip: `Project` label (Width **68**) + combobox + logo + **Dashboard** pill |

Welcome screen only: Excel export + Settings (top row). **Dashboard** pill (bottom row, right of logo): `Launch(varSelectedProject.dashboard_url)` — see [sharepoint-hyperlinks.md](./sharepoint-hyperlinks.md).

- **Home icon navigation:** Welcome → Project Dashboard; Create New Package / Package Details → **Back arrow** → Welcome screen.
- **Project picker row:** label + combobox both **Height 32**, no vertical padding on white strip; combobox `AlignInContainer: Center`.
