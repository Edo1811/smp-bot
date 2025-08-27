import discord
from discord import app_commands
from discord.ext import commands
import json

class Reports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # /viewreports — Show all reports
    @app_commands.command(name="viewreports", description="View all reports")
    @app_commands.default_permissions(manage_messages=True)
    async def viewreports(self, interaction: discord.Interaction):
        with open("data/reports.json", "r") as f:
            reports = json.load(f)
        if not reports:
            await interaction.response.send_message("✅ No reports found!", ephemeral=True)
            return
        report_list = "\n".join(
            [f"**{i+1}.** Reporter: <@{r['reporter']}>, Player: `{r['player']}`, Reason: {r['reason']}"
             for i, r in enumerate(reports)]
        )
        embed = discord.Embed(title="📄 Reports", description=report_list, color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # /deletereport <id>
    @app_commands.command(name="deletereport", description="Delete a report by ID")
    @app_commands.default_permissions(manage_messages=True)
    async def deletereport(self, interaction: discord.Interaction, report_id: int):
        with open("data/reports.json", "r") as f:
            reports = json.load(f)
        if report_id < 1 or report_id > len(reports):
            await interaction.response.send_message("❌ Invalid report ID.", ephemeral=True)
            return
        reports.pop(report_id - 1)
        with open("data/reports.json", "w") as f:
            json.dump(reports, f, indent=4)
        await interaction.response.send_message(f"🗑️ Report `{report_id}` deleted.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Reports(bot))
