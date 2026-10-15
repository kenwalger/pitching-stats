"""Fetch Statcast pitch data and summarize starting pitchers.

The pipeline is:

1. :func:`fetch_data` pulls pitch-level Statcast rows for a date range.
2. :func:`process_pitcher_data` adds whiff and CSW indicator columns.
3. :func:`identify_starts` finds the starting pitcher for each team in each game.
4. :func:`process_data` restricts the data to those starts, ranks the starters
   by pitches thrown, and builds per-pitcher summaries.

A note on run prevention: Statcast pitch data does not record earned runs, so
true ERA cannot be computed from it. This module reports **R/9** instead: runs
that scored while the pitcher was on the mound, per nine innings. It is not
earned, and it does not reassign inherited runners, so it will not match an
official ERA.
"""

import warnings
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from pybaseball import statcast

# Suppress FutureWarning from pybaseball
warnings.simplefilter(action="ignore", category=FutureWarning)

#: Events that record exactly one out (double and triple plays are handled separately).
SINGLE_OUT_EVENTS: List[str] = [
    "strikeout",
    "groundout",
    "flyout",
    "field_out",
    "force_out",
    "sac_fly",
    "sac_bunt",
    "fielders_choice_out",
    "bunt_groundout",
    "bunt_pop_out",
    "double_play_bunt",
    "triple_play_bunt",
]

#: Events that count as hits allowed.
HIT_EVENTS: List[str] = ["single", "double", "triple", "home_run"]

#: Minimum pitches thrown in starts to qualify for the effectiveness rankings,
#: roughly one full start. Keeps a pitcher with a handful of great pitches off
#: the top of the list.
MIN_QUALIFYING_PITCHES: int = 75


def fetch_data(start_str: str, end_str: str) -> pd.DataFrame:
    """Fetch pitch-level Statcast data for a date range.

    ``pybaseball.statcast`` requests regular season, postseason, and spring
    training games by default, so a postseason date range returns postseason
    games without any extra filtering.

    :param start_str: First date to include, in ``YYYY-MM-DD`` format.
    :param end_str: Last date to include, in ``YYYY-MM-DD`` format.
    :return: One row per pitch.
    """
    print(f"Fetching Statcast data from {start_str} to {end_str}...")
    return statcast(start_dt=start_str, end_dt=end_str)


