import random

import arrow
import httpx
from ics import Calendar, Event

from .config import CALENDAR_URL


def get_next_meeting() -> Event | None:
    url = f"{CALENDAR_URL}?c={random.randint(0, 9999)}"
    calendar = Calendar(httpx.get(url).text)

    return next(calendar.timeline.start_after(arrow.now()), None)
