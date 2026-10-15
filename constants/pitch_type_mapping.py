"""Statcast pitch type codes mapped to the keys used in ``PITCH_DATA``.

Codes follow Baseball Savant's current classification. ``ST`` is the sweeper
and ``SV`` is the slurve; Statcast has no separate two-seam fastball code, and
two-seamers are generally classified as ``SI`` (sinker).

Pitch types without an entry in ``PITCH_DATA`` are still displayed, but are not
color-coded against a league average.
"""

from typing import Dict

PITCH_TYPE_MAPPING: Dict[str, str] = {
    "FF": "4_seam_fastball",
    "FA": "fastball",
    "SI": "sinker",
    "FC": "cutter",
    "SL": "slider",
    "ST": "sweeper",
    "SV": "slurve",
    "CU": "curveball",
    "KC": "knuckle_curve",
    "CS": "slow_curve",
    "CH": "changeup",
    "FS": "split_finger_fastball",
    "FO": "forkball",
    "SC": "screwball",
    "KN": "knuckleball",
    "EP": "eephus",
    "PO": "pitchout",
}
