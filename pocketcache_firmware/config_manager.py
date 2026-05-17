from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path


DEFAULT_CONFIG_PATH = Path(os.environ.get("POCKETCACHE_CONFIG", "/etc/pocket-cache/firmware.json"))


@dataclass
class PocketCacheConfig:
    ssid: str = "PocketCache"
    password: str = "cache-ready"
    portal_url: str = "http://10.0.0.1"
    ip_address: str = "10.0.0.1"
    led_enabled: bool = True


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> PocketCacheConfig:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return PocketCacheConfig(
            ssid=str(data.get("ssid", "PocketCache")),
            password=str(data.get("password", "cache-ready")),
            portal_url=str(data.get("portal_url", "http://10.0.0.1")),
            ip_address=str(data.get("ip_address", "10.0.0.1")),
            led_enabled=bool(data.get("led_enabled", True)),
        )
    except FileNotFoundError:
        return PocketCacheConfig()
    except Exception:
        return PocketCacheConfig()


def save_config(config: PocketCacheConfig, path: Path = DEFAULT_CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8")


def apply_runtime_config_to_state(state, config: PocketCacheConfig) -> None:
    state.ssid = config.ssid
    state.password = config.password
    state.portal_url = config.portal_url
    state.ip_address = config.ip_address
    state.led_enabled = config.led_enabled


def write_hostapd_config(config: PocketCacheConfig, path: Path = Path("/etc/hostapd/hostapd.conf")) -> None:
    """Write a minimal hostapd config.

    This is intentionally conservative. If your real pocket-cache hostapd.conf
    has more fields, merge this function later rather than replacing it blindly.
    """
    if len(config.password) < 8:
        raise ValueError("Wi-Fi password must be at least 8 characters for WPA2.")

    text = f"""interface=wlan0
driver=nl80211
ssid={config.ssid}
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={config.password}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def restart_network_services() -> None:
    """Best-effort restart for the hotspot services."""
    commands = [
        ["sudo", "systemctl", "restart", "hostapd"],
        ["sudo", "systemctl", "restart", "dnsmasq"],
    ]
    for cmd in commands:
        subprocess.run(cmd, check=False)


def reboot_pi() -> None:
    subprocess.run(["sudo", "systemctl", "reboot"], check=False)
