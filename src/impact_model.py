"""
impact_model.py
Functions for modeling how events affect financial inclusion indicators
over time, with lag and gradual ramp-up. Used by Task 3 (impact modeling)
and Task 4 (forecasting).
"""

import numpy as np

# Default mapping from qualitative impact_magnitude labels to assumed
# percentage-point effects. Documented assumption — adjust based on
# validation against real observed changes.
DEFAULT_MAGNITUDE_MAP = {
    'high': 5.0,
    'medium': 2.5,
    'low': 1.0,
}


def event_effect_at_time(magnitude, lag_months, months_since_event, ramp_months=12):
    """
    Returns the effect (in percentage points) that has materialized by a
    given point in time after an event.

    Parameters
    ----------
    magnitude : float
        Signed magnitude of the full effect (positive = increase,
        negative = decrease).
    lag_months : float
        Months before the effect starts appearing at all.
    months_since_event : float
        How many months have passed since the event occurred.
    ramp_months : float
        How many months it takes for the effect to ramp up to full
        magnitude once it starts (logistic curve).
    """
    if months_since_event < 0:
        return 0.0
    t = months_since_event - lag_months
    if t <= 0:
        return 0.0
    fraction = 1 / (1 + np.exp(-0.5 * (t - ramp_months / 2)))
    return magnitude * fraction


def total_effect_at_date(target_date, indicator_code, events_df, links_df,
                          magnitude_map=None):
    """
    Sum all event effects on a given indicator as of target_date.

    Parameters
    ----------
    target_date : pd.Timestamp
        The date to evaluate cumulative effect at.
    indicator_code : str
        The indicator_code to compute effects for (matches related_indicator
        in impact_link records).
    events_df : pd.DataFrame
        DataFrame of event records (record_type == 'event'), must have
        'record_id' and 'observation_date'.
    links_df : pd.DataFrame
        DataFrame of impact_link records (record_type == 'impact_link'),
        must have 'parent_id', 'related_indicator', 'impact_direction',
        'impact_magnitude', 'lag_months'.
    magnitude_map : dict, optional
        Maps qualitative magnitude labels to numeric pp values.
        Defaults to DEFAULT_MAGNITUDE_MAP.

    Returns
    -------
    float
        Total modeled effect in percentage points.
    """
    if magnitude_map is None:
        magnitude_map = DEFAULT_MAGNITUDE_MAP

    relevant_links = links_df[links_df['related_indicator'] == indicator_code]
    total = 0.0

    for _, link in relevant_links.iterrows():
        event_row = events_df[events_df['record_id'] == link['parent_id']]
        if event_row.empty:
            continue

        event_date = event_row.iloc[0]['observation_date']
        months_since = (
            (target_date.year - event_date.year) * 12
            + (target_date.month - event_date.month)
        )

        magnitude_num = magnitude_map.get(str(link['impact_magnitude']).lower(), 0)
        direction = 1 if str(link['impact_direction']).lower() == 'increase' else -1
        signed_magnitude = magnitude_num * direction

        lag = link['lag_months'] if pd.notna(link['lag_months']) else 0

        total += event_effect_at_time(signed_magnitude, lag, months_since)

    return total


# Note: total_effect_at_date uses pd.notna, so pandas must be imported
# in any script/notebook that calls it, OR we import it here directly:
import pandas as pd