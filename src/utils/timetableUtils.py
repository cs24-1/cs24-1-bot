import warnings
from datetime import datetime, timedelta, timezone

from discord import AutocompleteContext
from requests import JSONDecodeError, RequestException
from requests_cache import CachedSession
from urllib3.exceptions import InsecureRequestWarning

from models.timetableModels import TimetableEntry
from utils.constants import Constants

_SESSION = CachedSession(
    backend="memory",
    stale_while_revalidate=timedelta(hours=24),
)
"""Cache session for campus API"""

MAX_TIMETABLE_RANGE_DAYS = 30
"""The maximum range a user is allowed to request starting from today"""


def _campus_url() -> str:
    return (
        "https://selfservice.campus-dual.de/room/json?userid="
        f"{Constants.SECRETS.CAMPUS_USER}&hash="
        f"{Constants.SECRETS.CAMPUS_HASH}"
    )


def _local_datetime_from_utc_timestamp(timestamp: float) -> datetime:
    """Get a `datetime` of the SYSTIMEZONE based on a UNIX UTC timestamp"""
    utc_datetime = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return utc_datetime.astimezone(Constants.SYSTIMEZONE)


def _calc_time_window(days: int) -> tuple[datetime, datetime]:
    """Return (start_date, period_end) window based on given days.

    Args:
        days (int):
            0 -> today 00:00 to tomorrow 00:00
            1 -> tomorrow 00:00 to day-after-tomorrow 00:00
            >1 -> today 00:00 to (today + days) 00:00
    """

    now = datetime.now(tz=Constants.SYSTIMEZONE)
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if days == 0:
        start_date = today_midnight
        period_end = today_midnight + timedelta(days=1)
    elif days == 1:
        start_date = today_midnight + timedelta(days=1)
        period_end = start_date + timedelta(days=1)
    else:
        start_date = today_midnight
        period_end = today_midnight + timedelta(days=days)

    return start_date, period_end


def _format_entries(grouped_days: dict[str, list[TimetableEntry]]) -> str:
    """Format grouped timetable entries into multi-line string."""

    output = ""
    for date, entries in grouped_days.items():
        output += f"📌 **{date}**:\n"
        for entry in entries:
            start_dt = _local_datetime_from_utc_timestamp(entry["start"])
            end_dt = _local_datetime_from_utc_timestamp(entry["end"])

            start = start_dt.strftime("%H:%M")
            end = end_dt.strftime("%H:%M")

            output += f"📚 {entry['description']}\n"
            output += f"🕒 {start}–{end}\n"
            output += f"🏫 Ort: {entry['room']}\n"
            output += f"\n"

        output += "\n"
    return output.strip()


def _fetch_timetable_entries(force_refresh: bool = False) -> list[TimetableEntry] | str:
    """Fetch raw timetable JSON entries or return an error message."""
    url = _campus_url()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InsecureRequestWarning)
            response = _SESSION.get(
                url, verify=False, timeout=None, force_refresh=force_refresh
            )
        if response.status_code != 200:
            return (
                "❌ Fehler beim Abrufen des Stundenplans. Fehlercode: "
                f"{response.status_code}"
            )
        entries: list[TimetableEntry] | None = response.json()

        # Campus Dual returns HTTP 200 with 'null' JSON when auth fails (ich kann nicht mehr)
        if entries is None:
            return (
                "❌ Leere Antwort vom Server. "
                "Mögliche Ursache: ungültiger CAMPUS_USER oder CAMPUS_HASH."
            )
    except JSONDecodeError:
        return "❌ Ungültige JSON-Antwort des Servers."
    except RequestException as ex:
        return f"❌ Fehler beim Abrufen des Stundenplans: {ex}"

    return entries


def _filter_entries_for_window(
    entries: list[TimetableEntry], start_date: datetime, period_end: datetime
) -> list[TimetableEntry]:
    """Return entries whose start timestamp lies within [start_date, period_end)."""
    return [
        entry
        for entry in entries
        if start_date <= _local_datetime_from_utc_timestamp(entry["start"]) < period_end
    ]


def _group_entries_by_date(
    entries: list[TimetableEntry],
) -> dict[str, list[TimetableEntry]]:
    """Group entries by localized date string."""
    grouped: dict[str, list[TimetableEntry]] = {}
    for entry in entries:
        start_dt = _local_datetime_from_utc_timestamp(entry["start"])
        date_key = start_dt.strftime("%A, %d.%m.%Y")
        grouped.setdefault(date_key, []).append(entry)
    return grouped


def _empty_message(days: int) -> str:
    if days == 0:
        return "ℹ️ Kein Stundenplan für heute gefunden."
    if days == 1:
        return "ℹ️ Kein Stundenplan für morgen gefunden."
    return f"ℹ️ Kein Stundenplan für die nächsten {days} Tage gefunden."


def _header(days: int) -> str:
    scope = (
        "heute" if days == 0 else "morgen" if days == 1 else f"die nächsten {days} Tage"
    )
    return f"📅 **Stundenplan für {scope}**\n\n"


def days_autocomplete(ctx: AutocompleteContext) -> list[str]:
    """
    Autocompletes filtered days for the timetable argument.
    """
    default_entries = ["today", "tomorrow"] + [
        str(n) for n in range(1, MAX_TIMETABLE_RANGE_DAYS)
    ]

    return [entry for entry in default_entries if entry.startswith(ctx.value)]


def get_timetable(days: int) -> str:
    """Return formatted timetable string for given day range."""
    raw = _fetch_timetable_entries()
    if isinstance(raw, str):
        return raw  # error message

    start_date, period_end = _calc_time_window(days)
    filtered = _filter_entries_for_window(raw, start_date, period_end)
    if not filtered:
        return _empty_message(days)

    grouped = _group_entries_by_date(filtered)
    body = _header(days) + _format_entries(grouped)
    return body


def warm_timetable_cache(force_refresh: bool = False) -> None:
    """Pre-populate or refresh cached timetable response."""
    _ = _fetch_timetable_entries(force_refresh)
