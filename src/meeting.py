import arrow
import ics
import nextcord
from nextcord import ScheduledEventEntityType

from .calendar import get_next_meeting
from .config import CORE_DEVS_CHANNEL_ID, NOTES_LINK, SCHEDULED_EVENT_CHANNEL_ID
from .database import (
    add_notification_for_date,
    add_scheduled_event_for_date,
    get_notification_for_date,
    get_scheduled_event_for_date,
)
from .date_utils import add_localized_times_to_embed


async def add_scheduled_event(next_meeting: ics.Event, guild: nextcord.Guild):
    scheduled_event = get_scheduled_event_for_date(next_meeting.begin.isoformat())

    if not scheduled_event:
        event_channel = guild.get_channel(SCHEDULED_EVENT_CHANNEL_ID)
        assert isinstance(event_channel, nextcord.channel.VoiceChannel)

        event = await guild.create_scheduled_event(
            name="Strawberry Monthly Meeting 🍓",
            channel=event_channel,
            start_time=next_meeting.begin.datetime,
            entity_type=ScheduledEventEntityType.voice,
        )

        add_scheduled_event_for_date(next_meeting.begin.isoformat(), event.id)


async def find_next_event_and_notify_core_team(client: nextcord.Client):
    next_meeting = get_next_meeting()

    if not next_meeting:
        print("No next meeting found")
        return

    next_meeting_in_days = (next_meeting.begin - arrow.now()).days

    channel = client.get_channel(CORE_DEVS_CHANNEL_ID)
    assert isinstance(channel, nextcord.channel.TextChannel)

    if next_meeting_in_days > 25:
        print("Next meeting is more than 25 days away, not adding the scheduled event")
        return

    await add_scheduled_event(next_meeting, channel.guild)

    if next_meeting_in_days > 3:
        print("Next meeting is more than 3 days away")
        return

    event_date = next_meeting.begin.isoformat()
    notification = get_notification_for_date(event_date, "core_devs")

    if not notification:
        embed = nextcord.Embed(color=5814783)

        add_localized_times_to_embed(embed, next_meeting.begin)

        message = await channel.send(
            "Hey @everyone 👋 the next monthly meeting will happen "
            f"{next_meeting.begin.humanize()} 📅\n"
            f"Make sure you update the note doc here: {NOTES_LINK}.\n\n"
            "When ready, react with ✅ to send a notification in the general channel! 🍓",
            embed=embed,
        )
        await message.add_reaction("✅")

        add_notification_for_date(event_date, message.id, "core_devs")
