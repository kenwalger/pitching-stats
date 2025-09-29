from constants.pitch_data import PITCH_DATA

def style_summary_df(df):
    """
    Applies conditional styling to the summary DataFrame.
    - Colors avg_speed and avg_spin based on MLB averages.
    - Sets table-wide border styles.
    """
    def apply_cell_styles(row):
        # Convert the human-readable pitch type back to the dictionary key format
        pitch_type_key = row['pitch_type'].lower().replace(' ', '_')

        if pitch_type_key not in PITCH_DATA:
            return [''] * len(row)

        pitch_avg_data = PITCH_DATA[pitch_type_key]
        styles = [''] * len(row)

        try:
            # Get column indices dynamically
            speed_idx = df.columns.get_loc('avg_speed')
            spin_idx = df.columns.get_loc('avg_spin')
        except KeyError:
            return styles  # Return no styles if columns aren't found

        # Style avg_speed
        avg_speed_diff = row['avg_speed'] - pitch_avg_data['avg_velocity']
        if avg_speed_diff > 2:
            styles[speed_idx] = 'background-color: #d4edda'  # Light Green
        elif avg_speed_diff < -2:
            styles[speed_idx] = 'background-color: #f8d7da'  # Light Red
            
        # Style avg_spin
        avg_spin_diff = row['avg_spin'] - pitch_avg_data['avg_spin']
        if avg_spin_diff > 150:
            styles[spin_idx] = 'background-color: #d4edda'
        elif avg_spin_diff < -150:
            styles[spin_idx] = 'background-color: #f8d7da'

        return styles

    styler = df.style.apply(apply_cell_styles, axis=1)
    
    # Set border properties on all cells and headers
    styler.set_table_styles([
        {'selector': 'th, td', 'props': [('border', '1px solid #dee2e6')]}
    ])

    return styler
