# Input Tracker

A lightweight system-tray app that counts your daily keystrokes and mouse clicks, and visualises them in a heatmap calendar.

- **macOS** — lives in the menu bar
- **Windows / Linux** — lives in the system tray

Data is stored locally as JSON files in `~/.inputtracker/`. Nothing leaves your machine.

---

## Requirements

- Python 3.8 or newer
- **Linux only** — install system packages for the tray icon backend (needed on both X11 and Wayland):

  ```bash
  # Ubuntu / Debian
  sudo apt install python3-gi gir1.2-appindicator3-0.1

  # Fedora / RHEL
  sudo dnf install python3-gobject libappindicator-gtk3

  # Arch
  sudo pacman -S python-gobject libappindicator-gtk3
  ```

  > **GNOME on Wayland** does not show system tray icons by default. Install the
  > [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/)
  > GNOME Shell extension to enable them. KDE Plasma, XFCE, Cinnamon, and most
  > other DEs support tray icons out of the box.

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

**Run `setup.sh` from within your graphical session** (not over SSH) so it can detect your session type and import the correct display environment variables.

```
Stop:     systemctl --user stop inputtracker
Disable:  systemctl --user disable inputtracker
Logs:     journalctl --user -u inputtracker -f
          or: tail -f ~/.inputtracker/err.log
```

#### X11 (Xorg)

Works out of the box once the system packages above are installed. `pynput` uses the X11/Xlib backend automatically when `DISPLAY` is set.

#### Wayland

Two modes depending on whether XWayland is present:

| Setup | How input monitoring works |
|---|---|
| Wayland + XWayland (default on most distros) | `pynput` uses the X11 backend via XWayland. No extra steps needed. |
| Pure Wayland (XWayland disabled) | `pynput` uses the `evdev` backend. Requires the user to be in the `input` group. |

If `setup.sh` detects pure Wayland (no `DISPLAY`), it automatically adds your user to the `input` group and prompts you to log out and back in for it to take effect.

To check which mode you're using:

```bash
echo $XDG_SESSION_TYPE   # "x11" or "wayland"
echo $DISPLAY            # empty = pure Wayland (no XWayland)
```

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
