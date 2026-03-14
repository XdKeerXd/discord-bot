import requests
import os

# RAW GitHub link to your version.txt
VERSION_URL = "https://raw.githubusercontent.com/XdKeerXd/discord-bot/main/version.txt"

# Local version (from local version.txt)
LOCAL_VERSION_FILE = "version.txt"

def get_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return "0.0"
    with open(LOCAL_VERSION_FILE, "r") as f:
        return f.read().strip()

def get_remote_version():
    r = requests.get(VERSION_URL)
    return r.text.strip()

def check_update():
    local = get_local_version()
    remote = get_remote_version()

    print("Local version:", local)
    print("GitHub version:", remote)

    if remote != local:
        print("⚠ NEW UPDATE AVAILABLE!")
    else:
        print("✅ Bot is up to date")

# Run the updater
check_update()
