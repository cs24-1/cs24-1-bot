# TODO: add tests once framework is in place
from datetime import date

from holidays import country_holidays

# hard-coded for now
COUNTRY = "DE"
SUBDIV = "SN"


def is_holiday(check_date: date) -> bool:
    """Check whether the given date is a holiday in the configured subdivision"""

    holidays: dict[date, str]
    holidays = country_holidays(
        country=COUNTRY,
        subdiv=SUBDIV,
        years=check_date.year
    )

    return check_date in holidays
