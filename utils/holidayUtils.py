# TODO: add tests once framework is in place
from holidays import country_holidays
from datetime import date

# hard-coded for now
COUNTRY = "DE"
SUBDIV = "SN"


def is_holiday(date: date):
    """Check whether the given date is a holiday in the configured subdivision"""
    this_year = date.today().year
    holidays: dict[date,
                   str] = country_holidays(
                       country=COUNTRY,
                       subdiv=SUBDIV,
                       years=this_year
                   )

    return date in holidays
