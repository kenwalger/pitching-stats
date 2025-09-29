import pandas as pd
from pybaseball import statcast, playerid_reverse_lookup
from datetime import date, timedelta
import warnings

# Suppress FutureWarning from pybaseball
warnings.simplefilter(action='ignore', category=FutureWarning)


def fetch_data(start_str, end_str):
    print(f"Fetching Statcast data from {start_str} to {end_str}...")
    df = statcast(start_dt=start_str, end_dt=end_str)
    return df

def process_pitcher_data(df):
    # Map whiff / CSW
    whiff_map = {'swinging_strike': 1, 'swinging_strike_blocked': 1}
    csw_map = {'swinging_strike': 1, 'swinging_strike_blocked': 1, 'called_strike': 1}

    # Avoid SettingWithCopyWarning
    df = df.copy()
    df['whiff'] = df['description'].map(lambda x: whiff_map.get(x, 0))
    df['csw'] = df['description'].map(lambda x: csw_map.get(x, 0))
    return df

# A flag to ensure we only print debug info once
debug_info_printed = False

def compute_general_stats(df_pitcher):
    # Approximate outs from events (simplified)
    # Drop rows where 'events' is NaN, as they don't represent the end of a plate appearance
    events = df_pitcher['events'].dropna()

    # Define out-producing events
    single_out_events = [
        'strikeout', 'groundout', 'flyout', 'field_out', 'force_out',
        'sac_fly', 'sac_bunt', 'fielders_choice_out', 'bunt_groundout',
        'bunt_pop_out', 'double_play_bunt', 'triple_play_bunt'
    ]
    
    # Calculate outs, handling double and triple plays
    outs = events.isin(single_out_events).sum()
    outs += events.str.contains('double_play', na=False).sum()
    outs += events.str.contains('triple_play', na=False).sum() * 2

    # Standard calculations
    hits = events.isin(['single', 'double', 'triple', 'home_run']).sum()
    walks = events.isin(['walk']).sum()
    hr = events.isin(['home_run']).sum()
    strikeouts = events.isin(['strikeout']).sum()
    
    # Avoid division by zero for innings_pitched
    innings_pitched_val = outs / 3 if outs > 0 else 0
    innings_pitched_str = f"{int(innings_pitched_val)}.{outs % 3}"


    # Per-9 inning stats
    era = (hr * 1) / innings_pitched_val * 9 if innings_pitched_val > 0 else 0
    whip = (walks + hits) / innings_pitched_val if innings_pitched_val > 0 else 0
    k_per_9 = strikeouts / innings_pitched_val * 9 if innings_pitched_val > 0 else 0
    bb_per_9 = walks / innings_pitched_val * 9 if innings_pitched_val > 0 else 0
    hr_per_9 = hr / innings_pitched_val * 9 if innings_pitched_val > 0 else 0

    avg_speed = df_pitcher['release_speed'].mean()
    avg_spin = df_pitcher['release_spin_rate'].mean()
    avg_plate_x = df_pitcher['plate_x'].mean()
    avg_plate_z = df_pitcher['plate_z'].mean()
    
    player_name = df_pitcher['player_name'].iloc[0]
    home_team = df_pitcher['home_team'].iloc[0]
    total_pitches = len(df_pitcher)
    
    return {
        'player_name': player_name,
        'home_team': home_team,
        'total_pitches': total_pitches,
        'innings_pitched': innings_pitched_str,
        'strikeouts': strikeouts,
        'walks': walks,
        'hits': hits,
        'hr': hr,
        'ERA': era,
        'WHIP': whip,
        'K/9': k_per_9,
        'BB/9': bb_per_9,
        'HR/9': hr_per_9,
        'avg_speed': avg_speed,
        'avg_spin': avg_spin,
        'avg_plate_x': avg_plate_x,
        'avg_plate_z': avg_plate_z
    }

