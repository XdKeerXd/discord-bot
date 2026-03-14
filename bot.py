print("ahmed")
import discord
from discord.ext import commands
import requests
import os
import sys
import shutil
import time

# -------------------
# CONFIG
# -------------------
BOT_FILE = "bot.exe"  # or bot.py if running from Python source
LOCAL_VERSION_FILE = "version.txt"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/XdKeerXd/discord-bot/main/version.txt"
GITHUB_BOT_URL = "https://github.com/XdKeerXd/discord-bot/raw/main/bot.exe"  # raw EXE link

# -------------------
# AUTO-UPDATER
# -------------------
def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return "0.0"
    with open(LOCAL_VERSION_FILE, "r") as f:
        return f.read().strip()

def get_remote_version():
    r = requests.get(GITHUB_VERSION_URL)
    return r.text.strip()

def download_new_bot():
    print("Downloading new version...")
    r = requests.get(GITHUB_BOT_URL, stream=True)
    temp_file = BOT_FILE + ".new"
    with open(temp_file, "wb") as f:
        shutil.copyfileobj(r.raw, f)
    print("Replacing old bot...")
    try:
        os.remove(BOT_FILE)
    except:
        pass
    os.rename(temp_file, BOT_FILE)

def update_version_file(new_version):
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(new_version)

def restart_bot():
    print("Restarting bot...")
    if BOT_FILE.endswith(".exe"):
        os.startfile(BOT_FILE)  # Launch new EXE
        sys.exit()
    else:
        os.execv(sys.executable, ['python'] + [BOT_FILE])

def check_update():
    local = get_local_version()
    remote = get_remote_version()

    print(f"Local version: {local}")
    print(f"GitHub version: {remote}")

    if remote != local:
        print("⚠ New update available!")
        download_new_bot()
        update_version_file(remote)
        restart_bot()
    else:
        print("✅ Bot is up to date")

# Run updater first
check_update()

# -------------------
# DISCORD BOT
# -------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run("YOUR_BOT_TOKEN")  # replace with your bot token
