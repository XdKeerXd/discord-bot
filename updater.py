import requests

VERSION_URL = "https://raw.githubusercontent.com/XdKeerXd/discord-bot/main/version.txt"
LOCAL_VERSION = "1.0"

def check_update():
    try:
        r = requests.get(VERSION_URL)
        github_version = r.text.strip()

        print("Local version:", LOCAL_VERSION)
        print("GitHub version:", github_version)

        if github_version != LOCAL_VERSION:
            print("⚠ UPDATE AVAILABLE!")
        else:
            print("✅ Bot is up to date")

    except Exception as e:
        print("Update check failed:", e)

check_update()
