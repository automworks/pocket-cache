#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/pocket-cache-firmware"
SERVICE="/etc/systemd/system/pocket-cache-firmware.service"
USER_NAME="${SUDO_USER:-pi}"

echo "Installing pocket-cache firmware to ${APP_DIR}"

sudo mkdir -p "${APP_DIR}"
sudo rsync -a --delete ./ "${APP_DIR}/"
sudo chown -R "${USER_NAME}:${USER_NAME}" "${APP_DIR}"

cd "${APP_DIR}"

if [ ! -d ".venv" ]; then
  sudo -u "${USER_NAME}" python3 -m venv .venv
fi

sudo -u "${USER_NAME}" .venv/bin/pip install --upgrade pip
sudo -u "${USER_NAME}" .venv/bin/pip install -r requirements.txt
sudo -u "${USER_NAME}" .venv/bin/pip install displayhatmini

sudo mkdir -p /etc/pocket-cache
if [ ! -f /etc/pocket-cache/firmware.json ]; then
  sudo tee /etc/pocket-cache/firmware.json >/dev/null <<'JSON'
{
  "ssid": "PocketCache",
  "password": "cache-ready",
  "portal_url": "http://10.0.0.1",
  "ip_address": "10.0.0.1",
  "led_enabled": true
}
JSON
fi

sudo cp systemd/pocket-cache-firmware.service "${SERVICE}"
sudo sed -i "s/User=pi/User=${USER_NAME}/" "${SERVICE}"

sudo systemctl daemon-reload
sudo systemctl enable pocket-cache-firmware.service
sudo systemctl restart pocket-cache-firmware.service

echo "Installed and started pocket-cache firmware."
echo "Logs: sudo journalctl -u pocket-cache-firmware -f"
