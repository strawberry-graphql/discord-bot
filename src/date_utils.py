import arrow
import nextcord

LOCATIONS = {
    "🇬🇧 London": "Europe/London",
    "🇮🇹 Rome": "Europe/Rome",
    "🇺🇸 San Francisco": "America/Los_Angeles",
}


def add_localized_times_to_embed(embed: nextcord.Embed, date: arrow.Arrow) -> None:
    for location, timezone in LOCATIONS.items():
        embed.add_field(
            name=location,
            value=(date.to(timezone).format("dddd, MMMM Do YYYY h:mm a ZZZ") + "\n"),
            inline=False,
        )
