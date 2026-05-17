# pocket-cache firmware v0

A 320×240 Pygame firmware simulator for the pocket-cache LCD experience, designed around Pimoroni Display HAT Mini constraints.

## What this does

This is not the full Raspberry Pi hotspot stack. It is the first firmware/UI layer for testing:

- Boot sequence
- Wi-Fi join screen
- Portal QR screen
- Device status
- Library/content status
- Alert state
- Four-button navigation
- RGB LED state simulation
- Simulated telemetry: battery, clients, uptime, storage, service health

## Target hardware

- Pimoroni Display HAT Mini
- 320×240 display
- 4 tactile buttons
- RGB LED

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run simulator

```bash
python -m pocketcache_firmware.main
```

## Simulator controls

| Key | Action |
|---|---|
| Left / A | Previous screen |
| Right / D | Next screen |
| Enter / Space | Select / acknowledge alert |
| M / Esc | Menu / alert toggle |
| B | Drain battery |
| C | Cycle client count |
| E | Toggle Kiwix error |
| R | Reboot simulation |
| Q | Quit |

## Screen flow

```text
Boot → Join Wi-Fi → Open Portal → Status → Library → About
```

Alert state can be triggered by low battery or service error.

## Hardware path

The code is split so the Pygame simulator can later be replaced by a real Display HAT Mini adapter:

```text
pocketcache_firmware/
├── adapters/
│   ├── pygame_adapter.py
│   └── displayhatmini_adapter.py
├── screens/
├── state.py
├── theme.py
├── qr.py
└── main.py
```

`displayhatmini_adapter.py` is a scaffold, not yet active.


## Run on Display HAT Mini hardware

Use this on the Pi terminal/SSH session. It does not need a desktop window.

```bash
cd ~/pocket-cache-firmware-v0-displayhat
source ~/.virtualenvs/displayhatmini/bin/activate
pip install -r requirements.txt
pip install displayhatmini
python -m pocketcache_firmware.displayhat_main
```

Hardware buttons:

| Button | Action |
|---|---|
| A | Previous screen |
| B | Next screen |
| X | Select / acknowledge alert |
| Y | Alert/menu |

The RGB LED mirrors status:
- Green: healthy
- Blue: client connected
- Amber: warning
- Red: critical/service down


## v0-displayhat-polling note

This build polls the Display HAT Mini buttons every frame instead of using
`on_button_pressed()`. This avoids `RuntimeError: Failed to add edge detection`
from `RPi.GPIO.add_event_detect()` on setups where callback-based GPIO edge
detection is unavailable.


## v0 portrait update

This build uses a portrait firmware canvas:

- Logical UI: 240×320
- Physical LCD: 320×240
- The Display HAT adapter rotates the portrait canvas onto the physical screen.
- Small labels now use bold monospace fonts.
- Footer/header labels are uppercase and heavier for the 2" LCD.

Run:

```bash
python -m pocketcache_firmware.displayhat_main
```

If the display is rotated the wrong way, try:

```bash
POCKETCACHE_ROTATION=ccw python -m pocketcache_firmware.displayhat_main
POCKETCACHE_ROTATION=180 python -m pocketcache_firmware.displayhat_main
```


## v0 Sudoku app

This build adds a working Sudoku app to the firmware carousel.

Sudoku uses only the four Display HAT Mini buttons:

| Button | Action |
|---|---|
| A | Move to next editable cell |
| B | Cycle selected number 1–9 |
| X | Set number / clear same number |
| Y | Exit Sudoku back to firmware |

Notes:
- Given puzzle numbers are locked.
- Correct entries show green.
- Incorrect entries show amber and increment `MISS`.
- The app runs inside the same 240×320 portrait firmware canvas.


## v0 Reader + unified controls update

This build adds a simple firmware e-reader and standardizes the four hardware buttons.

Global controls:

| Button | Action |
|---|---|
| A | Back |
| B | Select |
| X | Left / previous |
| Y | Right / next |

Sudoku controls:

| Button | Action |
|---|---|
| A | Exit Sudoku |
| B | Set number / clear same number |
| X | Next editable cell |
| Y | Cycle number 1–9 |

Reader controls:

| Button | Action |
|---|---|
| A | Exit Reader |
| B | Toggle text size |
| X | Previous page |
| Y | Next page |

The reader currently includes a built-in sample text. It is intentionally simple:
large bold monospace text, page-by-page navigation, and a progress bar.


## v0 rotated button mapping update

This build assumes the device is held in portrait orientation with the buttons arranged:

```text
Top row:     X   Y
Bottom row:  A   B
```

Firmware controls are now:

| Physical button | Action |
|---|---|
| X | Back / exit current app |
| Y | Select |
| A | Left / previous |
| B | Right / next |

The Display HAT renderer now defaults to `POCKETCACHE_ROTATION=180`.

Run:

```bash
python -m pocketcache_firmware.displayhat_main
```

If you need to override rotation:

```bash
POCKETCACHE_ROTATION=cw python -m pocketcache_firmware.displayhat_main
POCKETCACHE_ROTATION=ccw python -m pocketcache_firmware.displayhat_main
POCKETCACHE_ROTATION=180 python -m pocketcache_firmware.displayhat_main
```


## v0 app menu update

The firmware now uses an app menu instead of a linear carousel.

