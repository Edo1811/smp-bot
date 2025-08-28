import discord
from discord.ext import commands
from discord import app_commands
import json
import os

EVENTS_FILE = os.path.join("data", "events.json")

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="events", description="Show upcoming events")
    async def events(self, interaction: discord.Interaction):
        if not os.path.exists(EVENTS_FILE):
            await interaction.response.send_message("📭 No events found.", ephemeral=True)
            return

        with open(EVENTS_FILE, "r") as f:
            events = json.load(f)

        embed = discord.Embed(title="📅 Upcoming Events", color=discord.Color.blue())
        for event in events:
            embed.add_field(
                name=f"{event['title']} — {event['date']}",
                value=event['description'],
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Events(bot))
