import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # /kick
    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 {member} has been kicked. Reason: `{reason}`", ephemeral=True)

    # /ban
    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 {member} has been banned. Reason: `{reason}`", ephemeral=True)

    # /clear <n>
    @app_commands.command(name="clear", description="Delete messages in bulk")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted `{amount}` messages.", ephemeral=True)

    # /mute
    @app_commands.command(name="mute", description="Mute a member")
    @app_commands.default_permissions(mute_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member):
        await member.edit(mute=True)
        await interaction.response.send_message(f"🔇 {member} has been muted.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
