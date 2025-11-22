# Bitaxe Desktop Widget (Windows)

A lightweight and minimalist desktop widget for Windows that displays live statistics from your Bitaxe miner.  
The widget stays attached to your desktop, updates automatically, and requires no technical skills to use. Widget designed for a single bitaxe or a single nerdqaxe compatible with any miner using AxeOS version 2.10.1 and earlier .
## Features

- Real-time display of:
  - Hash Rate (GH/s)
  - Power consumption (W)
  - Temperature (°C)
  - Best Difficulty
  - Best Session Difficulty
  - Uptime
  - Fan speed (RPM)
- Editable miner name
- Custom miner IP address
- Red styled separator bar
- Saves widget position on screen
- Draggable (locked inside screen boundaries)
- Optional Windows startup
- Updates every 5 seconds
- Runs silently without opening a terminal (`.pyw` file)

---

## Screenshot

<img width="1919" height="1079" alt="Capture d&#39;écran 2025-11-21 164447" src="https://github.com/user-attachments/assets/1f494137-1814-4f0f-8003-7b6b8b710af4" />



## Requirements

### **1. Install Python**

Download Python for Windows:  
https://www.python.org/downloads/windows/

During installation, **check the box**:  
✔️ *“Add Python to PATH”*

---

### **2. Install pip (usually included)**

Verify pip installation:
    
    
    python -m pip --version
## If pip is missing:

1. Download `get-pip.py` from:
   https://bootstrap.pypa.io/get-pip.py

2. Run this command in the same folder as the downloaded file:

   ```cmd
   python get-pip.py

### **3 Install the required Python dependency**
   
    python -m pip install requests


## Running The Widget

1. Download get-pip.py from:
2. Double-click it to run.
(Open with Python if at some point, for example when restarting the PC, you are asked what to open it with, select Python and choose "always".)

On the first launch, the widget will ask for:

Your miner name

Your miner IP address (e.g. 192.168.1.10)

Whether you want the widget to start automatically with Windows

To edit the miner name or IP later, click the small ⚙️ (settings) button on the widget.











