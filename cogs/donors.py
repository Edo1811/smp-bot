import discord
from discord.ext import commands
from discord import app_commands
import json
import os

DONORS_FILE = os.path.join("data", "donors.json")

class Donors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="topdonors", description="Show the top donors leaderboard")
    async def topdonors(self, interaction: discord.Interaction):
        # Check if donors.json exists
        if not os.path.exists(DONORS_FILE):
            await interaction.response.send_message("❌ No donors found.", ephemeral=True)
            return

        # Load donors and sort them by donation amount (descending)
        with open(DONORS_FILE, "r") as f:
            donors = json.load(f)

        if not donors:
            await interaction.response.send_message("❌ No donors found.", ephemeral=True)
            return

        donors.sort(key=lambda x: x["amount"], reverse=True)

        # Create the leaderboard embed
        embed = discord.Embed(
            title="💎 Top Donors Leaderboard",
            description="Thanks to our amazing supporters ❤️",
            color=discord.Color.gold()
        )

        # Add each donor to the embed
        medals = ["🥇", "🥈", "🥉"]
        for i, donor in enumerate(donors[:10]):  # Show top 10 donors max
            medal = medals[i] if i < len(medals) else f"#{i+1}"
            embed.add_field(
                name=f"{medal} {donor['name']}",
                value=f"💰 **{donor['amount']}$** donated",
                inline=False
            )

        # Add footer if there are more donors
        if len(donors) > 10:
            embed.set_footer(text=f"...and {len(donors) - 10} more generous donors!")

        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Donors(bot))
