#!/usr/bin/env python3
import calendar
import json
import os
import platform
import tempfile
import threading
import time
import webbrowser
from datetime import date, datetime
from pathlib import Path

DATA_DIR = os.path.expanduser("~/.inputtracker")
OS = platform.system()  # 'Darwin', 'Windows', 'Linux'


# ── data helpers ──────────────────────────────────────────────────────────────

def _load(day_str):
    path = os.path.join(DATA_DIR, f"{day_str}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"date": day_str, "keystrokes": 0, "clicks": 0}


def _save(day_str, counts):
    path = os.path.join(DATA_DIR, f"{day_str}.json")
    with open(path, "w") as f:
        json.dump(counts, f)


def load_all_data():
    data = {}
    if not os.path.isdir(DATA_DIR):
        return data
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(DATA_DIR, fname)) as f:
                    d = json.load(f)
                    data[d["date"]] = d
            except Exception:
                pass
    return data


# ── calendar html ─────────────────────────────────────────────────────────────

def open_calendar():
    html = build_calendar_html()
    path = os.path.join(tempfile.gettempdir(), "inputtracker.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(Path(path).as_uri())


def build_calendar_html():
    data = load_all_data()
    today = date.today()

    months = []
    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        months.append((year, month))

    totals = [d.get("keystrokes", 0) + d.get("clicks", 0) for d in data.values()]
    max_total = max(totals) if totals else 1

    def day_color(day_str):
        if day_str not in data:
            return "#16162a"
        d = data[day_str]
        total = d.get("keystrokes", 0) + d.get("clicks", 0)
        t = min(total / max_total, 1.0)
        r = int(22 + t * (79 - 22))
        g = int(22 + t * (70 - 22))
        b = int(42 + t * (229 - 42))
        return f"rgb({r},{g},{b})"

    def week_rows(year, month):
        cal = calendar.Calendar(0).monthdayscalendar(year, month)
        rows = ""
        for week in cal:
            cells = ""
            for day in week:
                if day == 0:
                    cells += '<td class="empty"></td>'
                else:
                    d = date(year, month, day)
                    ds = str(d)
                    is_today = " today" if d == today else ""
                    color = day_color(ds)
                    entry = data.get(ds, {})
                    k = entry.get("keystrokes", 0)
                    c = entry.get("clicks", 0)
                    tip = f"Keys: {k:,} · Clicks: {c:,}" if ds in data else "No data"
                    cells += (
                        f'<td class="day{is_today}" style="background:{color}" title="{tip}">'
                        f'<span class="num">{day}</span>'
                        f'<div class="tip">{tip}</div>'
                        f'</td>'
                    )
            rows += f"<tr>{cells}</tr>"
        return rows

    months_html = ""
    for (year, month) in months:
        label = datetime(year, month, 1).strftime("%B %Y")
        months_html += f"""
        <div class="month-block">
          <h3>{label}</h3>
          <table>
            <thead><tr>
              <th>Mo</th><th>Tu</th><th>We</th><th>Th</th><th>Fr</th><th>Sa</th><th>Su</th>
            </tr></thead>
            <tbody>{week_rows(year, month)}</tbody>
          </table>
        </div>"""

    total_keys   = sum(d.get("keystrokes", 0) for d in data.values())
    total_clicks = sum(d.get("clicks", 0)     for d in data.values())
    days_tracked = len(data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Input Tracker</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0d0d1a;
    color: #d0d0e8;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    padding: 48px 40px;
    min-height: 100vh;
  }}
  h1 {{ font-size: 1.5rem; font-weight: 700; color: #e8e8ff; margin-bottom: 4px; }}
  .subtitle {{ color: #555; font-size: 0.82rem; margin-bottom: 36px; }}
  .summary {{ display: flex; gap: 16px; margin-bottom: 48px; flex-wrap: wrap; }}
  .stat {{
    background: #12122a;
    border: 1px solid #252545;
    border-radius: 12px;
    padding: 18px 28px;
    min-width: 150px;
  }}
  .stat .val {{ font-size: 1.9rem; font-weight: 700; color: #6366f1; letter-spacing: -.02em; }}
  .stat .lbl {{ font-size: 0.7rem; color: #666; margin-top: 5px; text-transform: uppercase; letter-spacing: .07em; }}
  .grid {{ display: flex; flex-wrap: wrap; gap: 40px; }}
  .month-block h3 {{
    font-size: 0.72rem;
    font-weight: 600;
    color: #888;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: .1em;
  }}
  table {{ border-collapse: separate; border-spacing: 4px; }}
  th {{
    font-size: 0.6rem;
    color: #444;
    text-align: center;
    padding: 0 2px 6px;
    font-weight: 500;
    width: 32px;
  }}
  td.day {{
    width: 32px;
    height: 32px;
    border-radius: 6px;
    text-align: center;
    position: relative;
    cursor: default;
    transition: transform .12s ease, box-shadow .12s ease;
  }}
  td.day:hover {{
    transform: scale(1.2);
    z-index: 20;
    box-shadow: 0 4px 16px rgba(99,102,241,.4);
  }}
  td.empty {{ width: 32px; height: 32px; }}
  .num {{
    font-size: 0.65rem;
    color: rgba(255,255,255,0.35);
    line-height: 32px;
    display: block;
    user-select: none;
  }}
  td.today {{ outline: 2px solid #6366f1; outline-offset: 2px; }}
  td.today .num {{ color: rgba(255,255,255,0.85); font-weight: 700; }}
  .tip {{
    display: none;
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: #1e1e3a;
    border: 1px solid #35356a;
    border-radius: 8px;
    padding: 7px 12px;
    font-size: 0.68rem;
    white-space: nowrap;
    color: #c0c0e0;
    pointer-events: none;
    z-index: 100;
    box-shadow: 0 4px 20px rgba(0,0,0,.5);
  }}
  td.day:hover .tip {{ display: block; }}
</style>
</head>
<body>
<h1>Input Tracker</h1>
<p class="subtitle">{days_tracked} day{"s" if days_tracked != 1 else ""} recorded · hover a day for details</p>
<div class="summary">
  <div class="stat">
    <div class="val">{total_keys:,}</div>
    <div class="lbl">Keystrokes</div>
  </div>
  <div class="stat">
    <div class="val">{total_clicks:,}</div>
    <div class="lbl">Clicks</div>
  </div>
</div>
<div class="grid">{months_html}</div>
</body>
</html>"""


# ── macOS app (rumps) ─────────────────────────────────────────────────────────

if OS == "Darwin":
    import rumps
    from pynput import keyboard, mouse

    class InputTrackerApp(rumps.App):
        def __init__(self):
            super().__init__("⌨", quit_button=None)
            os.makedirs(DATA_DIR, exist_ok=True)
            self.today_str = str(date.today())
            self.counts = _load(self.today_str)
            self.stats_item = rumps.MenuItem("")
            self.menu = [
                self.stats_item,
                None,
                rumps.MenuItem("View Calendar", callback=self.open_calendar),
                None,
                rumps.MenuItem("Quit", callback=self._quit),
            ]
            self._refresh_menu()
            self._start_listeners()
            rumps.Timer(self._tick, 60).start()

        def _refresh_menu(self):
            k = self.counts["keystrokes"]
            c = self.counts["clicks"]
            self.stats_item.title = f"Keys {k:,}   Clicks {c:,}"

        def _tick(self, _):
            today = str(date.today())
            if today != self.today_str:
                _save(self.today_str, self.counts)
                self.today_str = today
                self.counts = _load(today)
            _save(self.today_str, self.counts)
            self._refresh_menu()

        def _start_listeners(self):
            def on_press(_key):
                self.counts["keystrokes"] += 1

            def on_click(_x, _y, _btn, pressed):
                if pressed:
                    self.counts["clicks"] += 1

            kb = keyboard.Listener(on_press=on_press)
            ms = mouse.Listener(on_click=on_click)
            kb.daemon = True
            ms.daemon = True
            kb.start()
            ms.start()

        def open_calendar(self, _):
            open_calendar()

        def _quit(self, _):
            _save(self.today_str, self.counts)
            rumps.quit_application()


# ── Windows / Linux app (pystray) ─────────────────────────────────────────────

else:
    import pystray
    from PIL import Image, ImageDraw
    from pynput import keyboard, mouse

    def _make_icon():
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([2, 14, 62, 50], radius=8, fill=(99, 102, 241))
        for x in range(8, 56, 11):
            draw.rectangle([x, 19, x + 8, 27], fill=(220, 220, 255))
            draw.rectangle([x, 31, x + 8, 39], fill=(220, 220, 255))
        draw.rectangle([16, 43, 48, 47], fill=(220, 220, 255))
        return img

    class InputTrackerApp:
        def __init__(self):
            os.makedirs(DATA_DIR, exist_ok=True)
            self._lock = threading.Lock()
            self.today_str = str(date.today())
            self.counts = _load(self.today_str)
            self._icon = None
            self._start_listeners()

        def _start_listeners(self):
            def on_press(_key):
                with self._lock:
                    self.counts["keystrokes"] += 1

            def on_click(_x, _y, _btn, pressed):
                if pressed:
                    with self._lock:
                        self.counts["clicks"] += 1

            kb = keyboard.Listener(on_press=on_press)
            ms = mouse.Listener(on_click=on_click)
            kb.daemon = True
            ms.daemon = True
            kb.start()
            ms.start()

        def _tick(self):
            while True:
                time.sleep(60)
                today = str(date.today())
                with self._lock:
                    if today != self.today_str:
                        _save(self.today_str, self.counts)
                        self.today_str = today
                        self.counts = _load(today)
                    _save(self.today_str, self.counts)
                if self._icon:
                    self._icon.menu = self._build_menu()

        def _stats_text(self, icon, item):
            with self._lock:
                k = self.counts["keystrokes"]
                c = self.counts["clicks"]
            return f"Keys {k:,}   Clicks {c:,}"

        def _build_menu(self):
            return pystray.Menu(
                pystray.MenuItem(self._stats_text, None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("View Calendar", lambda icon, item: open_calendar()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", lambda icon, item: icon.stop()),
            )

        def run(self):
            t = threading.Thread(target=self._tick, daemon=True)
            t.start()
            self._icon = pystray.Icon(
                "inputtracker",
                _make_icon(),
                "Input Tracker",
                menu=self._build_menu(),
            )
            self._icon.run()


if __name__ == "__main__":
    InputTrackerApp().run()
