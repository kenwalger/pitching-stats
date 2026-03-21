# Pitching Analysis

This project provides a web application and a command-line interface to analyze MLB pitcher performance data. It fetches data using `pybaseball`, processes it, and displays detailed summaries for starting pitchers over a given date range.

## Key Features

-   **Accurate Starter Identification**: The app automatically identifies the true starting pitcher for each game, ensuring the analysis is focused and relevant.
-   **Contextual Statistics**: Displays both raw totals (IP, K, BB, HR) and calculated rate stats (ERA, WHIP, K/9) to provide a complete picture of a pitcher's performance.
-   **Performance Highlighting**: Pitch speed and spin rates are automatically color-coded (red/green) if they are significantly different from the MLB average for that pitch type, making it easy to spot exceptional performances.
-   **Interactive Charts (Web UI)**: After you submit the form, each pitcher card includes a **Visualizations** section (Bootstrap tabs) powered by [Chart.js](https://www.chartjs.org/) via `templates/base.html` (`extra_head`) and logic in `templates/index.html`:
    -   **Arsenal** — Doughnut chart of pitch mix (`pitch_percentage`, with fallback from counts) and a radar chart of whiff rate vs. CSW rate by pitch type. Vertices on the radar use the same per-pitch colors as the donut.
    -   **Location** — Scatter of average plate position (`avg_plate_x`, `avg_plate_z`) with a gray strike-zone box (rule-book bounds in feet: x ±0.85, z 1.5–3.5). **Legend** lists each pitch type with matching point colors.
    -   **Velocity / Spin** — Bubble chart: speed vs. spin, bubble radius from `total_pitches`, with a **pitch-type legend** at the bottom.
    **Colors**: Each pitch type gets a consistent hue across charts (fixed palette, sorted by name). **Borders** use green or red when average speed or spin is highlighted vs. MLB in the table; otherwise a darker shade of that pitch’s color. **Parsing**: The script walks `.table-responsive` blocks, aligns `thead`/`tbody` column counts (pandas Styler often adds a blank corner `<th>`), and can rediscover plate-location columns by value ranges if headers and cells are still misaligned.
-   **Detailed Legend**: A clear on-page legend explains the thresholds for performance highlighting.
-   **Web Interface & CLI**: A user-friendly Flask web app for visual analysis and a command-line interface for quick terminal-based queries.
-   **Pitch Type Reference**: A dedicated page in the "Resources" section provides a handy reference for pitch type abbreviations.

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

Open your web browser and navigate to `http://127.0.0.1:5000`. You can then select a date range and the number of top/bottom starters to view. Charts appear under each pitcher’s summary table after results load; Location and Velocity/Spin tabs include Chart.js legends keyed by pitch type.

### Command-Line Interface

You can also run the analysis from the command line.

**Default (last 5 days, top/bottom 5 starters):**
```bash
python main.py
```

**Custom Parameters:**
```bash
python main.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD --n 10
```
-   `--start_date`: The start date for the data query.
-   `--end_date`: The end date for the data query.
-   `--n`: The number of top and bottom starters to display.

## Deployment

The app is served in production with **Gunicorn** (`Procfile`: `web: gunicorn app:app --bind 0.0.0.0:$PORT`).

-   **[Render](https://render.com/)**: A `render.yaml` Blueprint defines a Python web service (install via `requirements.txt`, start command with bind and health check on `/`). Connect the repo in the Render dashboard under **New → Blueprint**, or create a Web Service and match those settings.
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
