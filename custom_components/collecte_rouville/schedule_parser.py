"""
Parser pour les formats d'horaires Publidata iCalendar.

Formats supportés :
  - "2026 week 3-52/3 Mo 06:00-19:00"     → toutes les 3 semaines le lundi
  - "2026 week 1-53/2 Tu 06:00-19:00"     → toutes les 2 semaines le mardi
  - "2026 week 14-44 Th 06:00-19:00"      → toutes les semaines (jeudi)
  - "2026 Mar 30-2026 Apr 03 07:00-19:00" → plage de dates spécifique
  - "2026 Jan 09 07:00-19:00"             → date unique
  - "2026 Oct 26-30 07:00-19:00"          → plage dans le même mois
  - "2026 Sa[1] 07:00-19:00"              → premier samedi du mois
  - "2025 Sa[-1] 07:00-19:00"             → dernier samedi du mois
"""

import re
from datetime import date, datetime, timedelta
from typing import Optional

# Mapping jour abrégé → numéro weekday (0=lundi)
DAY_MAP = {
    "Mo": 0, "Tu": 1, "We": 2, "Th": 3,
    "Fr": 4, "Sa": 5, "Su": 6,
}

# Mapping mois abrégé → numéro
MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def parse_schedule(opening_hours: str, today: Optional[date] = None) -> list[date]:
    """
    Parse un string d'horaire Publidata et retourne la liste
    de toutes les dates de collecte futures (max 365 jours).
    """
    if today is None:
        today = date.today()

    dates = []
    # Le champ opening_hours peut contenir plusieurs horaires séparés par ";"
    for part in opening_hours.split(";"):
        part = part.strip()
        if not part:
            continue
        parsed = _parse_single(part, today)
        dates.extend(parsed)

    # Dédupliquer, trier, retourner uniquement les dates >= aujourd'hui
    dates = sorted(set(d for d in dates if d >= today))
    return dates


def _parse_single(s: str, today: date) -> list[date]:
    """Parse un seul segment d'horaire."""

    # 1. Format "YYYY Sa[N]" ou "YYYY Sa[-N]" → Nième samedi/dimanche du mois
    m = re.match(
        r"(\d{4})\s+(Mo|Tu|We|Th|Fr|Sa|Su)\[(-?\d+)\]",
        s
    )
    if m:
        year = int(m.group(1))
        weekday = DAY_MAP[m.group(2)]
        nth = int(m.group(3))
        return _nth_weekday_each_month(year, weekday, nth, today)

    # 2. Format "YYYY week W1-W2/step DAY" → toutes les X semaines
    m = re.match(
        r"(\d{4})\s+week\s+(\d+)-(\d+)(?:/(\d+))?\s+(Mo|Tu|We|Th|Fr|Sa|Su)",
        s
    )
    if m:
        year = int(m.group(1))
        w_start = int(m.group(2))
        w_end = int(m.group(3))
        step = int(m.group(4)) if m.group(4) else 1
        weekday = DAY_MAP[m.group(5)]
        return _weekly_range(year, w_start, w_end, step, weekday, today)

    # 3. Format "YYYY Mon DD-YYYY Mon DD" → plage cross-mois (ex: Mar 30-Apr 03)
    # On retourne seulement le premier jour (début de la semaine de collecte)
    m = re.match(
        r"(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)"
        r"-(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)",
        s
    )
    if m:
        d_start = date(int(m.group(1)), MONTH_MAP[m.group(2)], int(m.group(3)))
        if d_start >= today:
            return [d_start]
        return []

    # 4. Format "YYYY Mon DD-DD" → plage dans le même mois
    # On retourne seulement le premier jour
    m = re.match(
        r"(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)-(\d+)",
        s
    )
    if m:
        year = int(m.group(1))
        month = MONTH_MAP[m.group(2)]
        d_start = date(year, month, int(m.group(3)))
        if d_start >= today:
            return [d_start]
        return []

    # 5. Format "YYYY Mon DD" → date unique
    m = re.match(
        r"(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)",
        s
    )
    if m:
        d = date(int(m.group(1)), MONTH_MAP[m.group(2)], int(m.group(3)))
        if d >= today:
            return [d]
        return []

    return []


