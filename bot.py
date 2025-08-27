import os
import json
import discord
from discord import app_commands
from mcstatus import JavaServer
from dotenv import load_dotenv
import asyncio

# Load .env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

# Intents & client
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

REPORTS_FILE = os.path.join("data", "reports.json")

if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, "w") as f:
        json.dump([], f)

with open(REPORTS_FILE, "r") as f:
    try:
        reports = json.load(f)
    except json.JSONDecodeError:
        reports = []
        with open(REPORTS_FILE, "w") as f2:
            json.dump(reports, f2)

# Slash command: check server status
import asyncio

@tree.command(name="status", description="Check Minecraft server status")
async def status(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)  # ⬅ Prevents the 3s timeout

    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")

        # Add a timeout of 2 seconds
        status = await asyncio.wait_for(asyncio.to_thread(server.status), timeout=2.0)

        embed = discord.Embed(
            title="Minecraft Server Status",
            color=discord.Color.green()
        )
        embed.add_field(name="Status", value="🟢 **Online**", inline=False)
        embed.add_field(
            name="Players",
            value=f"{status.players.online}/69",
            inline=False
        )

    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="Minecraft Server Status",
            description="🔴 **Offline** *(timeout)*",
            color=discord.Color.red()
        )
    except Exception:
        embed = discord.Embed(
            title="Minecraft Server Status",
            description="🔴 **Offline**",
            color=discord.Color.red()
        )

    await interaction.followup.send(embed=embed, ephemeral=True)



# Slash command: report cheaters or bugs
@tree.command(name="report", description="Report a cheater or bug")
async def report(interaction: discord.Interaction, reason: str, player: str = "N/A"):
    report_entry = {
        "reporter": str(interaction.user),
        "player": player,
        "reason": reason
    }
    reports.append(report_entry)
    with open("reports.json", "w") as f:
        json.dump(reports, f, indent=4)

    # Send report confirmation
    embed = discord.Embed(
        title="✅ Report Submitted",
        description=f"Thanks {interaction.user.mention}, your report has been logged.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # Send to staff-only channel
    STAFF_CHANNEL_ID = 1410220376843358218
    staff_channel = bot.get_channel(STAFF_CHANNEL_ID)
    if staff_channel:
        staff_embed = discord.Embed(
            title="🚨 New Report",
            description=f"**Reporter:** {interaction.user.mention}\n**Player:** {player}\n**Reason:** {reason}",
            color=discord.Color.red()
        )
        await staff_channel.send(embed=staff_embed)

@tree.command(name="online", description="See who's online right now")
async def online(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")

        # Add timeout for slow/offline servers
        status = await asyncio.wait_for(asyncio.to_thread(server.status), timeout=2.0)

        if status.players.sample:
            player_list = ", ".join([p.name for p in status.players.sample])
        else:
            player_list = "*No players online*"

        embed = discord.Embed(
            title="Players Online",
            description=f"🟢 **{status.players.online}/69**",
            color=discord.Color.green()
        )
        embed.add_field(name="Player List", value=player_list, inline=False)

    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="Players Online",
            description="🔴 **Server Offline** *(timeout)*",
            color=discord.Color.red()
        )
    except Exception:
        embed = discord.Embed(
            title="Players Online",
            description="🔴 **Server Offline**",
            color=discord.Color.red()
        )

    await interaction.followup.send(embed=embed, ephemeral=True)



@tree.command(name="ip", description="Show Minecraft server IP")
async def ip(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🌍 **Server IP:** `{SERVER_IP}`\n📌 **Port:** `{SERVER_PORT}`",
        ephemeral=True
    )

STATUS_CHANNEL_ID = 1410387177891958875

async def update_status_channel():
    await bot.wait_until_ready()
    channel = bot.get_channel(STATUS_CHANNEL_ID)

    while not bot.is_closed():
        try:
            from mcstatus import JavaServer
            server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
            status = server.status()
            # If server is online, update channel name with players
            new_name = f"🟢 Online: {status.players.online}/{status.players.max}"
        except:
            # If server is offline or unreachable
            new_name = "🔴 SMP Offline"

        # Update the channel name only if it changed
        if channel and channel.name != new_name:
            await channel.edit(name=new_name)

        # Update every 60 seconds
        await asyncio.sleep(60)

# On bot startup
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

    # Load cogs automatically
    for cog in ["utility", "moderation", "reports"]:
        await bot.load_extension(f"cogs.{cog}")


