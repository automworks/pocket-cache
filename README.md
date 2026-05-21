# pocket-cache

A portable offline knowledge hub. Creates a local Wi-Fi hotspot so nearby phones and laptops can access maps, reference guides, and games — no internet required.

Built around a Raspberry Pi Zero 2W and Pimoroni Display HAT Mini (2" IPS LCD, 4 buttons, RGB LED).

---

## What it does

- **Hotspot** — broadcasts a WPA2 Wi-Fi network (no internet needed)
- **Portal** — serves a web UI at `http://10.0.0.1` accessible from any connected device
- **Offline maps** — Leaflet.js with local OpenStreetMap XYZ tiles
- **Reference reader** — First Aid quick reference, Field Guide, and more
- **Games** — Sudoku, 2048, Minesweeper, Blackjack, Chess, Tetris, Game of Life, Dice
- **Device dashboard** — battery, CPU temp, memory, clients, uptime on the LCD
- **Settings** — change SSID/password, restart hotspot, reboot from the device

---

## Hardware

| Component | Part |
|---|---|
| SBC | Raspberry Pi Zero 2W |
| Display + buttons | Pimoroni Display HAT Mini (320×240 IPS, 4 buttons, RGB LED) |
| Storage | MicroSD (16GB+ recommended; 64GB+ for content packs) |
| Power | USB-C, 5V/2.5A |

**Button layout (portrait orientation):**
```
┌─────────────┐
│  X       Y  │  ← Back / Exit     Select / Confirm
│             │
│  A       B  │  ← Left / Prev     Right / Next
└─────────────┘
```

Context labels for each button are shown in the header and footer bars on screen.

**LED indicator:**

| Color | Meaning |
|---|---|
| Cyan | Normal operation |
| Green | Client connected |
| Amber | Warning |
| Red | Alert / service down |

---

## Project layout

```
pocket-cache/
├── pocketcache_firmware/       # Device firmware (Python/Pygame)
│   ├── adapters/
│   │   ├── pygame_adapter.py           # Desktop simulator
│   │   └── displayhatmini_adapter.py   # Real hardware
│   ├── screens/                        # 18 screen implementations
│   ├── data/                           # Plain-text reader documents
│   ├── main.py                         # Simulator entry point
│   ├── displayhat_main.py              # Hardware entry point
│   ├── router.py                       # Screen navigation
│   ├── state.py                        # Device state + telemetry
│   ├── config_manager.py               # Config I/O, hostapd, reboot
│   ├── theme.py                        # Colors, layout constants
│   ├── ui.py                           # Shared drawing helpers
│   ├── qr.py                           # QR code generation
│   └── Pixel12x10Mono.ttf              # Bundled monospace font
├── portal/                     # Web portal (served at 10.0.0.1)
│   ├── server.py                       # HTTP server + /api/status
│   ├── index.html                      # Home page
│   ├── map.html                        # Offline Leaflet map
│   ├── library.html                    # Reference content
│   ├── status.html                     # Live device status
│   ├── hello.html                      # Web server test page
│   ├── static/                         # CSS, JS, Leaflet vendor
│   └── tiles/                          # OSM map tiles (XYZ PNG)
├── scripts/
│   ├── setup-hotspot.sh                # One-command Pi hotspot setup
│   ├── install-autoboot.sh             # Install firmware systemd service
│   ├── install-portal-demo.sh          # Install portal systemd service
│   └── uninstall-autoboot.sh           # Remove firmware service
├── systemd/
│   ├── pocket-cache-firmware.service
│   └── pocket-cache-portal.service
└── requirements.txt
```

---

## Development setup (simulator)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pocketcache_firmware.main
```

**VS Code:** use the included `launch.json` — press F5 to launch.

### Simulator controls

| Key | Button | Action |
|---|---|---|
| `X` / `Backspace` / `Q` | X | Back / exit |
| `Space` / `Return` | Y | Select |
| `Left` / `A` | A | Left / previous |
| `Right` / `D` | B | Right / next |
| `-` | — | Drain battery (test alert) |
| `C` | — | Cycle client count |
| `E` | — | Toggle Kiwix error |
| `R` | — | Simulate reboot |

### Simulator window size

```bash
POCKETCACHE_SCALE=2 python -m pocketcache_firmware.main   # default
POCKETCACHE_SCALE=3 python -m pocketcache_firmware.main   # larger
```

---

## Deploy on a Raspberry Pi

### 1. Set up the hotspot

Run once after flashing a fresh Pi OS image:

```bash
sudo ./scripts/setup-hotspot.sh
```

This installs and configures `hostapd`, `dnsmasq`, static IP (`10.0.0.1`), `openssh-server`, and iptables rules, then reboots.

### 2. Install the firmware

```bash
sudo ./scripts/install-autoboot.sh
```

Copies the firmware to `/opt/pocket-cache-firmware`, creates a venv, installs dependencies, and enables the `pocket-cache-firmware` systemd service.

### 3. Install the portal

```bash
sudo ./scripts/install-portal-demo.sh
```

Enables the `pocket-cache-portal` systemd service (runs `portal/server.py` on port 80).

### Check logs

```bash
sudo journalctl -u pocket-cache-firmware -f
sudo journalctl -u pocket-cache-portal -f
```

### Uninstall

```bash
sudo ./scripts/uninstall-autoboot.sh
```

---

## Run firmware on hardware (manual)

```bash
pip install displayhatmini
python -m pocketcache_firmware.displayhat_main
```

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `POCKETCACHE_ROTATION` | `180` | Display rotation: `180`, `cw`, `ccw` |
| `POCKETCACHE_CONFIG` | `/etc/pocket-cache/firmware.json` | Config file path |
| `SDL_VIDEODRIVER` | `dummy` | Set by systemd service (headless) |

If the display is upside-down:

```bash
POCKETCACHE_ROTATION=cw python -m pocketcache_firmware.displayhat_main
```

---

## Portal

Served at `http://10.0.0.1` when connected to the PocketCache Wi-Fi network.

| Page | URL | Description |
|---|---|---|
| Home | `/` | Card grid navigation |
| Map | `/map.html` | Offline Leaflet map |
| Library | `/library.html` | Reference content |
| Status | `/status.html` | Live device info |
| Test | `/hello.html` | Web server connectivity test |
| API | `/api/status` | JSON: uptime, temp, disk, clients |

### Map tiles

Tiles are served from `portal/tiles/{z}/{x}/{y}.png` (standard XYZ format). Zoom levels 0–2 (21 world tiles) are included in the repo. For regional detail, add higher-zoom tiles:

```bash
# Example: download tiles for a region using a tool like tilesdownloader or osmium
# Place at portal/tiles/{z}/{x}/{y}.png
```

Recommended formats: XYZ PNG tiles. For large content packs, consider MBTiles + a lightweight tile server.

---

## Settings (on-device)

Navigate to **Settings** from the main menu.

| Row | Action |
|---|---|
| SSID | Edit the hotspot network name |
| PASS | Edit the WPA2 password (8+ chars) |
| LED | Toggle RGB LED on/off |
| SAVE WIFI | Write config + restart hotspot |
| RESTART PI | Reboot the device |

Config is stored at `/etc/pocket-cache/firmware.json`.

---

## Reader documents

Documents live in `pocketcache_firmware/data/` as plain `.txt` files. Currently included:

| File | Contents |
|---|---|
| `field_guide.txt` | Device guide: connecting, controls, features, troubleshooting |
| `first_aid.txt` | CPR, choking, bleeding, burns, shock, seizure, poisoning, heat/cold |

To add a document, drop a `.txt` file in `data/` and add an entry to the `_DOCS` list in `screens/reader.py`.

---

## Screens

| Screen | Description |
|---|---|
| Boot | Animated startup with progress bar and service checklist |
| Menu | Paged app launcher (4 items/page) |
| Library | Content module status (medical, maps, wikipedia, books, games) |
| Connect | QR codes: Hello test, Portal URL, Wi-Fi join |
| Status | Battery, CPU load, memory, Wi-Fi, temp, clients, uptime |
| Settings | SSID/password editor, LED toggle, hotspot save, reboot |
| Reader | Paged e-reader with two documents and font size toggle |
| About | Device branding and tagline |
| Alert | Low battery / service failure overlay |
| Games → | Paged games menu |
| Sudoku | 9×9 puzzle with mistake counter |
| 2048 | Tile merge game (4-button adaptation) |
| Minesweeper | 6×6 grid |
| Blackjack | Dealer simulation |
| Chess | Micro chess with random bot |
| Tetris | Piece rotation and line clear |
| Game of Life | Conway's cellular automaton |
| Dice | Polyhedral dice roller (D4–D100) |

---

## Roadmap

### v0.1
- [ ] Dev Mode — toggle hotspot off, join home WiFi for SSH access and `git pull`
- [ ] More reader content (survival, repair, navigation reference)
- [ ] Higher-zoom regional map tiles + tile download script

### v0.2
- [ ] Kiwix integration — serve offline Wikipedia / reference ZIM files
- [ ] Portal content indexing and search
- [ ] Battery monitoring (hardware UPS module)

### Future
- [ ] Content sync over USB
- [ ] Multi-language support
- [ ] Accessibility: high-contrast mode
- [ ] Tests and CI

---

## License

MIT. Map tiles sourced from OpenStreetMap contributors (ODbL).
Font: Pixel12x10Mono (OFL) by Corne2Plum3.
