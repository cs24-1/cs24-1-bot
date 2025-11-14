from discord.ext import commands
from typing import TypedDict


class TimetableEntry(TypedDict):
    """
    Campus Dual timetable entry.
    """
    title: str
    start: int
    end: int
    description: str
    room: str
    allDay: bool
    color: str
    editable: bool
    sroom: str
    instructor: str
    sinstructor: str
    remarks: str


Context = commands.Context[commands.Bot]
