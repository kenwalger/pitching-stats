# Pitching Analysis

This project provides a web application and a command-line interface to analyze MLB pitcher performance data. It fetches data using `pybaseball`, processes it, and displays detailed summaries for starting pitchers over a given date range.

The hosted version on Render is intended as a **lightweight demo**: date ranges are capped (currently 14 calendar days per request) to stay within typical free-tier memory limits, and the UI shows a short demo banner. **Large date-range queries may still exceed the limits of the free hosting tier** or time out—run the app locally for heavier analyses.

## Key Features

-   **Starter Identification**: Finds both starting pitchers in every game (the first pitcher in the top of the first is the home starter, the first in the bottom of the first is the road starter). Stats include only pitches thrown in a pitcher's starts; relief appearances in the same date range are excluded.
-   **Contextual Statistics**: Displays raw totals (GS, IP, R, K, BB, H, HR) and rate stats (R/9, WHIP, K/9, BB/9, HR/9).
    -   **R/9, not ERA.** Statcast pitch data does not record earned runs, so the app reports runs that scored while the pitcher was on the mound, per nine innings. It is not earned and does not reassign inherited runners, so it will not match official ERA.
-   **Effectiveness Ranking**: Starters are listed as most and least effective by **CSW%** (called strikes plus whiffs, as a share of all pitches), which stays meaningful over short date ranges. Only starters with at least 75 pitches in their starts qualify, roughly one full start. If there are fewer qualifiers than two full lists, no pitcher appears in both.
-   **Postseason Ready**: `pybaseball` requests regular season, postseason, and spring training games, so a postseason date range works with no extra settings. An entire World Series fits inside the hosted demo's 14-day window.
-   **Performance Highlighting**: Pitch speed and spin rates are automatically color-coded (red/green) if they are significantly different from the MLB average for that pitch type, making it easy to spot exceptional performances.
-   **Interactive Charts (Web UI)**: After you submit the form, each pitcher card includes a **Visualizations** section (Bootstrap tabs) powered by [Chart.js](https://www.chartjs.org/) via `templates/base.html` (`extra_head`) and logic in `templates/index.html`:
    -   **Arsenal** — Doughnut chart of pitch mix (`pitch_percentage`, with fallback from counts) and a radar chart of whiff rate vs. CSW rate by pitch type. Vertices on the radar use the same per-pitch colors as the donut.
    -   **Location** — Scatter of average plate position (`avg_plate_x`, `avg_plate_z`) with a gray strike-zone box (rule-book bounds in feet: x ±0.85, z 1.5–3.5). **Legend** lists each pitch type with matching point colors.
    -   **Velocity / Spin** — Bubble chart: speed vs. spin, bubble radius from `total_pitches`, with a **pitch-type legend** at the bottom.
    **Colors**: Each pitch type gets a consistent hue across charts (fixed palette, sorted by name). **Borders** use green or red when average speed or spin is highlighted vs. MLB in the table; otherwise a darker shade of that pitch’s color. **Parsing**: The script walks `.table-responsive` blocks, aligns `thead`/`tbody` column counts (pandas Styler often adds a blank corner `<th>`), and can rediscover plate-location columns by value ranges if headers and cells are still misaligned.
-   **Detailed Legend**: A clear on-page legend explains the thresholds for performance highlighting.
-   **Web Interface & CLI**: A user-friendly Flask web app for visual analysis and a command-line interface for quick terminal-based queries.
-   **Pitch Type Reference**: A dedicated page in the "Resources" section lists the current Statcast pitch codes. Note that `ST` is the sweeper and `SV` is the slurve; Statcast classifies most two-seamers as sinkers (`SI`). Pitch types without a league average on file are displayed but not color-coded.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/PitchingAPI.git
    cd PitchingAPI
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Web Application

To start the Flask web server:

```bash
python app.py
```

Open your web browser and navigate to `http://127.0.0.1:5000`. You can then select a date range and the number of starters to show in each list (most and least effective). Charts appear under each pitcher’s summary table after results load; Location and Velocity/Spin tabs include Chart.js legends keyed by pitch type.

### Command-Line Interface

You can also run the analysis from the command line.

**Default (last 5 days, 5 starters per list):**
```bash
python main.py
```

**Custom Parameters:**
```bash
python main.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD --n 10
```
-   `--start_date`: The start date for the data query.
-   `--end_date`: The end date for the data query.
-   `--n`: The number of starters in each list (most and least effective, by CSW%).

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The tests use synthetic Statcast rows, so they run offline. Each one is written to fail against the bug it guards against (for example, the starter test fails if road starters are dropped).

## Deployment

The app is served in production with **Gunicorn** (`Procfile`: `web: gunicorn app:app --bind 0.0.0.0:$PORT`).

-   **[Render](https://render.com/)**: A `render.yaml` Blueprint defines a Python web service (install via `requirements.txt`, start command with bind and health check on `/`). Connect the repo in the Render dashboard under **New → Blueprint**, or create a Web Service and match those settings. Render sets the environment variable `RENDER=true` automatically; the app uses that to enable demo mode (banner + max 14-day inclusive window). To mimic that locally, run with `RENDER=true` in your environment.
-   **Heroku-style hosts**: The same `Procfile` pattern applies anywhere a `PORT` environment variable is set.

Python version is pinned for consistency (see `.python-version` and `render.yaml`).

## Changelog

High-level release notes live in [CHANGELOG.md](CHANGELOG.md). They are maintained from `git log`; for full detail run:

```bash
git log --oneline
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, pull requests, and how to file issues.

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities privately and notes on running the app safely in production.

---
[LICENSE](LICENSE)
