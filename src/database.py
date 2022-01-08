import pathlib
import sqlite3
from typing import NamedTuple

import arrow

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS "meeting_notifications" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "date" DATE,
        "discord_message_id" TEXT NOT NULL,
        "type" TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS "scheduled_events" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "date" DATE,
        "discord_event_id" TEXT NOT NULL
    );
    """,
]

here = pathlib.Path(__file__).parent
root = here.parent

connection = sqlite3.connect(root / "database.db")
cursor = connection.cursor()

for table_creation_statement in TABLES:
    cursor.execute(table_creation_statement)


class Notification(NamedTuple):
    date: arrow.Arrow
    discord_message_id: int


def get_notification_for_date(date: str, notification_type: str) -> Notification | None:
    cursor.execute(
        "SELECT date, discord_message_id FROM meeting_notifications "
        "WHERE date = ? AND type = ?",
        (date, notification_type),
    )

    row = cursor.fetchone()

    if row:
        date, message_id = row

        return Notification(date=arrow.get(date), discord_message_id=int(message_id))

    return None


def add_notification_for_date(
    date: str, discord_message_id: int, notification_type: str
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

        return Notification(date=arrow.get(date), discord_message_id=int(message_id))

    return None


def get_scheduled_event_for_date(date: str) -> str | None:
    cursor.execute(
        "SELECT discord_event_id FROM scheduled_events " "WHERE date = ?",
        (date,),
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    return None


def add_scheduled_event_for_date(date: str, discord_event_id: int) -> None:
    cursor.execute(
        "INSERT INTO scheduled_events " "(date, discord_event_id) VALUES (?, ?)",
        (date, discord_event_id),
    )

    connection.commit()
