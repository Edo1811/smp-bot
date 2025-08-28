import os
import json
import discord
from discord.ext import commands
from discord import app_commands
from mcstatus import JavaServer
from dotenv import load_dotenv
import asyncio
from keep_alive import keep_alive

# Load .env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

# Intents & client
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# Reports JSON setup
REPORTS_FILE = os.path.join("data", "reports.json")
os.makedirs("data", exist_ok=True)

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

# ===== Slash Commands ===== #

@tree.command(name="status", description="Check Minecraft server status")
async def status(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = await asyncio.wait_for(asyncio.to_thread(server.status), timeout=2.0)

        embed = discord.Embed(title="Minecraft Server Status", color=discord.Color.green())
        embed.add_field(name="Status", value="🟢 **Online**", inline=False)
        embed.add_field(name="Players", value=f"{status.players.online}/{status.players.max}", inline=False)

    except asyncio.TimeoutError:
        embed = discord.Embed(title="Minecraft Server Status", description="🔴 **Offline** *(timeout)*", color=discord.Color.red())
    except Exception:
        embed = discord.Embed(title="Minecraft Server Status", description="🔴 **Offline**", color=discord.Color.red())

    await interaction.followup.send(embed=embed, ephemeral=True)


@tree.command(name="report", description="Report a cheater or bug")
async def report(interaction: discord.Interaction, reason: str, player: str = "N/A"):
    report_entry = {"reporter": str(interaction.user), "player": player, "reason": reason}
    reports.append(report_entry)
    with open(REPORTS_FILE, "w") as f:
        json.dump(reports, f, indent=4)

    embed = discord.Embed(title="✅ Report Submitted", description=f"Thanks {interaction.user.mention}, your report has been logged.", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)

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
        status = await asyncio.wait_for(asyncio.to_thread(server.status), timeout=2.0)

        if status.players.sample:
            player_list = ", ".join([p.name for p in status.players.sample])
        else:
            player_list = "*No players online*"

        embed = discord.Embed(
            title="Players Online",
            description=f"🟢 **{status.players.online}/{status.players.max}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Player List", value=player_list, inline=False)

    except asyncio.TimeoutError:
        embed = discord.Embed(title="Players Online", description="🔴 **Server Offline** *(timeout)*", color=discord.Color.red())
    except Exception:
        embed = discord.Embed(title="Players Online", description="🔴 **Server Offline**", color=discord.Color.red())

    await interaction.followup.send(embed=embed, ephemeral=True)


@tree.command(name="ip", description="Show Minecraft server IP")
async def ip(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🌍 **Server IP:** `{SERVER_IP}`\n📌 **Port:** `{SERVER_PORT}`",
        ephemeral=True
    )

# ===== Update Channel Status ===== #

STATUS_CHANNEL_ID = 1410387177891958875

async def update_status_channel():
    await bot.wait_until_ready()
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    while not bot.is_closed():
        try:
            server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
            status = server.status()
            new_name = f"🟢 Online: {status.players.online}/{status.players.max}"
        except:
            new_name = "🔴 SMP Offline"
        if channel and channel.name != new_name:
            await channel.edit(name=new_name)
        await asyncio.sleep(60)

# ===== Load Cogs Dynamically ===== #

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"🔹 Loaded {filename}")
            except Exception as e:
                print(f"⚠️ Failed to load {filename}: {e}")

# ===== Bot Startup ===== #

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await load_cogs()
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"⚠️ Failed to sync commands: {e}")
    bot.loop.create_task(update_status_channel())

# Start bot safely
try:
    keep_alive()
    bot.run(TOKEN)
except Exception as e:
    import traceback
    print("❌ Bot failed to start:")
    traceback.print_exc()

