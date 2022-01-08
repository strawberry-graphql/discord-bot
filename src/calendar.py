import arrow
import httpx
from ics import Calendar, Event

from .config import CALENDAR_URL


def get_next_meeting() -> Event | None:
    calendar = Calendar(httpx.get(CALENDAR_URL).text)

    return next(calendar.timeline.start_after(arrow.now()), None)
