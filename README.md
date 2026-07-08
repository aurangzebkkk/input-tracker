# Input Tracker

A lightweight system-tray app that counts your daily keystrokes and mouse clicks, and visualises them in a heatmap calendar.

- **macOS** — lives in the menu bar
- **Windows / Linux** — lives in the system tray

Data is stored locally as JSON files in `~/.inputtracker/`. Nothing leaves your machine.

---

## Requirements

- Python 3.8 or newer
- **Linux only** — install these system packages before running `setup.sh`:

  ```bash
  # Ubuntu / Debian
  sudo apt install python3-gi gir1.2-appindicator3-0.1

  # Fedora / RHEL
  sudo dnf install python3-gobject

  # Arch
  sudo pacman -S python-gobject libappindicator-gtk3
  ```

---

## Installation & first run

### macOS

```bash
bash setup.sh
```

This creates a virtual environment, installs dependencies, registers a LaunchAgent so the app starts at login, and launches it immediately.

**After running**, grant Accessibility access so key/click monitoring works:

> System Settings → Privacy & Security → Accessibility → add Terminal (or whichever app you ran the script from)

```
Stop:    launchctl unload ~/Library/LaunchAgents/com.inputtracker.plist
Start:   launchctl load  ~/Library/LaunchAgents/com.inputtracker.plist
```

---

### Linux

```bash
bash setup.sh
```

This creates a virtual environment, installs dependencies, registers a systemd user service so the app starts at login, and launches it immediately.

```
Stop:     systemctl --user stop inputtracker
Disable:  systemctl --user disable inputtracker
Logs:     journalctl --user -u inputtracker -f
```

> **Wayland note**: `pynput` requires XWayland for input monitoring. Most distributions ship XWayland by default. If the app starts but records nothing, ensure XWayland is running.

---

### Windows

Double-click `setup.bat`, or run it from Command Prompt:

```cmd
setup.bat
```

This creates a virtual environment, installs dependencies, adds a startup launcher to your Startup folder so the app runs at login, and launches it immediately (no console window).

If Windows Security prompts about input monitoring, click **Allow**.

```
Stop:             taskkill /f /im pythonw.exe
Remove autostart: delete %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\inputtracker.vbs
```

---

## Running manually (any OS)

If you prefer not to use the setup scripts, or want to run it once without auto-start:

```bash
# create venv and install deps once
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt      # macOS / Linux
# .venv\Scripts\pip install -r requirements.txt  # Windows

# run
.venv/bin/python app.py      # macOS / Linux
# .venv\Scripts\python app.py  # Windows
```

---

## Usage

Click the menu-bar / tray icon to see today's keystroke and click counts. Select **View Calendar** to open a heatmap of your activity over the last six months in your browser.

---

## Data

All data is stored in `~/.inputtracker/` (one JSON file per day):

```
~/.inputtracker/
  2026-07-01.json
  2026-07-02.json
  ...
```

Each file contains:

```json
{"date": "2026-07-08", "keystrokes": 4821, "clicks": 312}
```

---

## Uninstalling

1. Stop the app (see OS-specific commands above).
2. Delete the project folder.
3. Delete `~/.inputtracker/` if you want to remove your data.
4. **macOS**: `rm ~/Library/LaunchAgents/com.inputtracker.plist`
5. **Linux**: `rm ~/.config/systemd/user/inputtracker.service && systemctl --user daemon-reload`
6. **Windows**: delete `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\inputtracker.vbs`
