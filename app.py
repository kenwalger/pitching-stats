from flask import Flask, render_template, request
from datetime import date, timedelta
import pandas as pd
from data_processing import process_data
from helper_functions.style import style_summary_df
from constants.pitch_type_mapping import PITCH_TYPE_MAPPING


app = Flask(__name__)

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

    if request.method == 'POST':
        start_str = request.form['start_date']
        end_str = request.form['end_date']
        num_pitchers = int(request.form['num_pitchers'])
        
        top_pitchers, bottom_pitchers, all_pitchers_summary, general_stats = process_data(start_str, end_str, num_pitchers)
        
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


    return render_template('index.html', 
                           start_date=start_str, 
                           end_date=end_str,
                           num_pitchers=num_pitchers,
                           top_pitchers_data=top_pitchers_data,
                           bottom_pitchers_data=bottom_pitchers_data)


@app.route('/pitch-types')
def pitch_types():
    return render_template('pitch_types.html')

if __name__ == '__main__':
    app.run(debug=True)
