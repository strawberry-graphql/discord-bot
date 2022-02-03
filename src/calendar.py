import httpx
from ics import Calendar, Event

from .config import CALENDAR_URL


def get_next_meeting() -> Event | None:
    calendar = Calendar(httpx.get(CALENDAR_URL).text)

    try:
        return list(calendar.events)[0]
    except IndexError:
        return None
