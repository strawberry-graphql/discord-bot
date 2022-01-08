import pathlib
import sqlite3
from typing import NamedTuple

import arrow

SCHEMA = """
CREATE TABLE IF NOT EXISTS "meeting_notifications" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "date" DATE,
    "discord_message_id" TEXT NOT NULL,
    "type" TEXT NOT NULL
);
"""

here = pathlib.Path(__file__).parent
root = here.parent

connection = sqlite3.connect(root / "database.db")
cursor = connection.cursor()
cursor.execute(SCHEMA)


class Notification(NamedTuple):
    date: arrow.Arrow
    discord_message_id: str


def get_notification_for_date(date: str, notification_type: str) -> Notification | None:
    cursor.execute(
        "SELECT date, discord_message_id FROM meeting_notifications "
        "WHERE date = ? AND type = ?",
        (date, notification_type),
    )

    row = cursor.fetchone()

    if row:
        date, message_id = row

        return Notification(date=arrow.get(date), discord_message_id=message_id)

    return None


def add_notification_for_date(
    date: str, discord_message_id: str, notification_type: str
) -> None:
    cursor.execute(
        "INSERT INTO meeting_notifications "
        "(date, discord_message_id, type) VALUES (?, ?, ?)",
        (date, discord_message_id, notification_type),
    )

    connection.commit()


def get_notification_for_discord_message_id(
    discord_message_id: str, notification_type: str
) -> Notification | None:
    cursor.execute(
        "SELECT date, discord_message_id FROM meeting_notifications "
        "WHERE discord_message_id = ? and type = ?",
        (discord_message_id, notification_type),
    )

    row = cursor.fetchone()

    if row:
        date, message_id = row

        return Notification(date=arrow.get(date), discord_message_id=message_id)

    return None
