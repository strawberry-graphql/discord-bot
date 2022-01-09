import asyncio

import nextcord

from src.database import (
    add_notification_for_date,
    get_notification_for_date,
    get_notification_for_discord_message_id,
)
from src.date_utils import add_localized_times_to_embed

from .config import GENERAL_CHANNEL_ID, NOTES_LINK
from .meeting import find_next_event_and_notify_core_team


class StrawberryDiscordClient(nextcord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.check_events_for_next_week())

    async def on_raw_reaction_add(self, reaction):

        assert self.user

        if reaction.user_id == self.user.id:
            return

        message_id = reaction.message_id
        emoji = reaction.emoji

        if emoji.name == "✅" and (
            notification := get_notification_for_discord_message_id(
                message_id, "core_devs"
            )
        ):
            event_date = notification.date.isoformat()
            public_notification = get_notification_for_date(event_date, "public")

            if public_notification:
                return

            channel = client.get_channel(GENERAL_CHANNEL_ID)

            assert isinstance(channel, nextcord.channel.TextChannel)

            embed = nextcord.Embed(color=5814783)
            add_localized_times_to_embed(embed, notification.date)

            message = await channel.send(
                "Hey @everyone 👋 the next monthly meeting will happen "
                f"{notification.date.humanize()} 📅\n"
                f"Realtime notes will be posted here: {NOTES_LINK}.\n\n"
                "Feel free to add any topics you'd like to discuss in the meeting! 🍓",
                embed=embed,
            )

            add_notification_for_date(event_date, message.id, "public")

    async def check_events_for_next_week(self):
        await self.wait_until_ready()
        print("Bot is ready!")

        while not self.is_closed():
            print("Checking for events...")
            await find_next_event_and_notify_core_team(self)
            print("Sleeping for 60 seconds...")
            await asyncio.sleep(60)


client = StrawberryDiscordClient()
