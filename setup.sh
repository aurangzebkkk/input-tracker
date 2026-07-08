#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
OS="$(uname -s)"

echo "→ Creating Python virtual environment..."
python3 -m venv "$VENV"

echo "→ Installing dependencies..."
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo "→ Creating data directory..."
mkdir -p "$HOME/.inputtracker"

# ── macOS ──────────────────────────────────────────────────────────────────

if [ "$OS" = "Darwin" ]; then
    PLIST="$HOME/Library/LaunchAgents/com.inputtracker.plist"

    echo "→ Installing launch agent (auto-start at login)..."
    cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.inputtracker</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV/bin/python</string>
        <string>$SCRIPT_DIR/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.inputtracker/out.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.inputtracker/err.log</string>
</dict>
</plist>
EOF

    echo "→ Starting InputTracker..."
    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load "$PLIST"

    echo ""
    echo "✓ Done. InputTracker is running in your menubar."
    echo ""
    echo "  IMPORTANT — grant Accessibility access:"
    echo "  System Settings → Privacy & Security → Accessibility"
    echo "  Add Terminal (or whichever app you ran this from)."
    echo ""
    echo "  To stop:    launchctl unload ~/Library/LaunchAgents/com.inputtracker.plist"
    echo "  To restart: launchctl load  ~/Library/LaunchAgents/com.inputtracker.plist"
    echo "  Data lives: ~/.inputtracker/"

# ── Linux ──────────────────────────────────────────────────────────────────

elif [ "$OS" = "Linux" ]; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"

    SESSION_TYPE="${XDG_SESSION_TYPE:-x11}"
    UID_NUM="$(id -u)"
    NEEDS_RELOGIN=false

    echo "→ Detected session type: ${SESSION_TYPE}"

    # Bake the current session's display variables into the systemd user manager
    # so they are available to services started after re-login without re-running setup.
    systemctl --user import-environment \
        DISPLAY WAYLAND_DISPLAY XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS 2>/dev/null || true

    # Pure Wayland (no XWayland): pynput needs the evdev backend, which requires
    # the user to be in the 'input' group to read from /dev/input/*.
    if [ "$SESSION_TYPE" = "wayland" ] && [ -z "${DISPLAY:-}" ]; then
        echo "→ Pure Wayland detected (no XWayland). Checking 'input' group membership..."
        if ! id -nG "$USER" | grep -qw input; then
            if sudo usermod -aG input "$USER" 2>/dev/null; then
                echo "  Added $USER to the 'input' group."
                NEEDS_RELOGIN=true
            else
                echo ""
                echo "  WARNING: Could not add to 'input' group automatically."
                echo "  Run manually: sudo usermod -aG input $USER"
                echo "  Then log out and back in, and re-run setup.sh."
                echo ""
            fi
        else
            echo "  Already in 'input' group."
        fi
    fi

    echo "→ Installing systemd user service (auto-start at login)..."
    cat > "$SERVICE_DIR/inputtracker.service" << EOF
[Unit]
Description=Input Tracker
# Start after the graphical session is up so DISPLAY/WAYLAND_DISPLAY are set.
After=graphical-session.target

[Service]
ExecStart=$VENV/bin/python $SCRIPT_DIR/app.py
Restart=on-failure
# XDG_RUNTIME_DIR is required for D-Bus (AppIndicator) and the Wayland socket.
Environment=XDG_RUNTIME_DIR=/run/user/$UID_NUM
# Fallback DISPLAY for X11 sessions where import-environment didn't run yet.
# Overridden at login by the session manager on GNOME/KDE/etc.
Environment=DISPLAY=:0
StandardOutput=append:$HOME/.inputtracker/out.log
StandardError=append:$HOME/.inputtracker/err.log

[Install]
WantedBy=graphical-session.target
EOF

    systemctl --user daemon-reload
    systemctl --user enable inputtracker
    systemctl --user start inputtracker

    echo ""
    echo "✓ Done. InputTracker is running in your system tray."
    echo ""
    if [ "$NEEDS_RELOGIN" = "true" ]; then
        echo "  ACTION REQUIRED: Log out and back in for Wayland input monitoring"
        echo "  to work ('input' group membership takes effect on next login)."
        echo ""
    fi
    echo "  To stop:    systemctl --user stop inputtracker"
    echo "  To disable: systemctl --user disable inputtracker"
    echo "  Logs:       journalctl --user -u inputtracker -f"
    echo "              or: tail -f ~/.inputtracker/err.log"
    echo "  Data lives: ~/.inputtracker/"

else
    echo "Unsupported OS: $OS"
    echo "Run app.py directly: $VENV/bin/python $SCRIPT_DIR/app.py"
    exit 1
fi
