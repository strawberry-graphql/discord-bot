import arrow
import nextcord

from .calendar import get_next_meeting
from .config import CORE_DEVS_CHANNEL_ID, NOTES_LINK
from .database import add_notification_for_date, get_notification_for_date
from .date_utils import add_localized_times_to_embed


async def find_next_event_and_notify_core_team(client: nextcord.Client):
    next_meeting = get_next_meeting()

    if not next_meeting:
        print("No next meeting found")
        return

    if (next_meeting.begin - arrow.now()).days > 3:
        print("Next meeting is more than 3 days away")
        return

    event_date = next_meeting.begin.isoformat()
    notification = get_notification_for_date(event_date, "core_devs")

    if not notification:
        channel = client.get_channel(CORE_DEVS_CHANNEL_ID)

        assert isinstance(channel, nextcord.channel.TextChannel)

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
