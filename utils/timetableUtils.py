from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any
import warnings
from utils.constants import Constants
import pytz
import requests
from requests import RequestException
from urllib3.exceptions import InsecureRequestWarning


def get_timetable(days):
    """Fetch and format the timetable from Campus Dual self-service system.

    This function retrieves class schedules from the Campus Dual API and formats them
    into a readable Discord message. It handles time zone conversion and groups entries by date.

    Args:
        days (int): Number of days to fetch the schedule for:
            - 0: Today's schedule only
            - 1: Tomorrow's schedule only
            - n > 1: Schedule for the next n days

    Returns:
        str: A formatted string containing the timetable with:
            - 📅 Date headers (Day of week, DD.MM.YYYY)
            - 📚 Class descriptions
            - 🕒 Start and end times (24h format)
            - 🏫 Room numbers
            Entries are displayed in two columns for better readability.
            Returns an info message if no schedule is found.

    Environment Variables:
        CAMPUS_USER: Campus Dual user ID
        CAMPUS_HASH: Campus Dual authentication hash
    """
    url = f"https://selfservice.campus-dual.de/room/json?userid={Constants.SECRETS.CAMPUS_USER}&hash={Constants.SECRETS.CAMPUS_HASH}"

    # Ignore SSL certificate warnings (unsafe, temporary only)
    warnings.simplefilter("ignore", InsecureRequestWarning)

    try:
        # SSL verification disabled and timeout added
        response = requests.get(
            url,
            verify=False,
            timeout=30
        )  # 30 second timeout, TODO: implement cache

        if response.status_code != 200:
            return f"❌ Fehler beim Abrufen des Stundenplans. Fehlercode: {response.status_code}"

        data = response.json()

        # Campus Dual returns HTTP 200 with 'null' JSON when auth fails (ich kann nicht mehr)
        if data is None:
            return (
                "❌ Leere Antwort vom Server. "
                "Mögliche Ursache: ungültiger CAMPUS_USER oder CAMPUS_HASH."
            )
    except RequestException as entry:
        # further errorhandling: all possible network-/connection errors
        return f"❌ Fehler beim Abrufen des Stundenplans: {str(entry)}"
    except ValueError:
        return "❌ Ungültige JSON-Antwort des Servers."
    except Exception as entry:
        return f"❌ [YIKES] Unbehandelter Fehler: {entry.with_traceback}"

    entries: list[dict[str,
                       Any]
                  ] = data if isinstance(data,
                                         list) else data.get("entries",
                                                             [])

    now = datetime.now(tz=Constants.SYSTIMEZONE)
    today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1) Set time window
    if days == 0:
        start_date = today_midnight
        period_end = today_midnight + timedelta(days=1)
    elif days == 1:
        start_date = today_midnight + timedelta(days=1)
        period_end = start_date + timedelta(days=1)
    else:
        start_date = today_midnight
        period_end = today_midnight + timedelta(days=days)

    # 2) Filter (Timestamp → UTC → Berlin)
    filtered_entries = []
    for entry in entries:
        start_dt = datetime.fromtimestamp(entry["start"],
                                          tz=timezone.utc).astimezone(
                                              Constants.SYSTIMEZONE
                                          )
        if start_date <= start_dt < period_end:
            filtered_entries.append(entry)

    if not filtered_entries:
        if days == 0:
            return "ℹ️ Kein Stundenplan für heute gefunden."
        elif days == 1:
            return "ℹ️ Kein Stundenplan für morgen gefunden."
        return f"ℹ️ Kein Stundenplan für die nächsten {days} Tage gefunden."

    output = f"📅 **Stundenplan für {'heute' if days == 0 else 'morgen' if days == 1 else 'die nächsten ' + str(days) + ' Tage'}**\n\n"

    # Group by date
    days_grouped = {}
    for entry in filtered_entries:
        start_dt = datetime.fromtimestamp(entry["start"])
        date = start_dt.strftime(
            "%A, %d.%m.%Y"
        )  # Date format "Monday, 29.04.2025", TODO: translate

        if date not in days_grouped:
            days_grouped[date] = []

        days_grouped[date].append(entry)

    for date, entries in days_grouped.items():
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
            output += f"🏫 Raum: {entry['room']}\n"
            output += f"\n"

        output += "\n"

    return output.strip()