def summarize_pitcher(df_pitcher):
    df_pitcher = df_pitcher.sort_values('game_date').copy()

    # Rolling metrics (last 50 pitches)
    df_pitcher['avg_speed_rolling'] = df_pitcher['release_speed'].rolling(50, min_periods=1).mean()
    df_pitcher['avg_spin_rolling'] = df_pitcher['release_spin_rate'].rolling(50, min_periods=1).mean()

    total_pitches_for_pitcher = len(df_pitcher)
    summary = (
        df_pitcher.groupby('pitch_type')
        .agg(
            total_pitches=('pitch_type', 'count'),
            avg_speed=('release_speed', 'mean'),
            avg_spin=('release_spin_rate', 'mean'),
            avg_plate_x=('plate_x', 'mean'),
            avg_plate_z=('plate_z', 'mean'),
            whiff_rate=('whiff', 'mean'),
            csw_rate=('csw', 'mean'),
            hits=('events', lambda x: x.isin(['single', 'double', 'triple', 'home_run']).sum()),
            hr=('events', lambda x: (x == 'home_run').sum()),
            avg_speed_rolling=('avg_speed_rolling', 'last'),
            avg_spin_rolling=('avg_spin_rolling', 'last')
        )
        .reset_index()
    )
    if total_pitches_for_pitcher > 0:
        summary['pitch_percentage'] = (summary['total_pitches'] / total_pitches_for_pitcher) * 100
    else:
        summary['pitch_percentage'] = 0
        
    # Reorder columns to place pitch_percentage after total_pitches
    cols = summary.columns.tolist()
    # Find the index of total_pitches
    total_pitches_index = cols.index('total_pitches')
    # Remove pitch_percentage and insert it after total_pitches
    cols.remove('pitch_percentage')
    cols.insert(total_pitches_index + 1, 'pitch_percentage')
    summary = summary[cols]

    return summary

def process_data(start_dt, end_dt, n=5):
    df = fetch_data(start_dt, end_dt)
    if df.empty:
        return [], [], {}, {}
        
    df = process_pitcher_data(df)

    # Identify starting pitchers by finding the first pitch of each game
    starters_mlbam_ids = df.sort_values(by=['game_pk', 'inning', 'at_bat_number', 'pitch_number'], ascending=True)
    starters_mlbam_ids = starters_mlbam_ids.groupby('game_pk')['pitcher'].first().unique()
    
    # Filter the main DataFrame to only include starters
    starters_df = df[df['pitcher'].isin(starters_mlbam_ids)].copy()
    
    if starters_df.empty:
        return [], [], {}, {}

    # Rank starters by their total pitch counts
    pitch_counts = starters_df.groupby('pitcher')['pitch_type'].count().sort_values(ascending=False)
    
    top_pitchers = pitch_counts.head(n).index
    bottom_pitchers = pitch_counts.tail(n).index
    
    pitchers_to_process = top_pitchers.union(bottom_pitchers)

    all_pitchers_summary = {}
    general_stats = {}
    for pitcher_id in pitchers_to_process:
        df_pitcher = df[df['pitcher'] == pitcher_id].copy()
        all_pitchers_summary[pitcher_id] = summarize_pitcher(df_pitcher)
        general_stats[pitcher_id] = compute_general_stats(df_pitcher)

    return top_pitchers, bottom_pitchers, all_pitchers_summary, general_stats

def display_data(pitcher_ids, category, all_pitchers_summary, general_stats):
    print(f"\n========== {category} {len(pitcher_ids)} STARTERS ==========")
    for pitcher_id in pitcher_ids:
        stats = general_stats[pitcher_id]
        summary = all_pitchers_summary[pitcher_id]
        
        header = (
            f"\n{category} STARTER: {stats['player_name']} vs {stats['home_team']} — {stats['innings_pitched']} IP, {stats['total_pitches']} Pitches\n"
            f"  Rates: ERA: {stats['ERA']:.2f} | WHIP: {stats['WHIP']:.2f} | K/9: {stats['K/9']:.2f} | BB/9: {stats['BB/9']:.2f}\n"
            f"  Totals: {stats['strikeouts']} K | {stats['walks']} BB | {stats['hits']} H | {stats['hr']} HR"
        )
        print(header)
        print(summary.to_string())

# -----------------------------
# Decoder / Legend (for reference)
# -----------------------------
"""
Pitch Types:
    FF = Four-seam fastball
    FS = Split-finger fastball
    SI = Sinker
    SL = Slider
    CH = Changeup
    FC = Cutter
    ST = Two-seam fastball
CSW Rate = Called Strike + Whiff rate (proportion of pitches ending in strike or swing-and-miss)
Whiff Rate = Swing-and-miss only
plate_x = horizontal location over the plate (feet, center = 0)
plate_z = vertical location over the plate (feet, top = sz_top, bottom = sz_bot)
release_spin_rate = spin rate in RPM
hits / hr = number of hits / home runs allowed
"""
