import os
from flask import Flask, render_template, request
from datetime import date, timedelta
import pandas as pd
from data_processing import process_data
from helper_functions.style import style_summary_df
from constants.pitch_type_mapping import PITCH_TYPE_MAPPING


app = Flask(__name__)

# Render sets RENDER=true on web services (https://render.com/docs/environment-variables)
RENDER_DEMO_MAX_CALENDAR_DAYS = 14


def is_render_environment():
    return os.environ.get("RENDER", "").strip().lower() == "true"


@app.context_processor
def inject_render_demo():
    return {
        "demo_mode": is_render_environment(),
        "render_demo_max_calendar_days": RENDER_DEMO_MAX_CALENDAR_DAYS,
    }

def format_pitch_name(pitch_abbr):
    full_name = PITCH_TYPE_MAPPING.get(pitch_abbr, pitch_abbr)
    return full_name.replace('_', ' ').title()

@app.route('/', methods=['GET', 'POST'])
def index():
    start_dt = date.today() - timedelta(days=5)
    end_dt = date.today()
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")
    num_pitchers = 5

    top_pitchers_data = None
    bottom_pitchers_data = None
    range_error = None

    if request.method == 'POST':
        start_str = request.form['start_date']
        end_str = request.form['end_date']
        num_pitchers = int(request.form['num_pitchers'])

        if is_render_environment():
            try:
                start_parsed = date.fromisoformat(start_str)
                end_parsed = date.fromisoformat(end_str)
            except ValueError:
                range_error = "Invalid start or end date."
            else:
                if end_parsed < start_parsed:
                    range_error = "End date must be on or after start date."
                elif (end_parsed - start_parsed).days + 1 > RENDER_DEMO_MAX_CALENDAR_DAYS:
                    range_error = (
                        f"On this demo host you can request at most {RENDER_DEMO_MAX_CALENDAR_DAYS} calendar days "
                        "at once. Run the app locally for longer ranges."
                    )

        if range_error is None:
            top_pitchers, bottom_pitchers, all_pitchers_summary, general_stats = process_data(
                start_str, end_str, num_pitchers
            )

            top_pitchers_data = []
            for pitcher_id in top_pitchers:
                summary_df = all_pitchers_summary[pitcher_id].copy()
                summary_df['pitch_type'] = summary_df['pitch_type'].apply(format_pitch_name)
                styled_summary = style_summary_df(summary_df)
                top_pitchers_data.append({
                    'stats': general_stats[pitcher_id],
                    'summary': styled_summary.to_html(classes='table table-striped table-bordered', index=False)
                })

            bottom_pitchers_data = []
            for pitcher_id in bottom_pitchers:
                summary_df = all_pitchers_summary[pitcher_id].copy()
                summary_df['pitch_type'] = summary_df['pitch_type'].apply(format_pitch_name)
                styled_summary = style_summary_df(summary_df)
                bottom_pitchers_data.append({
                    'stats': general_stats[pitcher_id],
                    'summary': styled_summary.to_html(classes='table table-striped table-bordered', index=False)
                })

    return render_template(
        'index.html',
        start_date=start_str,
        end_date=end_str,
        num_pitchers=num_pitchers,
        top_pitchers_data=top_pitchers_data,
        bottom_pitchers_data=bottom_pitchers_data,
        range_error=range_error,
    )


@app.route('/pitch-types')
def pitch_types():
    return render_template('pitch_types.html')

if __name__ == '__main__':
    app.run(debug=True)
