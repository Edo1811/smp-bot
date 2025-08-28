import os
import json
import asyncio
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from mcstatus import JavaServer
from dotenv import load_dotenv
from keep_alive import keep_alive

# =========================================================
#   KEEP-ALIVE SERVER FOR RENDER
# =========================================================
keep_alive()

# =========================================================
#   LOAD ENV VARIABLES
# =========================================================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT", "25565"))
RENDER_URL = os.getenv("RENDER_URL")

# =========================================================
#   CHECK REQUIRED VARIABLES
# =========================================================
if not TOKEN:
    raise RuntimeError("❌ Missing DISCORD_TOKEN in environment variables!")
if not SERVER_IP:
    print("⚠️ Warning: SERVER_IP is missing — /status and /online will fail!")

# =========================================================
#   ENSURE DATA FOLDER & FILES EXIST
# =========================================================
os.makedirs("data", exist_ok=True)
required_files = {
    "kills.json": {},
    "donors.json": [],
    "events.json": [],
    "ranks.json": {},
    "reports.json": []
}
for filename, default_content in required_files.items():
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            json.dump(default_content, f, indent=4)

REPORTS_FILE = os.path.join("data", "reports.json")
with open(REPORTS_FILE, "r") as f:
    try:
        reports = json.load(f)
    except json.JSONDecodeError:
        reports = []
        with open(REPORTS_FILE, "w") as f2:
            json.dump(reports, f2, indent=4)

# =========================================================
#   DISCORD BOT SETUP
# =========================================================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# =========================================================
#   SELF-PING TO KEEP BOT ALIVE ON RENDER
# =========================================================
async def self_ping():
    await bot.wait_until_ready()
    if not RENDER_URL:
        print("⚠️ RENDER_URL not set. Self-ping disabled.")
        return

    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RENDER_URL):
                    pass
            print(f"✅ Self-pinged {RENDER_URL}")
        except Exception as e:
            print(f"⚠️ Self-ping failed: {e}")
        await asyncio.sleep(150)  # Ping every 2.5 minutes

# =========================================================
#   SLASH COMMANDS FROM ORIGINAL BOT.PY
# =========================================================

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


@tree.command(name="report", description="Report a cheater or bug")
async def report(interaction: discord.Interaction, reason: str, player: str = "N/A"):
    report_entry = {
        "reporter": str(interaction.user),
        "player": player,
        "reason": reason
    }
    reports.append(report_entry)
    with open(REPORTS_FILE, "w") as f:
        json.dump(reports, f, indent=4)

    embed = discord.Embed(
        title="✅ Report Submitted",
        description=f"Thanks {interaction.user.mention}, your report has been logged.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # If staff channel is set, send report there too
    STAFF_CHANNEL_ID = 1410220376843358218  # <- change this if needed
    staff_channel = bot.get_channel(STAFF_CHANNEL_ID)
    if staff_channel:
        staff_embed = discord.Embed(
            title="🚨 New Report",
            description=f"**Reporter:** {interaction.user.mention}\n**Player:** {player}\n**Reason:** {reason}",
            color=discord.Color.red()
        )
        await staff_channel.send(embed=staff_embed)

# =========================================================
#   LOAD COGS AUTOMATICALLY
# =========================================================
async def load_cogs():
    cogs_dir = "./cogs"
    if not os.path.exists(cogs_dir):
        print("⚠️ No 'cogs' folder found!")
        return

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"🔹 Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")

# =========================================================
#   BOT STARTUP
# =========================================================
@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user} (ID: {bot.user.id})")
    await load_cogs()

    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

    bot.loop.create_task(self_ping())

# =========================================================
#   RUN THE BOT
# =========================================================
try:
    bot.run(TOKEN)
except Exception:
    import traceback
    print("❌ Bot failed to start:")
    traceback.print_exc()
