import os
import requests
import shutil
import tkinter as tk
from tkinter import messagebox
import subprocess

# GitHub raw URL
GITHUB_RAW = "https://raw.githubusercontent.com/XdKeerXd/discord-bot/main/"

FILES = ["snake.py", "version.txt"]

VERSION_FILE = "version.txt"
PROGRAM_FILE = "snake.py"


def get_local_version():
    if not os.path.exists(VERSION_FILE):
        return "0"
    with open(VERSION_FILE) as f:
        return f.read().strip()


def get_remote_version():
    try:
        r = requests.get(GITHUB_RAW + "version.txt")
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return None


def download_file(file):
    try:
        r = requests.get(GITHUB_RAW + file)
        if r.status_code == 200:
            with open(file + ".new", "wb") as f:
                f.write(r.content)
            return True
    except:
        pass
    return False


def replace_files():
    for f in FILES:
        new_file = f + ".new"
        if os.path.exists(new_file):
            if os.path.exists(f):
                os.remove(f)
            os.rename(new_file, f)


def update_app():
    local = get_local_version()
    remote = get_remote_version()

    if not remote:
        messagebox.showerror("Updater", "Cannot reach GitHub.")
        return

    if local == remote:
        messagebox.showinfo("Updater", "You already have the latest version.")
        return

    success = True

    for f in FILES:
        if not download_file(f):
            success = False

    if success:
        replace_files()
        messagebox.showinfo("Updater", "Update successful!")
    else:
        messagebox.showerror("Updater", "Update failed.")


def run_game():
    if not os.path.exists(PROGRAM_FILE):
        messagebox.showerror("Error", "snake.py not found.")
        return

    subprocess.Popen(["python", PROGRAM_FILE])


# GUI
root = tk.Tk()
root.title("Snake Game Updater")
root.geometry("320x200")

tk.Label(root, text="Snake Game Updater", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="Check for Updates", command=update_app, width=20).pack(pady=10)
tk.Button(root, text="Play Snake 🐍", command=run_game, width=20).pack(pady=5)

root.mainloop()