def process_pitcher_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add whiff and called-strike-plus-whiff (CSW) indicator columns.

    :param df: Pitch-level Statcast data.
    :return: A copy of ``df`` with integer ``whiff`` and ``csw`` columns.
    """
    whiff_map = {"swinging_strike": 1, "swinging_strike_blocked": 1}
    csw_map = {"swinging_strike": 1, "swinging_strike_blocked": 1, "called_strike": 1}

    df = df.copy()
    df["whiff"] = df["description"].map(lambda x: whiff_map.get(x, 0))
    df["csw"] = df["description"].map(lambda x: csw_map.get(x, 0))
    return df


def identify_starts(df: pd.DataFrame) -> pd.DataFrame:
    """Identify both starting pitchers in every game.

    The first pitch of the top of the first inning is thrown by the **home**
    team's starter, and the first pitch of the bottom of the first is thrown by
    the **away** team's starter. Taking only the first pitch of each game finds
    one starter per game, so this groups by game and half-inning instead.

    :param df: Pitch-level Statcast data.
    :return: One row per start, with columns ``game_pk`` and ``pitcher``.
    """
    ordered = df.sort_values(
        by=["game_pk", "inning", "at_bat_number", "pitch_number"], ascending=True
    )
    starts = (
        ordered.groupby(["game_pk", "inning_topbot"], as_index=False)["pitcher"]
        .first()[["game_pk", "pitcher"]]
        .drop_duplicates()
    )
    return starts.reset_index(drop=True)


def runs_allowed(df_pitcher: pd.DataFrame) -> Optional[int]:
    """Count the runs that scored while this pitcher was pitching.

    Each Statcast row carries the batting team's score before the pitch
    (``bat_score``) and after it (``post_bat_score``). Summing the difference
    over a pitcher's pitches gives the runs scored during his time on the mound.
    This is not earned runs, and runners he left on base who score later are
    charged to whoever was pitching when they scored.

    A missing score is unknown, not zero. If any of the pitcher's rows lacks a
    before or after score, a run could have scored on that pitch without being
    counted, so the total is reported as unknown rather than as an undercount.

    :param df_pitcher: Pitch-level data for one pitcher.
    :return: Runs scored, or ``None`` if the score columns are unavailable or
        any row is missing a score.
    """
    if "bat_score" not in df_pitcher or "post_bat_score" not in df_pitcher:
        return None
    scores = df_pitcher[["bat_score", "post_bat_score"]]
    if scores.isna().any().any():
        return None
    delta = scores["post_bat_score"] - scores["bat_score"]
    return int(delta.clip(lower=0).sum())


def compute_general_stats(df_pitcher: pd.DataFrame) -> Dict[str, Any]:
    """Compute totals and rate stats for one pitcher.

    Outs are approximated from plate-appearance events, so outs recorded on
    pickoffs or caught stealing are not counted.

    :param df_pitcher: Pitch-level data for one pitcher, already restricted to
        the games being summarized.
    :return: A dictionary of totals, rate stats, and averages.
    """
    events = df_pitcher["events"].dropna()

    outs = int(events.isin(SINGLE_OUT_EVENTS).sum())
    outs += int(events.str.contains("double_play", na=False).sum())
    outs += int(events.str.contains("triple_play", na=False).sum()) * 2

    hits = int(events.isin(HIT_EVENTS).sum())
    walks = int(events.isin(["walk"]).sum())
    hr = int(events.isin(["home_run"]).sum())
    strikeouts = int(events.isin(["strikeout"]).sum())
    runs = runs_allowed(df_pitcher)

    innings_pitched_val = outs / 3 if outs > 0 else 0
    innings_pitched_str = f"{outs // 3}.{outs % 3}"

    def per_nine(count: Optional[int]) -> Optional[float]:
        if count is None:
            return None
        return count / innings_pitched_val * 9 if innings_pitched_val > 0 else 0.0

    whip = (walks + hits) / innings_pitched_val if innings_pitched_val > 0 else 0.0

    # Opponent from the most recent game in the data
    last_pitch = df_pitcher.sort_values(by="game_date", ascending=False).iloc[0]
    if last_pitch["inning_topbot"] == "Top":
        pitcher_team = last_pitch["home_team"]
        opponent_team = last_pitch["away_team"]
    else:
        pitcher_team = last_pitch["away_team"]
        opponent_team = last_pitch["home_team"]

    return {
        "player_name": df_pitcher["player_name"].iloc[0],
        "pitcher_team": pitcher_team,
        "opponent_team": opponent_team,
        "games_started": int(df_pitcher["game_pk"].nunique()),
        "total_pitches": len(df_pitcher),
        "innings_pitched": innings_pitched_str,
        "strikeouts": strikeouts,
        "walks": walks,
        "hits": hits,
        "hr": hr,
        "runs": runs,
        "csw_rate": float(df_pitcher["csw"].mean()) if "csw" in df_pitcher else None,
        "R/9": per_nine(runs),
        "WHIP": whip,
        "K/9": per_nine(strikeouts),
        "BB/9": per_nine(walks),
        "HR/9": per_nine(hr),
        "avg_speed": df_pitcher["release_speed"].mean(),
        "avg_spin": df_pitcher["release_spin_rate"].mean(),
        "avg_plate_x": df_pitcher["plate_x"].mean(),
        "avg_plate_z": df_pitcher["plate_z"].mean(),
    }


def summarize_pitcher(df_pitcher: pd.DataFrame) -> pd.DataFrame:
    """Summarize one pitcher's arsenal by pitch type.

    :param df_pitcher: Pitch-level data for one pitcher, with ``whiff`` and
        ``csw`` columns from :func:`process_pitcher_data`.
    :return: One row per pitch type, with usage, velocity, spin, location,
        whiff and CSW rates, and hits allowed.
    """
    df_pitcher = df_pitcher.sort_values("game_date").copy()

    # Rolling metrics (last 50 pitches)
    df_pitcher["avg_speed_rolling"] = (
        df_pitcher["release_speed"].rolling(50, min_periods=1).mean()
    )
    df_pitcher["avg_spin_rolling"] = (
        df_pitcher["release_spin_rate"].rolling(50, min_periods=1).mean()
    )

    total_pitches_for_pitcher = len(df_pitcher)
    summary = (
        df_pitcher.groupby("pitch_type")
        .agg(
            total_pitches=("pitch_type", "count"),
            avg_speed=("release_speed", "mean"),
            avg_spin=("release_spin_rate", "mean"),
            avg_plate_x=("plate_x", "mean"),
            avg_plate_z=("plate_z", "mean"),
            whiff_rate=("whiff", "mean"),
            csw_rate=("csw", "mean"),
            hits=("events", lambda x: x.isin(HIT_EVENTS).sum()),
            hr=("events", lambda x: (x == "home_run").sum()),
            avg_speed_rolling=("avg_speed_rolling", "last"),
            avg_spin_rolling=("avg_spin_rolling", "last"),
        )
        .reset_index()
    )
    if total_pitches_for_pitcher > 0:
        summary["pitch_percentage"] = (
            summary["total_pitches"] / total_pitches_for_pitcher
        ) * 100
    else:
        summary["pitch_percentage"] = 0

    # Place pitch_percentage directly after total_pitches
    cols = summary.columns.tolist()
    cols.remove("pitch_percentage")
    cols.insert(cols.index("total_pitches") + 1, "pitch_percentage")
    return summary[cols]


def rank_starters(
    starts_df: pd.DataFrame, n: int, min_pitches: int = MIN_QUALIFYING_PITCHES
) -> Tuple[pd.Index, pd.Index]:
    """Rank qualifying starters by effectiveness, measured as CSW%.

    CSW% (called strikes plus whiffs, as a share of all pitches) settles quickly,
    so it stays meaningful over short date ranges where runs allowed swing wildly.
    Only starters with at least ``min_pitches`` pitches in their starts qualify.
    Ties are broken by pitches thrown. When there are fewer than ``2 * n``
    qualifiers, the bottom list excludes anyone already in the top list, so no
    pitcher appears twice.

    :param starts_df: Pitch-level data restricted to starts, with a ``csw`` column.
    :param n: Number of pitchers in each list.
    :param min_pitches: Minimum pitches thrown to qualify.
    :return: ``(most_effective, least_effective)`` pitcher ids. The first is
        ordered best first, the second worst first.
    """
    per_pitcher = starts_df.groupby("pitcher").agg(
        csw_rate=("csw", "mean"), pitches=("csw", "size")
    )
    qualified = per_pitcher[per_pitcher["pitches"] >= min_pitches]
    best_first = qualified.sort_values(
        by=["csw_rate", "pitches"], ascending=[False, False]
    )
    top = best_first.head(n).index
    worst_first = qualified.drop(top).sort_values(
        by=["csw_rate", "pitches"], ascending=[True, False]
    )
    bottom = worst_first.head(n).index
    return top, bottom


def process_data(
    start_dt: str,
    end_dt: str,
    n: int = 5,
    min_pitches: int = MIN_QUALIFYING_PITCHES,
) -> Tuple[pd.Index, pd.Index, Dict[Any, pd.DataFrame], Dict[Any, Dict[str, Any]]]:
    """Fetch a date range and summarize its starting pitchers.

    Only pitches thrown in a pitcher's starts are included. A starter who also
    pitched in relief during the range has those relief pitches excluded.

    :param start_dt: First date to include, in ``YYYY-MM-DD`` format.
    :param end_dt: Last date to include, in ``YYYY-MM-DD`` format.
    :param n: Number of starters in each of the most and least effective lists.
    :param min_pitches: Minimum pitches thrown in starts to be ranked.
    :return: ``(top_pitchers, bottom_pitchers, summaries, general_stats)``,
        where the last two are keyed by pitcher id.
    """
    df = fetch_data(start_dt, end_dt)
    if df.empty:
        return pd.Index([]), pd.Index([]), {}, {}

    df = process_pitcher_data(df)

    starts = identify_starts(df)
    starts_df = df.merge(starts, on=["game_pk", "pitcher"], how="inner")
    if starts_df.empty:
        return pd.Index([]), pd.Index([]), {}, {}

    top_pitchers, bottom_pitchers = rank_starters(starts_df, n, min_pitches)

    all_pitchers_summary: Dict[Any, pd.DataFrame] = {}
    general_stats: Dict[Any, Dict[str, Any]] = {}
    for pitcher_id in top_pitchers.union(bottom_pitchers):
        df_pitcher = starts_df[starts_df["pitcher"] == pitcher_id].copy()
        all_pitchers_summary[pitcher_id] = summarize_pitcher(df_pitcher)
        general_stats[pitcher_id] = compute_general_stats(df_pitcher)

    return top_pitchers, bottom_pitchers, all_pitchers_summary, general_stats


def _format_rate(value: Optional[float]) -> str:
    """Format a rate stat, showing ``n/a`` when it could not be computed.

    :param value: The rate, or ``None``.
    :return: The rate to two decimal places, or ``"n/a"``.
    """
    return "n/a" if value is None else f"{value:.2f}"


def _format_pct(value: Optional[float]) -> str:
    """Format a proportion as a percentage, showing ``n/a`` when unavailable.

    :param value: A proportion between 0 and 1, or ``None``.
    :return: The percentage to one decimal place, or ``"n/a"``.
    """
    return "n/a" if value is None else f"{value * 100:.1f}%"


def display_data(
    pitcher_ids: pd.Index,
    category: str,
    all_pitchers_summary: Dict[Any, pd.DataFrame],
    general_stats: Dict[Any, Dict[str, Any]],
) -> None:
    """Print pitcher summaries to the terminal.

    :param pitcher_ids: Pitchers to print, in order.
    :param category: Heading label, such as ``"MOST EFFECTIVE"``.
    :param all_pitchers_summary: Per-pitch-type summaries keyed by pitcher id.
    :param general_stats: Totals and rate stats keyed by pitcher id.
    """
    print(f"\n========== {category}: {len(pitcher_ids)} STARTERS ==========")
    for pitcher_id in pitcher_ids:
        stats = general_stats[pitcher_id]
        summary = all_pitchers_summary[pitcher_id]
        runs = "n/a" if stats["runs"] is None else stats["runs"]

        header = (
            f"\n{stats['player_name']} ({stats['pitcher_team']}), last start vs "
            f"{stats['opponent_team']}: {stats['games_started']} GS, "
            f"{stats['innings_pitched']} IP, {stats['total_pitches']} pitches\n"
            f"  Rates: CSW%: {_format_pct(stats['csw_rate'])} | "
            f"R/9: {_format_rate(stats['R/9'])} | WHIP: {stats['WHIP']:.2f} | "
            f"K/9: {stats['K/9']:.2f} | BB/9: {stats['BB/9']:.2f} | HR/9: {stats['HR/9']:.2f}\n"
            f"  Totals: {runs} R | {stats['strikeouts']} K | {stats['walks']} BB | "
            f"{stats['hits']} H | {stats['hr']} HR"
        )
        print(header)
        print(summary.to_string())


# -----------------------------
# Decoder / Legend (for reference)
# -----------------------------
"""
Pitch types: see constants/pitch_type_mapping.py for the full Statcast list.
    Note that ST is the sweeper and SV is the slurve. Statcast has no separate
    two-seam code; two-seamers are generally classified as SI (sinker).
CSW Rate = Called Strike + Whiff rate (share of pitches ending in a called or swinging strike).
    Used to rank starters as most and least effective, minimum 75 pitches in starts.
Whiff Rate = Swing-and-miss only
R/9 = Runs scored while the pitcher was pitching, per nine innings. Not ERA.
plate_x = horizontal location over the plate (feet, center = 0)
plate_z = vertical location over the plate (feet)
release_spin_rate = spin rate in RPM
hits / hr = number of hits / home runs allowed
"""
