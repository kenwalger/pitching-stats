# Pitching Analysis

This project provides a web application and a command-line interface to analyze pitcher performance data from Major League Baseball games. It fetches data from `pybaseball`, processes it, and displays summaries for top and bottom performers over a given date range.

## Features

-   **Web Interface**: A Flask-based web application to visualize pitcher statistics.
-   **CLI**: A command-line interface for quick data analysis in the terminal.
-   **Customizable Queries**: Filter data by date range and the number of top/bottom pitchers to display.
-   **Detailed Statistics**: View general stats (ERA, WHIP, K/9) and pitch-specific summaries (speed, spin rate, whiff rate).

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/PitchingAPI.git
    cd PitchingAPI
    ```

2.  **Create a virtual environment and activate it:**
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

Open your web browser and navigate to `http://127.0.0.1:5000`. You can then select a date range and the number of pitchers to view.

### Command-Line Interface

You can also run the analysis from the command line.

**Default (last 5 days, top/bottom 5 pitchers):**
```bash
python main.py
```

**Custom Parameters:**
```bash
python main.py --start_date YYYY-MM-DD --end_date YYYY-MM-DD --n 10
```
-   `--start_date`: The start date for the data query.
-   `--end_date`: The end date for the data query.
-   `--n`: The number of top and bottom pitchers to display.
