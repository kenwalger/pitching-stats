from constants.pitch_data import PITCH_DATA
from constants.pitch_type_mapping import PITCH_TYPE_MAPPING

def style_summary_df(df):
    def apply_styles(row):
        pitch_type_abbr = row['pitch_type']
        pitch_type_full = PITCH_TYPE_MAPPING.get(pitch_type_abbr)

        if not pitch_type_full or pitch_type_full not in PITCH_DATA:
            return [''] * len(row)

        pitch_avg_data = PITCH_DATA[pitch_type_full]
        styles = [''] * len(row)

        # Style avg_speed
        avg_speed_diff = row['avg_speed'] - pitch_avg_data['avg_velocity']
        if avg_speed_diff > 2:
            styles[2] = 'background-color: #d4edda'  # Light Green
        elif avg_speed_diff < -2:
            styles[2] = 'background-color: #f8d7da'  # Light Red
            
        # Style avg_spin
        avg_spin_diff = row['avg_spin'] - pitch_avg_data['avg_spin']
        if avg_spin_diff > 150:
            styles[3] = 'background-color: #d4edda'
        elif avg_spin_diff < -150:
            styles[3] = 'background-color: #f8d7da'

        return styles

    return df.style.apply(apply_styles, axis=1)
