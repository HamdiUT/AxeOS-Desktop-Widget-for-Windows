import tkinter as tk
from tkinter import simpledialog, messagebox
import requests
import threading
import time
import ctypes
import os
import sys
import winreg

# ==============================
# 0) Chemin config dans %APPDATA%
# ==============================
CONFIG_FILE = os.path.join(os.getenv("APPDATA"), "BitaxeWidget_config.txt")
API_PATH = "/api/system/info"

# ==============================
# 1) Gestion de la configuration
# ==============================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            config = {}
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value
            if "miner_name" in config and "miner_ip" in config:
                return config
    return None

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

def add_to_startup():
    exe_path = os.path.abspath(sys.argv[0])
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "BitaxeWidget", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ajouter au démarrage : {e}")

def remove_from_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "BitaxeWidget")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass

def get_config():
    config = load_config()
    if not config:
        root = tk.Tk()
        root.withdraw()
        name = simpledialog.askstring("Configuration", "Entrez le nom de votre mineur :")
        if not name:
            name = "Bitaxe"
        ip = simpledialog.askstring("Configuration", "Entrez l'IP de votre mineur (ex: 192.168.1.10) :")
        if not ip:
            ip = "192.168.1.10"

        startup = messagebox.askyesno("Démarrage", "Voulez-vous lancer le widget automatiquement au démarrage de Windows ?")
        config = {"miner_name": name, "miner_ip": ip}
        save_config(config)
        root.destroy()

        if startup:
            add_to_startup()

    return config

config = get_config()
MINER_NAME = config["miner_name"]
MINER_IP = config["miner_ip"]
API_URL = f"http://{MINER_IP}{API_PATH}"

# ==============================
# 2) API Bitaxe
# ==============================
def fetch_data():
    global API_URL
    try:
        return requests.get(API_URL, timeout=2).json()
    except:
        return None

def format_uptime(sec):
    d = sec // 86400
    h = (sec % 86400) // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{d}d {h}h {m}m {s}s"

def update_widget():
    data = fetch_data()
    if data:
        txt = (
            f"{'Hash Rate':15}: {data['hashRate']:.2f} GH/s\n"
            f"{'Power':15}: {data['power']:.2f} W\n"
            f"{'Temperature':15}: {data['temp']} °C\n"
            f"{'Best Diff':15}: {data['bestDiff']}\n"
            f"{'Best Session':15}: {data['bestSessionDiff']}\n"
            f"{'Uptime':15}: {format_uptime(data['uptimeSeconds'])}\n"
            f"{'Fan Speed':15}: {data['fanrpm']} RPM\n"
        )
    else:
        txt = "API unreachable"
    label_info.config(text=txt)

def updater():
    while True:
        update_widget()
        time.sleep(5)

# ==============================
# 3) UI Tkinter
# ==============================
root = tk.Tk()
root.overrideredirect(True)
root.configure(bg="#202020")

frame = tk.Frame(root, bg="#202020", bd=0)
frame.pack(padx=0, pady=0)

# Frame pour nom + bouton sur la même ligne
top_frame = tk.Frame(frame, bg="#202020")
top_frame.pack(fill="x", padx=10, pady=(10,5))

# Label du nom du mineur
label_name = tk.Label(
    top_frame,
    text=MINER_NAME,
    font=("Segoe UI Variable", 14, "bold"),
    fg="white",
    bg="#202020"
)
label_name.pack(side="left")

