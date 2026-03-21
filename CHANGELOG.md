# Changelog

All notable changes to this project are summarized here. Entries are grouped by date and derived from `git log` (subjects may be lightly edited for clarity). For the full history, run:

```bash
git log --format='%h %ad %s' --date=short
```

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
