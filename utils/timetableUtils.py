from datetime import datetime, timedelta, timezone
from typing import Any
import warnings
from utils.constants import Constants
import requests
from requests import RequestException
from urllib3.exceptions import InsecureRequestWarning


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


def _format_entries(grouped_days: dict) -> str:
    """Format grouped timtetable entries into multi-line string."""

    output = ""
    for date, entries in grouped_days.items():
        output += f"📌 **{date}**:\n"
        for i, entry in enumerate(entries):
            start_dt = datetime.fromtimestamp(entry["start"],
                                              tz=timezone.utc).astimezone(
                                                  Constants.SYSTIMEZONE
                                              )
            end_dt = datetime.fromtimestamp(entry["end"],
                                            tz=timezone.utc).astimezone(
                                                Constants.SYSTIMEZONE
                                            )
            start = start_dt.strftime("%H:%M")
            end = end_dt.strftime("%H:%M")
            title = entry["title"]

            output += f"📚 {entry['description']}\n"
            output += f"🕒 {start}–{end}\n"
            output += f"🏫 Ort: {entry['room']}\n"
            output += f"\n"

        output += "\n"
    return output.strip()


def _fetch_timetable_entries() -> list[dict[str, Any]] | str:
    """Fetch raw timetable JSON entries or return an error message."""
    url = (
        "https://selfservice.campus-dual.de/room/json?userid="
        f"{Constants.SECRETS.CAMPUS_USER}&hash="
        f"{Constants.SECRETS.CAMPUS_HASH}"
    )
    warnings.simplefilter("ignore", InsecureRequestWarning)
    try:
        response = requests.get(url, verify=False, timeout=30)
        if response.status_code != 200:
            return (
                "❌ Fehler beim Abrufen des Stundenplans. Fehlercode: "
                f"{response.status_code}"
            )
        data = response.json()

        # Campus Dual returns HTTP 200 with 'null' JSON when auth fails (ich kann nicht mehr)
        if data is None:
            return (
                "❌ Leere Antwort vom Server. "
                "Mögliche Ursache: ungültiger CAMPUS_USER oder CAMPUS_HASH."
            )
    except RequestException as ex:
        return f"❌ Fehler beim Abrufen des Stundenplans: {ex}"
    except ValueError:
        return "❌ Ungültige JSON-Antwort des Servers."
    except Exception as ex:
        return f"❌ [YIKES] Unbehandelter Fehler: {ex}"
    entries: list[dict[
        str,
        Any]] = (data if isinstance(data,
                                    list) else data.get("entries",
                                                        []))
    return entries


def _filter_entries_for_window(
    entries: list[dict[str,
                       Any]],
    start_date: datetime,
    period_end: datetime
) -> list[dict[str,
               Any]]:
    """Return entries whose start timestamp lies within [start_date, period_end)."""
    return [
        entry for entry in entries if
        start_date <= datetime.fromtimestamp(entry["start"], tz=timezone.utc).
        astimezone(Constants.SYSTIMEZONE) < period_end
    ]


def _group_entries_by_date(
    entries: list[dict[str,
                       Any]]
) -> dict[str,
          list[dict[str,
                    Any]]]:
    """Group entries by localized date string."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        start_dt = datetime.fromtimestamp(e["start"],
                                          tz=timezone.utc).astimezone(
                                              Constants.SYSTIMEZONE
                                          )
        date_key = start_dt.strftime("%A, %d.%m.%Y")
        grouped.setdefault(date_key, []).append(e)
    return grouped


def _empty_message(days: int) -> str:
    if days == 0:
        return "ℹ️ Kein Stundenplan für heute gefunden."
    if days == 1:
        return "ℹ️ Kein Stundenplan für morgen gefunden."
    return f"ℹ️ Kein Stundenplan für die nächsten {days} Tage gefunden."


def _header(days: int) -> str:
    scope = (
        "heute"
        if days == 0 else "morgen" if days == 1 else f"die nächsten {days} Tage"
    )
    return f"📅 **Stundenplan für {scope}**\n\n"


def get_timetable(days: int):
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
