import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_next_meeting(creds: Credentials) -> dict | None:
    service = build("calendar", "v3", credentials=creds)

    events = []

    try:
        now = f"{datetime.datetime.utcnow().isoformat()}Z"

        events_result = (
            service.events()
            .list(
                calendarId="2i2oq6fu9biq53t205b20agjjc@group.calendar.google.com",
                timeMin=now,
                maxResults=1,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
    except HttpError as error:
        print("An error occurred: %s" % error)

        return None
    finally:
        if not events:
            return None

        return events[0]
