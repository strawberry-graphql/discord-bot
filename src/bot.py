import asyncio
from pathlib import Path

import nextcord
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from nextcord import RawReactionActionEvent

from src.database import (
    add_notification_for_date,
    get_notification_for_date,
    get_notification_for_discord_message_id,
)
from src.date_utils import add_localized_times_to_embed

from .config import (
    GENERAL_CHANNEL_ID,
    MEETING_WATCHERS_ROLE_ID,
    NOTES_LINK,
    REACT_FOR_MEETINGS_NOTIFICATION_MESSAGE_ID,
)
from .meeting import find_next_event_and_notify_core_team

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class StrawberryDiscordClient(nextcord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._check_google_token()

        self.bg_task = self.loop.create_task(self.check_events_for_next_week())

    def _check_google_token(self):
        self.creds = None

        token_path = Path("./token.json")
        credentials_path = Path("./credentials.json")

        assert credentials_path.exists()

        if token_path.exists():
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run

            with token_path.open("w") as token:
                token.write(self.creds.to_json())

            print(f"Saved credentials to {token_path.name}")

    async def on_remove_checkmark_reaction(
        self, reaction: RawReactionActionEvent
    ) -> None:
        message_id = reaction.message_id

        if message_id == REACT_FOR_MEETINGS_NOTIFICATION_MESSAGE_ID:
            # reaction.member happens to be always `None`, so we use the
            # `user_id` instead

            if reaction.guild_id is None:
                print("Guild is None")
                return

            guild = await self.fetch_guild(reaction.guild_id)

            assert guild

            member = await guild.fetch_member(reaction.user_id)

            if member:
                await member.remove_roles(
                    nextcord.Object(id=MEETING_WATCHERS_ROLE_ID),
                    reason="Opted out of meeting notifications via reaction",
                )

    async def on_add_checkmark_reaction(self, reaction: RawReactionActionEvent) -> None:
        message_id = reaction.message_id

        if message_id == REACT_FOR_MEETINGS_NOTIFICATION_MESSAGE_ID:
            if reaction.member is None:
                print("Member is None")
                return

            await reaction.member.add_roles(
                nextcord.Object(id=MEETING_WATCHERS_ROLE_ID),
                reason="Opted in for meeting notifications via reaction",
            )

            return

        if meeting_notification := get_notification_for_discord_message_id(
            message_id, "core_devs"
        ):
            event_date = meeting_notification.date.isoformat()

            if get_notification_for_date(event_date, "public") is not None:
                return

            channel = client.get_channel(GENERAL_CHANNEL_ID)

            assert isinstance(channel, nextcord.channel.TextChannel)

            embed = nextcord.Embed(color=5814783)
            add_localized_times_to_embed(embed, meeting_notification.date)

            role = channel.guild.get_role(MEETING_WATCHERS_ROLE_ID)

            assert role

            message = await channel.send(
                f"Hey {role.mention} 👋 the next monthly meeting will happen "
                "in a few days 📅\n"
                f"Realtime notes will be posted here: {NOTES_LINK}.\n\n"
                "Feel free to add any topics you'd like to discuss in the meeting! 🍓",
                embed=embed,
            )

            add_notification_for_date(event_date, message.id, "public")

    async def on_raw_reaction_add(self, reaction: RawReactionActionEvent) -> None:
        assert self.user

        if reaction.user_id == self.user.id:
            return

        if reaction.emoji.name == "✅":
            await self.on_add_checkmark_reaction(reaction)

    async def on_raw_reaction_remove(self, reaction: RawReactionActionEvent) -> None:
        assert self.user

        if reaction.user_id == self.user.id:
            return

        if reaction.emoji.name == "✅":
            await self.on_remove_checkmark_reaction(reaction)

    async def check_events_for_next_week(self):
        await self.wait_until_ready()
        print("Bot is ready!")

        while not self.is_closed():
            print("Checking for events...")
            await find_next_event_and_notify_core_team(self)
            print("Sleeping for 60 seconds...")
            await asyncio.sleep(60)


client = StrawberryDiscordClient()