# Fonction modification configuration
def open_config_window():
    global MINER_NAME, MINER_IP, API_URL

    root_config = tk.Toplevel()
    root_config.title("Modifier configuration")
    root_config.geometry("300x200")
    root_config.resizable(False, False)
    root_config.attributes("-topmost", True)

    tk.Label(root_config, text="Nom du mineur:").pack(pady=(10,0))
    entry_name = tk.Entry(root_config)
    entry_name.insert(0, label_name.cget("text"))  # texte actuel
    entry_name.pack(pady=(0,10))

    tk.Label(root_config, text="IP du mineur:").pack()
    entry_ip = tk.Entry(root_config)
    entry_ip.insert(0, MINER_IP)  # IP actuelle
    entry_ip.pack(pady=(0,10))

    # Checkbox lancement au démarrage
    startup_var = tk.BooleanVar()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_READ)
        val = winreg.QueryValueEx(key, "BitaxeWidget")[0]
        startup_var.set(True)
        winreg.CloseKey(key)
    except FileNotFoundError:
        startup_var.set(False)

    chk_startup = tk.Checkbutton(
        root_config,
        text="Lancer au démarrage",
        variable=startup_var,
        bg="#FFFFFF"
    )
    chk_startup.pack(pady=(5,10))

    def save_changes():
        nonlocal entry_name, entry_ip, startup_var
        global MINER_NAME, MINER_IP, API_URL
        MINER_NAME = entry_name.get() or "Bitaxe"
        MINER_IP = entry_ip.get() or "192.168.1.10"
        API_URL = f"http://{MINER_IP}{API_PATH}"
        label_name.config(text=MINER_NAME)

        # Gestion démarrage
        if startup_var.get():
            add_to_startup()
        else:
            remove_from_startup()

        # Sauvegarde config avec position
        save_config({"miner_name": MINER_NAME, "miner_ip": MINER_IP,
                     "x": str(root.winfo_x()), "y": str(root.winfo_y())})

        update_widget()  # rafraîchissement immédiat
        root_config.destroy()

    tk.Button(root_config, text="Enregistrer", command=save_changes).pack(pady=(5,10))

# Mini bouton "⚙️" Modifier
btn_config = tk.Button(
    top_frame,
    text="⚙️",
    font=("Segoe UI", 10),
    fg="white",
    bg="#202020",
    bd=0,
    activebackground="#333333",
    command=open_config_window
)
btn_config.pack(side="right")

# Barre stylée rouge
separator = tk.Frame(frame, bg="#FF0000", height=2)
separator.pack(fill="x", padx=10, pady=(0,10))

# Infos du mineur avec police monospace
label_info = tk.Label(
    frame,
    text="Loading...",
    justify="left",
    font=("Consolas", 13),
    fg="white",
    bg="#202020",
    anchor="w"
)
label_info.pack(padx=10, pady=(0,10))

# ==============================
# 4) Drag limité à l'écran
# ==============================
def start_drag(event):
    root._drag_start_x = event.x_root - root.winfo_x()
    root._drag_start_y = event.y_root - root.winfo_y()

def do_drag(event):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    widget_width = root.winfo_width()
    widget_height = root.winfo_height()

    x = event.x_root - root._drag_start_x
    y = event.y_root - root._drag_start_y

    x = max(0, min(x, screen_width - widget_width))
    y = max(0, min(y, screen_height - widget_height))

    root.geometry(f"+{x}+{y}")

    # Sauvegarder la position à chaque drag
    try:
        config = load_config() or {}
        config["x"] = str(x)
        config["y"] = str(y)
        save_config(config)
    except:
        pass

for w in [frame, top_frame, label_name, label_info, btn_config]:
    w.bind("<ButtonPress-1>", start_drag)
    w.bind("<B1-Motion>", do_drag)

# ==============================
# 5) Restaurer la position si elle existe
# ==============================
pos_x = int(config.get("x", 100))
pos_y = int(config.get("y", 100))
root.geometry(f"+{pos_x}+{pos_y}")

# ==============================
# 6) Coller le widget sur le bureau
# ==============================
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
HWND_BOTTOM = 1
SetWindowPos = ctypes.windll.user32.SetWindowPos

def stick_to_desktop():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                 SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

# ==============================
# 7) Démarrage
# ==============================
threading.Thread(target=updater, daemon=True).start()
root.after(400, stick_to_desktop)
root.mainloop()