Apps:
- About
- Library
- Play: Sudoku
- Read: simple e-reader
- Connect: Portal / Wi-Fi QR
- Status: device info, battery, CPU load, memory, Wi-Fi, clients, served counter

Button mapping remains:

| Physical button | Action |
|---|---|
| X | Back |
| Y | Select / open |
| A | Left / previous menu item |
| B | Right / next menu item |

LED color now changes by app:
- Menu: blue
- About: purple
- Library: green
- Play/Sudoku: pink
- Reader: yellow
- Connect: cyan-blue
- Status: cyan
- Alerts still override app colors with amber/red.


## v0 Settings + autoboot update

New Settings app:
- Change pocket-cache SSID
- Change Wi-Fi password
- Save Wi-Fi config
- Restart hotspot services
- Restart the Pi

Settings controls:

| Button | Action |
|---|---|
| X | Back / delete while editing |
| Y | Select / add character while editing |
| A | Previous row / move cursor left |
| B | Next row / move cursor right |

Notes:
- WPA2 passwords must be at least 8 characters.
- The Settings app writes `/etc/pocket-cache/firmware.json`.
- It also writes a conservative `/etc/hostapd/hostapd.conf` and restarts `hostapd` + `dnsmasq`.
- If run without permission, simulator mode still updates runtime config where possible.

## Auto-boot firmware on the Pi

From the project root on the Pi:

```bash
sudo ./scripts/install-autoboot.sh
```

Check logs:

```bash
sudo journalctl -u pocket-cache-firmware -f
```

Disable autoboot:

```bash
sudo ./scripts/uninstall-autoboot.sh
```

The systemd service runs:

```bash
python -m pocketcache_firmware.displayhat_main
```

with:

```bash
SDL_VIDEODRIVER=dummy
POCKETCACHE_ROTATION=180
POCKETCACHE_CONFIG=/etc/pocket-cache/firmware.json
```


## v0 paged launcher update

The app launcher now:
- Removes app description text.
- Shows four app buttons per page.
- Adds `PAGE n/n` indicator.
- Adds page dots.
- Keeps `A` and `B` as previous/next item navigation.
- Keeps `Y` as open/select and `X` as back.


## v0 portal + offline map demo

This build adds a phone-accessible web portal under `portal/`.

Pages:
- `/` home portal
- `/map.html` offline map demo
- `/library.html` sample reference content
- `/status.html` simple device/status page

The map demo serves local image tiles from:

```text
/tiles/{z}/{x}/{y}.png
```

The included tiles are generated placeholders so the demo works immediately.
Later, replace `portal/tiles/` with real regional OpenStreetMap tiles.

### Run manually

From the project root:

```bash
sudo ./scripts/run-portal-demo.sh
```

Then from a phone connected to the pocket-cache Wi-Fi:

```text
http://10.0.0.1
```

### Install as auto-starting portal service

```bash
sudo ./scripts/install-portal-demo.sh
```

Check logs:

```bash
sudo journalctl -u pocket-cache-portal -f
```

### Real map tile path later

For real offline maps, generate or copy tiles into:

```text
portal/tiles/{z}/{x}/{y}.png
```

Recommended v0 real-map formats:
- XYZ raster tiles as `.png` or `.jpg`
- Later: MBTiles with a lightweight tile server


## v0 Games submenu update

The Play app now opens a game submenu instead of launching Sudoku directly.

Games:
- Sudoku
- 2048
- Snake placeholder
- Mines placeholder

Global controls remain:

| Button | Action |
|---|---|
| X | Back |
| Y | Select / open |
| A | Left / previous |
| B | Right / next |

2048 controls:

| Button | Action |
|---|---|
| X | Exit to Play menu |
| Y | Move up/down alternating |
| A | Move left |
| B | Move right |

2048 is intentionally lightweight: a 4×4 grid, no animation, no assets, and minimal redraw logic.


## v0 expanded offline game suite

Added low-processing-power games to the Play submenu:

- Minesweeper
- Blackjack
- Chess with a tiny random bot
- Tetris
- Game of Life
- D20 / polyhedral dice roller

These are intentionally lightweight firmware games:
- no assets
- no sound
- minimal animation
- all controlled with X/Y/A/B
- designed for the 240×320 portrait display

Notes:
- Chess is a small pseudo-legal "micro chess" demo, not a full chess engine.
- 2048 uses a four-button compromise where Y alternates up/down.
- Tetris auto-drops on redraw; Y rotates and drops.


## v0 aligned game submenu update

The Play submenu now uses the same layout as the updated home app launcher:
- no title/logo block above the list
- list starts at `y = 50`
- button size `204 × 40`
- row spacing `50`
- four items per page
- page dots at `y = 278`
- same selected-state accent rail


## v0 boot, LED, and Connect update

Changes:
- Added boot loader screen animation.
- Added rainbow RGB LED cycle during hardware adapter startup.
- Added Settings → LED ON/OFF.
- Moved About to menu slot 6.
- Tightened Connect screen copy to avoid overflow.
- Added Connect → Hello Test QR for `/hello.html`.
- Added `portal/hello.html` as a simple phone-accessible web server test page.

Connect modes:
- Hello Test: `http://10.0.0.1/hello.html`
- Portal: `http://10.0.0.1`
- Wi-Fi: QR join payload

LED behavior:
- Rainbow cycle runs at adapter startup.
- App LED colors continue after boot.
- Settings can disable app-controlled LEDs by setting `led_enabled = false`.
