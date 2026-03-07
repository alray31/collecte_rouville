"""Parsing du calendrier ICS Publidata pour Collecte Rouville."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from icalendar import Calendar

from .const import COLLECTE_TYPES


def _to_date(val) -> date | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    return None


def parse_collecte_events(cal: Calendar) -> dict[str, Any]:
    """
    Parcourt tous les VEVENT du calendrier ICS.
    Retourne un dict {type_clé: {prochaine_date, jours_restants, dates_futures, summary}}.
    """
    today = date.today()
    buckets: dict[str, list[tuple[date, str]]] = {k: [] for k in COLLECTE_TYPES}

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary_raw = str(component.get("SUMMARY", ""))
        description_raw = str(component.get("DESCRIPTION", ""))
        texte = (summary_raw + " " + description_raw).lower()

        dt_val = component.get("DTSTART")
        if dt_val is None:
            continue
        event_date = _to_date(dt_val.dt)
        if event_date is None or event_date < today:
            continue

        for ctype, meta in COLLECTE_TYPES.items():
            for kw in meta["keywords"]:
                if kw in texte:
                    buckets[ctype].append((event_date, summary_raw))
                    break  # un seul match par type par événement

    result: dict[str, Any] = {}
    for ctype, events in buckets.items():
        events_sorted = sorted(set(events), key=lambda x: x[0])
        if events_sorted:
            next_date, next_summary = events_sorted[0]
            result[ctype] = {
                "prochaine_date": next_date,
                "prochaine_datetime": datetime.combine(next_date, datetime.min.time()),
                "jours_restants": (next_date - today).days,
                "dates_futures": [d.isoformat() for d, _ in events_sorted],
                "summary": next_summary,
            }
        else:
            result[ctype] = {
                "prochaine_date": None,
                "prochaine_datetime": None,
                "jours_restants": None,
                "dates_futures": [],
                "summary": None,
            }

    return result
