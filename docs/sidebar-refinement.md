# Sidebar refinement

25 November 2026. The owner's video reference informs the compact brand row,
grouped icon navigation, rounded active item, quiet dataset disclosure, and
bottom-aligned workspace details. RetailPulse retains the logo palette and its
six actual destinations.

[Desktop](evidence/sidebar/desktop.png) ·
[Phone drawer](evidence/sidebar/phone.png) ·
[Browser checks](evidence/sidebar/checks.json)

The sidebar now groups Overview under Workspace; Sales Analysis, Product
Performance, and Geographic Analysis under Analytics; and the Explorer and
Quality Center under Data. Six consistent line icons replace the visible radio
circles. The underlying native radio, `navigation` state key, accessible names,
and arrow-key navigation remain. Group labels and icons are presentation only.

The existing logo appears beside the existing title/subtitle. Dataset & methodology
still contains the workbook upload, duplicate policy, and official source link.
The source footer remains in the sidebar's scrolling flow so it stays reachable
on short displays. Native collapse, resize, and the collapsed header logo remain.

Implementation is limited to the sidebar block in `app.py`, scoped rules in
`assets/styles.css`, and documentation. All `src` modules, the theme configuration,
and original logo match hashes captured at the start of this task.

The installed Impeccable layout guidance informed grouping and responsive
behavior. Existing anti-slop implementation mode and the logo-based design
direction remain. ENERGY 2 / RHYTHM 2 / MOTION 1.

## Delivery checks

- **Hard gate PASS:** all 84 tests pass; the real workbook retains its four
  default sales KPIs. All six pages, native arrow-key navigation, visible focus,
  dataset disclosure, duplicate policy, invalid upload recovery, and source link
  were checked. Navigation targets measure at least 44px high.
- **Purpose gate PASS:** icons identify the existing page subjects; groups
  organize existing tasks; the footer identifies the actual dataset. The active
  row retains the logo blue and its previously measured 5.37:1 white-text contrast.
- **Liveliness PASS:** compact branding and repeated line icons connect the
  sidebar to the video's spatial hierarchy while preserving the logo palette.
- **Craft PASS:** Chrome checks pass at 1440 × 1080, 375 × 900, and 844 × 390.
  Expanded/collapsed desktop and phone states have no page overflow or clipped
  KPI values. The sidebar scroll reaches the source controls in landscape.
  Reduced motion remains active when requested. Browser console errors and page
  exceptions are absent; `git diff --check` passes.

Browser harnesses and intermediate captures remain in ignored `.venv/qa/sidebar/`.
