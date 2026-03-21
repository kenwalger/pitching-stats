# Pitching Analysis

This project provides a web application and a command-line interface to analyze MLB pitcher performance data. It fetches data using `pybaseball`, processes it, and displays detailed summaries for starting pitchers over a given date range.

## Key Features

-   **Accurate Starter Identification**: The app automatically identifies the true starting pitcher for each game, ensuring the analysis is focused and relevant.
-   **Contextual Statistics**: Displays both raw totals (IP, K, BB, HR) and calculated rate stats (ERA, WHIP, K/9) to provide a complete picture of a pitcher's performance.
-   **Performance Highlighting**: Pitch speed and spin rates are automatically color-coded (red/green) if they are significantly different from the MLB average for that pitch type, making it easy to spot exceptional performances.
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

Open your web browser and navigate to `http://127.0.0.1:5000`. You can then select a date range and the number of top/bottom starters to view.

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

---
[LICENSE](LICENSE)
