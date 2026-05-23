from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from .theme import APP_COLORS


@dataclass
class DeviceState:
    ssid: str = "PocketCache"
    password: str = "cache-ready"
    portal_url: str = "http://10.0.0.1"
    ip_address: str = "10.0.0.1"

    battery_pct: int = 87
    clients: int = 0
    storage_used_gb: float = 92.0
    storage_total_gb: float = 128.0

    services: dict[str, bool] = field(default_factory=lambda: {
        "hotspot": True,
        "dns": True,
        "portal": True,
        "kiwix": True,
    })

    content: dict[str, bool] = field(default_factory=lambda: {
        "medical": True,
        "repair": True,
        "maps": True,
        "wikipedia": True,
        "books": True,
        "games": True,
    })

    selected: bool = False
    booting: bool = True
    boot_started_at: float = field(default_factory=monotonic)
    started_at: float = field(default_factory=monotonic)
    alert_acknowledged: bool = False
    active_app: str = "menu"
    led_enabled: bool = True
    cpu_temp_c: float = 42.0
    cpu_load_pct: int = 18
    memory_pct: int = 31
    wifi_signal_pct: int = 86
    packets_served: int = 1248

    def tick(self) -> None:
        """Advance simulated runtime state."""
        if self.booting and monotonic() - self.boot_started_at > 3.5:
            self.booting = False

        t = self.uptime_seconds
        self.cpu_temp_c = 41.5 + ((t % 17) * 0.35)
        self.cpu_load_pct = 14 + ((t * 7) % 46)
        self.memory_pct = 29 + ((t * 3) % 22)
        self.wifi_signal_pct = 72 + ((t * 5) % 22)
        self.packets_served += max(0, self.clients)

    @property
    def uptime_seconds(self) -> int:
        return int(monotonic() - self.started_at)

    @property
    def storage_pct(self) -> int:
        return int((self.storage_used_gb / self.storage_total_gb) * 100)

    @property
    def all_services_ok(self) -> bool:
        return all(self.services.values())

    @property
    def all_content_ok(self) -> bool:
        return all(self.content.values())

    @property
    def has_alert(self) -> bool:
        return self.battery_pct <= 15 or not self.all_services_ok or not self.all_content_ok

    @property
    def led_color(self) -> tuple[int, int, int]:
        if not self.led_enabled:
            return (0, 0, 0)
        if self.battery_pct <= 15 or not self.all_services_ok:
            return (255, 0, 0)
        if not self.all_content_ok or self.battery_pct <= 30:
            return (255, 160, 0)

        app_leds = {
            "menu": (80, 80, 255),
            "about": (180, 110, 255),
            "library": (0, 255, 120),
            "games": (255, 80, 180),
            "sudoku": (255, 80, 180),
            "game_2048": (255, 120, 40),
            "game_mines": (200, 255, 80),
            "blackjack": (0, 180, 80),
            "chess": (220, 220, 255),
            "tetris": (255, 80, 80),
            "life": (80, 255, 120),
            "dice": (255, 255, 80),
            "reader": (255, 210, 80),
            "portal": (0, 180, 255),
            "status": (80, 255, 255),
            "settings": (255, 120, 40),
        }
        return app_leds.get(self.active_app, (0, 255, 80))

    @property
    def app_accent_color(self) -> tuple[int, int, int]:
        """Return the UI accent color for the current app (Figma design system)."""
        return APP_COLORS.get(self.active_app, (255, 115, 0))

    def reboot(self) -> None:
        self.booting = True
        self.boot_started_at = monotonic()
        self.started_at = monotonic()
        self.alert_acknowledged = False

    def drain_battery(self, amount: int = 8) -> None:
        self.battery_pct = max(0, self.battery_pct - amount)

    def cycle_clients(self) -> None:
        self.clients = (self.clients + 1) % 6

    def toggle_kiwix_error(self) -> None:
        self.services["kiwix"] = not self.services["kiwix"]

    def toggle_selected(self) -> None:
        self.selected = not self.selected


def format_uptime(seconds: int) -> str:
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
