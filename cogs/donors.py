import discord
from discord.ext import commands
from discord import app_commands
import json
import os

DONORS_FILE = os.path.join("data", "donors.json")

class Donors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="topdonors", description="Show the top donors")
    async def topdonors(self, interaction: discord.Interaction):
        if not os.path.exists(DONORS_FILE):
            await interaction.response.send_message("No donors found.", ephemeral=True)
            return

        with open(DONORS_FILE, "r") as f:
            donors = json.load(f)

        embed = discord.Embed(title="💎 Top Donors", color=discord.Color.gold())
        for donor in donors:
            embed.add_field(
                name=donor["name"],
                value=f"💰 {donor['amount']}$",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Donors(bot))
