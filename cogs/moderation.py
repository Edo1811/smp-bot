import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(
                f"👢 {member.mention} has been kicked. Reason: {reason}", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to kick this member.", ephemeral=True
            )

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(
                f"🔨 {member.mention} has been banned. Reason: {reason}", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to ban this member.", ephemeral=True
            )

    @app_commands.command(name="clear", description="Clear messages from a channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted **{len(deleted)}** messages!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
