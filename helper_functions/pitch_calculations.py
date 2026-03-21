from typing import Optional, Dict, Any
from constants.pitch_data import PITCH_DATA

def calculate_bauer_units(spin_rate: float, velocity: float) -> float:
    """Calculate Bauer Units (spin rate ÷ velocity)."""
    return spin_rate / velocity

def get_pitch_metrics(pitch_type: str) -> Optional[Dict[str, Any]]:
    """Return the full metrics dictionary for a given pitch type."""
    return PITCH_DATA.get(pitch_type)

def get_avg_metric(pitch_type: str, metric: str) -> Optional[float]:
    """
    Generic accessor for pitch metrics.
    Example: get_avg_metric("slider", "avg_spin")
    """
    pitch = PITCH_DATA.get(pitch_type)
    if pitch:
        return pitch.get(metric)
    return None

# Convenience wrappers for common lookups
def get_avg_bauer_units(pitch_type: str) -> Optional[float]:
    return get_avg_metric(pitch_type, "avg_bauer_units")

def get_avg_spin_rate(pitch_type: str) -> Optional[float]:
    return get_avg_metric(pitch_type, "avg_spin")

def get_avg_velocity(pitch_type: str) -> Optional[float]:
    return get_avg_metric(pitch_type, "avg_velocity")
