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
RENDER_URL = os.getenv("RENDER_URL")  # <-- Add this in Render env variables

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