def _weekly_range(
    year: int, w_start: int, w_end: int, step: int,
    weekday: int, today: date
) -> list[date]:
    """Génère les dates pour un pattern de semaines répétitives."""
    results = []
    cutoff = today + timedelta(days=365)

    w = w_start
    while w <= w_end:
        # ISO week → lundi de cette semaine
        monday = _iso_week_monday(year, w)
        d = monday + timedelta(days=weekday)
        if today <= d <= cutoff:
            results.append(d)
        w += step

    return results


def _iso_week_monday(year: int, week: int) -> date:
    """Retourne le lundi de la semaine ISO donnée."""
    # 4 janvier est toujours en semaine 1
    jan4 = date(year, 1, 4)
    # Lundi de la semaine 1
    week1_monday = jan4 - timedelta(days=jan4.weekday())
    return week1_monday + timedelta(weeks=week - 1)


def _date_range(d_start: date, d_end: date, today: date) -> list[date]:
    """Retourne toutes les dates dans une plage (inclus)."""
    results = []
    cutoff = today + timedelta(days=365)
    current = d_start
    while current <= d_end:
        if today <= current <= cutoff:
            results.append(current)
        current += timedelta(days=1)
    return results


def _nth_weekday_each_month(
    year: int, weekday: int, nth: int, today: date
) -> list[date]:
    """
    Retourne le Nième jour de la semaine de chaque mois de l'année.
    nth=-1 = dernier, nth=1 = premier, etc.
    """
    results = []
    cutoff = today + timedelta(days=365)

    for month in range(1, 13):
        d = _nth_weekday_of_month(year, month, weekday, nth)
        if d and today <= d <= cutoff:
            results.append(d)

    return results


def _nth_weekday_of_month(
    year: int, month: int, weekday: int, nth: int
) -> Optional[date]:
    """Retourne le Nième jour de la semaine dans un mois donné."""
    try:
        if nth > 0:
            # Trouver le premier jour de la semaine dans le mois
            first = date(year, month, 1)
            days_ahead = (weekday - first.weekday()) % 7
            first_occurrence = first + timedelta(days=days_ahead)
            target = first_occurrence + timedelta(weeks=nth - 1)
            if target.month == month:
                return target
        else:
            # Trouver à partir de la fin du mois
            if month == 12:
                last = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                last = date(year, month + 1, 1) - timedelta(days=1)
            days_behind = (last.weekday() - weekday) % 7
            last_occurrence = last - timedelta(days=days_behind)
            target = last_occurrence + timedelta(weeks=nth + 1)
            if target.month == month:
                return target
    except ValueError:
        pass
    return None


def prochaine_date(opening_hours: str, today: Optional[date] = None) -> Optional[date]:
    """Retourne la prochaine date de collecte."""
    dates = parse_schedule(opening_hours, today)
    return dates[0] if dates else None


def dates_futures(
    opening_hours: str, today: Optional[date] = None, max_dates: int = 5
) -> list[date]:
    """Retourne les N prochaines dates de collecte."""
    dates = parse_schedule(opening_hours, today)
    return dates[:max_dates]


# ─── Écocentres ──────────────────────────────────────────────────────────────

def parse_ecocentre_schedule(opening_hours: str, now: Optional[datetime] = None):
    """
    Parse les horaires d'écocentre et retourne:
    - is_open (bool) : ouvert en ce moment
    - prochaine_ouverture (datetime) : prochain créneau d'ouverture
    - horaires_texte (str) : description lisible des horaires

    Formats supportés:
      "2026 Apr 09-2026 Nov 28 Th-Sa 09:00-16:30"  → plage de dates + jours + heures
      "2025 Nov 01-2026 Mar 28 Th-Sa 09:00-16:30"  → idem cross-année
      "2025 Dec 24-2026 Jan 03 off"                 → exception fermé
    """
    from datetime import datetime as dt
    if now is None:
        now = dt.now()

    segments = _parse_ecocentre_segments(opening_hours)
    is_open = _is_open_now(segments, now)
    prochaine = _next_opening(segments, now)

    return {
        "is_open": is_open,
        "prochaine_ouverture": prochaine,
    }


def _parse_ecocentre_segments(opening_hours: str) -> list[dict]:
    """Parse tous les segments d'horaire d'un écocentre."""
    segments = []
    for part in opening_hours.split(";"):
        part = part.strip()
        if not part:
            continue
        seg = _parse_ecocentre_segment(part)
        if seg:
            segments.append(seg)
    return segments


