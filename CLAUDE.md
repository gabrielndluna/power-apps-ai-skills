# Power Apps Canvas App Offline Workflow

This workspace uses an offline offline-first Canvas Apps source workflow with `pac canvas unpack` / `pac canvas pack` and YAML-based source files.

## Workflow

1. SEED (my job, browser)
   - Create a blank Canvas App in Power Apps Studio.
   - Download the `.msapp` package from Power Apps Studio.
   - Drop the seed `.msapp` into the app folder under `power_apps/<app_name>/`.

2. UNPACK (you)
   - Use `pac canvas unpack --msapp <seed>.msapp --sources ./src --layout SourceCode`.
   - This creates the unpacked YAML source under `./src`.

3. BUILD (you)
   - Edit and add screen `.pa.yaml` files in `./src` for the requested app.
   - Keep designs compatible with standard connectors only.
   - Avoid Premium-only features, Managed Environments, Git integration, Code Apps, or Dataverse-specific premium connectors.

4. PACK (you)
   - Use `pac canvas pack --msapp <app>.msapp --sources ./src`.
   - This re-creates a packed `.msapp` for import.

5. IMPORT/PUBLISH (my job, browser)
   - In Power Apps Studio, use File > Open > Browse to import the packed `.msapp`.
   - Authorize only standard connectors: SharePoint, Office 365 Users, Outlook, Excel Online.
   - Test the app in the browser, then Publish.

## Important rules

- Only standard connectors may be used: SharePoint, Office 365 Users, Outlook, Excel Online.
- Do not use Premium connectors, Dataverse-only services, or managed environment features.
- `pac canvas pack/unpack` is deprecated. Validate by importing after small changes rather than large rewrites.
- App source is kept in per-app subfolders under `power_apps/<app_name>/src/`.
- Seed, import, and publish are performed by the user in the browser.

## Tool versions

- `pac` pinned version: `2.8.1+ga4eb71c (.NET 10.0.9)`
- `.NET` SDK version: `10.0.301`

## Folder layout

- `power_apps/`
  - `_reference/` — cloned offline reference materials (gitignored)
  - `_canvas-notes/` — validated icons, layout patterns, design tokens (maintain after Studio imports)
  - `<app_name>/`
    - `seed.msapp` — user-provided blank canvas app seed
    - `app.msapp` — packed version produced by `pac canvas pack`
    - `src/` — unpacked Canvas App source YAML

## Notes

- The workspace is deliberately offline for Canvas YAML authoring.
- Do not rely on external MCP servers for app source generation.
- Use the `_reference/` clone only for guidance and offline reference.
- Check `_canvas-notes/` before adding new icons or AutoLayout patterns; update it after import validation.
- For SharePoint lists with large row counts, follow `_canvas-notes/delegation.md` (preload collections, avoid `in` on connector sources).
