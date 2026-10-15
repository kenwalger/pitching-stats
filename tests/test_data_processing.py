"""Tests for starter identification, run accounting, ranking, and pitch types.

Each test is written so that it fails against the behavior it guards against,
not just passes against the current code. The comments name the bug each one
would catch.
"""

from typing import Dict, List

import pandas as pd
import pytest

import data_processing
from constants.pitch_type_mapping import PITCH_TYPE_MAPPING
from data_processing import (
    compute_general_stats,
    identify_starts,
    process_data,
    rank_starters,
    runs_allowed,
)

HOME_STARTER = 100
HOME_RELIEVER = 101
AWAY_STARTER = 200
AWAY_RELIEVER = 201


def _pitch(
    game_pk: int,
    inning: int,
    half: str,
    at_bat: int,
    pitch_number: int,
    pitcher: int,
    *,
    events: object = None,
    bat_score: int = 0,
    post_bat_score: int = 0,
    pitch_type: str = "FF",
    game_date: str = "2026-10-24",
) -> Dict[str, object]:
    """Build one synthetic Statcast row with the columns the pipeline reads."""
    return {
        "game_pk": game_pk,
        "inning": inning,
        "inning_topbot": half,
        "at_bat_number": at_bat,
        "pitch_number": pitch_number,
        "pitcher": pitcher,
        "player_name": f"Pitcher {pitcher}",
        "description": "called_strike",
        "events": events,
        "pitch_type": pitch_type,
        "release_speed": 95.0,
        "release_spin_rate": 2300.0,
        "plate_x": 0.0,
        "plate_z": 2.5,
        "game_date": game_date,
        "home_team": "HOU",
        "away_team": "NYY",
        "bat_score": bat_score,
        "post_bat_score": post_bat_score,
    }


def _game_one() -> List[Dict[str, object]]:
    """One game: each team uses a starter for the first inning, then a reliever.

    The home starter throws the top of the first, the away starter throws the
    bottom of the first. The away starter gives up two runs.
    """
    return [
        _pitch(1, 1, "Top", 1, 1, HOME_STARTER, events="strikeout"),
        _pitch(1, 1, "Top", 2, 1, HOME_STARTER, events="groundout"),
        _pitch(1, 1, "Top", 3, 1, HOME_STARTER, events="flyout"),
        _pitch(1, 1, "Bot", 4, 1, AWAY_STARTER, events="home_run", post_bat_score=1),
        _pitch(
            1,
            1,
            "Bot",
            5,
            1,
            AWAY_STARTER,
            events="home_run",
            bat_score=1,
            post_bat_score=2,
        ),
        _pitch(1, 1, "Bot", 6, 1, AWAY_STARTER, events="strikeout", bat_score=2),
        _pitch(1, 1, "Bot", 7, 1, AWAY_STARTER, events="strikeout", bat_score=2),
        _pitch(1, 1, "Bot", 8, 1, AWAY_STARTER, events="strikeout", bat_score=2),
        _pitch(1, 2, "Top", 9, 1, HOME_RELIEVER, events="strikeout"),
        _pitch(1, 2, "Bot", 10, 1, AWAY_RELIEVER, events="strikeout", bat_score=2),
    ]


def _relief_outing_by_home_starter() -> List[Dict[str, object]]:
    """A second game in which the home starter pitches in relief."""
    return [
        _pitch(2, 1, "Top", 1, 1, 300, events="strikeout", game_date="2026-10-25"),
        _pitch(2, 1, "Bot", 2, 1, 400, events="strikeout", game_date="2026-10-25"),
        _pitch(2, 2, "Top", 3, 1, HOME_STARTER, events="walk", game_date="2026-10-25"),
    ]


def test_identify_starts_finds_both_teams_starters() -> None:
    # Guards against taking only the first pitch of each game, which finds the
    # home starter and silently drops every road starter.
    starts = identify_starts(pd.DataFrame(_game_one()))
    assert set(starts["pitcher"]) == {HOME_STARTER, AWAY_STARTER}


def test_identify_starts_excludes_relievers() -> None:
    starts = identify_starts(pd.DataFrame(_game_one()))
    assert HOME_RELIEVER not in set(starts["pitcher"])
    assert AWAY_RELIEVER not in set(starts["pitcher"])


def test_identify_starts_is_independent_of_row_order() -> None:
    df = pd.DataFrame(_game_one()).sample(frac=1, random_state=7)
    starts = identify_starts(df)
    assert set(starts["pitcher"]) == {HOME_STARTER, AWAY_STARTER}


def test_runs_allowed_sums_score_changes() -> None:
    df = pd.DataFrame(_game_one())
    assert runs_allowed(df[df["pitcher"] == AWAY_STARTER]) == 2
    assert runs_allowed(df[df["pitcher"] == HOME_STARTER]) == 0


def test_runs_allowed_without_score_columns_is_none() -> None:
    df = pd.DataFrame(_game_one()).drop(columns=["bat_score", "post_bat_score"])
    assert runs_allowed(df) is None


def test_general_stats_report_runs_not_a_mislabeled_era() -> None:
    # Guards against the old "ERA", which was computed from home runs alone.
    df = pd.DataFrame(_game_one())
    stats = compute_general_stats(df[df["pitcher"] == AWAY_STARTER])
    assert "ERA" not in stats
    assert stats["runs"] == 2
    assert stats["innings_pitched"] == "1.0"
    assert stats["R/9"] == pytest.approx(18.0)
    assert stats["HR/9"] == pytest.approx(18.0)


def test_r9_differs_from_hr9_when_runs_score_without_homers() -> None:
    # A positive control for the fix: with the old formula these two were
    # always identical, so a test where they agree cannot tell them apart.
    rows = [
        _pitch(3, 1, "Top", 1, 1, 500, events="single"),
        _pitch(3, 1, "Top", 2, 1, 500, events="double", post_bat_score=1),
        _pitch(3, 1, "Top", 3, 1, 500, events="strikeout", bat_score=1),
        _pitch(3, 1, "Top", 4, 1, 500, events="strikeout", bat_score=1),
        _pitch(3, 1, "Top", 5, 1, 500, events="strikeout", bat_score=1),
    ]
    stats = compute_general_stats(pd.DataFrame(rows))
    assert stats["HR/9"] == pytest.approx(0.0)
    assert stats["R/9"] == pytest.approx(9.0)


def test_rank_starters_bottom_list_never_repeats_top_list() -> None:
    df = pd.DataFrame(_game_one())
    starts_df = df.merge(identify_starts(df), on=["game_pk", "pitcher"])
    top, bottom = rank_starters(starts_df, n=5)
    assert list(top) == [AWAY_STARTER, HOME_STARTER]
    assert set(top).isdisjoint(set(bottom))


def test_process_data_counts_only_pitches_thrown_in_starts(monkeypatch) -> None:
    df = pd.DataFrame(_game_one() + _relief_outing_by_home_starter())
    monkeypatch.setattr(data_processing, "fetch_data", lambda start, end: df)

    top, bottom, summaries, stats = process_data("2026-10-24", "2026-10-25", n=5)

    home = stats[HOME_STARTER]
    assert home["games_started"] == 1
    assert home["total_pitches"] == 3
    assert home["walks"] == 0  # the walk came in relief, in game 2


def test_sweeper_is_not_compared_against_two_seam_averages() -> None:
    # In Statcast, ST is the sweeper and SV is the slurve.
    assert PITCH_TYPE_MAPPING["ST"] == "sweeper"
    assert PITCH_TYPE_MAPPING["SV"] == "slurve"
    assert "two_seam_fastball" not in PITCH_TYPE_MAPPING.values()
