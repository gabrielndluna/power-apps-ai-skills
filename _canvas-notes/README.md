# Canvas App Notes (validated reference)

Internal knowledge base for offline Power Apps YAML authoring in this repo.
Update these files whenever Studio import confirms or rejects something.

## Contents

| File | Purpose |
|------|---------|
| [icons.md](./icons.md) | `Icon.*` names that work vs fail in our apps |
| [layout-autolayout.md](./layout-autolayout.md) | AutoLayout / gallery sizing gotchas |
| [design-tokens.md](./design-tokens.md) | ProcTrack colors, spacing, typography |
| [dashboard-spec.md](./dashboard-spec.md) | Project Dashboard exact pixel measures |
| [delegation.md](./delegation.md) | SharePoint delegable formulas & preload pattern |
| [sharepoint-hyperlinks.md](./sharepoint-hyperlinks.md) | Hyperlink columns — use field directly in `Launch()` |

## How to maintain

1. After each Studio import, note any formula errors or layout surprises.
2. Add confirmed icons to **Validated** in `icons.md`; add failures to **Invalid**.
3. Record layout fixes in `layout-autolayout.md` so we do not repeat mistakes.
4. Prefer icons and patterns listed here over guessing from Microsoft docs.

## Related

- Workflow: [CLAUDE.md](../CLAUDE.md)
- External clone (gitignored): `_reference/` from power-platform-skills
