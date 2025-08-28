import discord
from discord import app_commands
from discord.ext import commands
import json

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # /help — List available commands
    @app_commands.command(name="help", description="Show a list of all commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 FrogSMP Bot Commands",
            description="Here's everything I can do:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎮 Player Commands",
            value="`/status` `/online` `/events` `/rank` `/leaderboard` `/donors`",
            inline=False
        )
        embed.add_field(
            name="🛠️ Staff Commands",
            value="`/kick` `/ban` `/clear` `/mute` `/viewreports` `/deletereport`",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # /rank — Show P2W rank
    @app_commands.command(name="rank", description="Show your current rank")
    async def rank(self, interaction: discord.Interaction):
        with open("data/ranks.json", "r") as f:
            ranks = json.load(f)
        user = str(interaction.user.id)
        rank = ranks.get(user, "No Rank")
        await interaction.response.send_message(f"🏆 **Your rank:** `{rank}`", ephemeral=True)

    # /leaderboard — Sorted by kills
    @app_commands.command(name="leaderboard", description="View top players by kills")
    async def leaderboard(self, interaction: discord.Interaction):
        with open("data/kills.json", "r") as f:
            kills = json.load(f)
        sorted_kills = sorted(kills.items(), key=lambda x: x[1], reverse=True)
        top_players = "\n".join([f"**{i+1}.** <@{player}> — `{count}` kills"
                                for i, (player, count) in enumerate(sorted_kills[:10])])
        embed = discord.Embed(title="🏹 Kill Leaderboard", description=top_players, color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # /donors — Renamed to avoid conflict
    @app_commands.command(name="donors", description="View top supporters")
    async def donors(self, interaction: discord.Interaction):
        with open("data/donors.json", "r") as f:
            donors = json.load(f)
        sorted_donors = sorted(donors.items(), key=lambda x: x[1], reverse=True)
        top_donors = "\n".join([f"**{i+1}.** {name} — `${amount}`"
                               for i, (name, amount) in enumerate(sorted_donors)])
        embed = discord.Embed(title="💎 Top Donors", description=top_donors, color=discord.Color.gold())
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