def _parse_ecocentre_segment(s: str) -> Optional[dict]:
    """
    Parse un segment comme:
      "2026 Apr 09-2026 Nov 28 Th-Sa 09:00-16:30"
      "2025 Nov 01-2026 Mar 28 Th-Sa 09:00-16:30"
      "2025 Dec 24-2026 Jan 03 off"
    """
    # Format avec "off" (fermeture exceptionnelle)
    m = re.match(
        r"(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)"
        r"-(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)\s+off",
        s
    )
    if m:
        return {
            "type": "off",
            "start": date(int(m.group(1)), MONTH_MAP[m.group(2)], int(m.group(3))),
            "end": date(int(m.group(4)), MONTH_MAP[m.group(5)], int(m.group(6))),
        }

    # Format normal avec jours et heures
    m = re.match(
        r"(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)"
        r"-(\d{4})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+)"
        r"\s+((?:Mo|Tu|We|Th|Fr|Sa|Su)(?:-(?:Mo|Tu|We|Th|Fr|Sa|Su))?)"
        r"\s+(\d{2}:\d{2})-(\d{2}:\d{2})",
        s
    )
    if m:
        days_str = m.group(7)
        days = _parse_day_range(days_str)
        open_h, open_m = map(int, m.group(8).split(":"))
        close_h, close_m = map(int, m.group(9).split(":"))
        return {
            "type": "open",
            "start": date(int(m.group(1)), MONTH_MAP[m.group(2)], int(m.group(3))),
            "end": date(int(m.group(4)), MONTH_MAP[m.group(5)], int(m.group(6))),
            "days": days,  # liste de weekday (0=lundi)
            "open_time": (open_h, open_m),
            "close_time": (close_h, close_m),
        }

    return None


def _parse_day_range(s: str) -> list[int]:
    """
    Parse "Th-Sa" → [3, 4, 5]
    Parse "We" → [2]
    """
    if "-" in s:
        parts = s.split("-")
        start_day = DAY_MAP[parts[0]]
        end_day = DAY_MAP[parts[1]]
        if end_day >= start_day:
            return list(range(start_day, end_day + 1))
        else:
            return list(range(start_day, 7)) + list(range(0, end_day + 1))
    else:
        return [DAY_MAP[s]]


def _is_open_now(segments: list[dict], now) -> bool:
    """Détermine si l'écocentre est ouvert maintenant."""
    from datetime import datetime as dt
    today = now.date()

    # Vérifier d'abord les exceptions "off"
    for seg in segments:
        if seg["type"] == "off":
            if seg["start"] <= today <= seg["end"]:
                return False

    # Vérifier les segments "open"
    for seg in segments:
        if seg["type"] != "open":
            continue
        if not (seg["start"] <= today <= seg["end"]):
            continue
        if now.weekday() not in seg["days"]:
            continue
        open_h, open_m = seg["open_time"]
        close_h, close_m = seg["close_time"]
        open_dt = now.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
        close_dt = now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)
        if open_dt <= now < close_dt:
            return True

    return False


def _next_opening(segments: list[dict], now) -> Optional[datetime]:
    """Trouve le prochain créneau d'ouverture."""
    from datetime import datetime as dt
    today = now.date()
    cutoff = today + timedelta(days=365)

    candidates = []

    for seg in segments:
        if seg["type"] != "open":
            continue

        # Parcourir les jours dans la plage du segment
        current = max(seg["start"], today)
        while current <= seg["end"] and current <= cutoff:
            if current.weekday() in seg["days"]:
                open_h, open_m = seg["open_time"]
                open_dt = datetime.combine(current, datetime.min.time()).replace(
                    hour=open_h, minute=open_m
                )

                # Si c'est aujourd'hui, vérifier que l'heure n'est pas passée
                if current == today:
                    close_h, close_m = seg["close_time"]
                    close_dt = datetime.combine(current, datetime.min.time()).replace(
                        hour=close_h, minute=close_m
                    )
                    if now >= close_dt:
                        current += timedelta(days=1)
                        continue

                # Vérifier que ce jour n'est pas dans une exception "off"
                is_off = any(
                    s["type"] == "off" and s["start"] <= current <= s["end"]
                    for s in segments
                )
                if not is_off:
                    candidates.append(open_dt)
                    break  # Premier jour valide de ce segment suffit

            current += timedelta(days=1)

    if not candidates:
        return None

    return min(candidates)
