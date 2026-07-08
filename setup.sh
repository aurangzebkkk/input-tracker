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

    echo "→ Installing systemd user service (auto-start at login)..."
    cat > "$SERVICE_DIR/inputtracker.service" << EOF
[Unit]
Description=Input Tracker

[Service]
ExecStart=$VENV/bin/python $SCRIPT_DIR/app.py
Restart=always
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF

    systemctl --user daemon-reload
    systemctl --user enable inputtracker
    systemctl --user start inputtracker

    echo ""
    echo "✓ Done. InputTracker is running in your system tray."
    echo ""
    echo "  IMPORTANT — grant input monitoring access if prompted."
    echo "  If the tray icon does not appear, check that your desktop"
    echo "  environment supports system tray icons (most do)."
    echo ""
    echo "  To stop:    systemctl --user stop inputtracker"
    echo "  To disable: systemctl --user disable inputtracker"
    echo "  Logs:       journalctl --user -u inputtracker"
    echo "  Data lives: ~/.inputtracker/"

else
    echo "Unsupported OS: $OS"
    echo "Run app.py directly: $VENV/bin/python $SCRIPT_DIR/app.py"
    exit 1
fi
