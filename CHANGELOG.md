# Changelog

All notable changes to this project are summarized here. Entries are grouped by date and derived from `git log` (subjects may be lightly edited for clarity). For the full history, run:

```bash
git log --format='%h %ad %s' --date=short
```

## 2026-10-15

- **Starter identification**: Find both starters in every game by grouping on game and half-inning. Previously only the first pitch of each game was used, which identified the home starter and dropped every road starter.
- **Starts only**: Stats now include only pitches thrown in a pitcher's starts. Relief appearances by a starter in the same range are excluded. Cards show games started (GS).
- **ERA replaced with R/9**: The old "ERA" was computed from home runs alone, duplicating HR/9. Statcast does not record earned runs, so the app now reports runs scored while the pitcher was pitching (from `bat_score` / `post_bat_score`) as R and R/9, labeled and explained in the UI.
- **Pitch types**: `ST` now maps to sweeper (it was two-seam fastball, so sweepers were compared against fastball averages and nearly always flagged slow). Added `SV` slurve, `KC`, `CS`, `FA`, `FO`, `SC`, `PO`; removed the non-Statcast `GY`. Reference page and decoder updated.
- **Ranking labels**: "Top/Bottom" is now "Most/Fewest Pitches Thrown", since the ranking measures workload. The fewest list no longer repeats pitchers already in the most list.
- **Tests**: Added offline pytest suite with synthetic Statcast rows (`tests/`), plus `requirements-dev.txt`.
- **Formatting**: Applied Black so the existing CI check passes.

## 2026-03-22

- **Hosted demo (Render)**: Detect `RENDER=true` (set automatically on Render web services). Cap each request to **14 calendar days** inclusive before calling `process_data`; show validation errors on the home form when the span is too long. Add a site-wide demo banner under the nav and a short note under the date form on the index page. README explains demo vs. local runs and how to set `RENDER=true` locally to test the same behavior.
- **Form validation**: On POST, validate ISO dates, end ≥ start, and **Top/Bottom N** (empty → 5, integer required, bounds 1–100) before `process_data`; use `request.form.get` for safe reads. The 14-day span check applies only when `RENDER=true`. Top/Bottom N uses one parse pass (`n_top_bottom` / `n_parse_ok`) for both template repopulation and gating. `RENDER` is resolved once per request via `flask.g` in `before_request` and read through `is_render_environment()` (with a fallback when there is no app context). The index form’s number input exposes `min`/`max`/`step` aligned with server limits.

## 2026-03-21

- **Deployment**: Add Render Blueprint (`render.yaml`); bind Gunicorn to `0.0.0.0:$PORT` in the `Procfile`.
- **Charts (web UI)**: Chart.js visualizations on each pitcher card—Arsenal (pitch-mix donut, whiff/CSW radar), Location (plate scatter with strike-zone overlay), Velocity/Spin (bubbles). Client-side parsing of pandas/Styler summary tables with `.table-responsive` discovery, thead/body column alignment for a blank corner header, and fallback detection of plate `x`/`z` columns by value range when needed.
- **Chart UX**: Shared per-pitch color palette across charts; green/red borders when speed or spin cells are highlighted vs. league; bottom legends on Location and Velocity/Spin (one dataset per pitch type); taller chart panes to fit legends; radar vertices use the same palette as the donut.
- **Docs**: README describes charts, parsing behavior, colors, and deployment; this changelog updated accordingly.

## 2025-09-29

- Add pitch percentage column; refine opponent display and related fixes.

## 2025-09-28

- Add contextual stats and color-coded performance vs. league averages.
- Update CSS, navigation, and summary pages.
- Debug/exploratory work on pitcher decision status.

## 2025-09-25

- Adjust Python version file handling for Heroku.
- Add Gunicorn to requirements; fix Procfile naming.
- Add README, LICENSE, and Heroku-oriented deployment files.
- Initial commit.
