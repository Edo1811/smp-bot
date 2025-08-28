import discord
from discord.ext import commands
from discord import app_commands
import json
import os

RANKS_FILE = os.path.join("data", "ranks.json")

class Ranks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rank", description="Show your current rank")
    async def rank(self, interaction: discord.Interaction):
        if not os.path.exists(RANKS_FILE):
            await interaction.response.send_message("No ranks set yet.", ephemeral=True)
            return

        with open(RANKS_FILE, "r") as f:
            ranks = json.load(f)

        username = str(interaction.user).split("#")[0].lower()
        rank = ranks.get(username, "Default")

        await interaction.response.send_message(
            f"🏆 {interaction.user.mention}, your rank is **{rank}**.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Ranks(bot))
