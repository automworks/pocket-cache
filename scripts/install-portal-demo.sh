#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/pocket-cache-firmware"
SERVICE="/etc/systemd/system/pocket-cache-portal.service"
USER_NAME="${SUDO_USER:-pi}"

sudo mkdir -p "${APP_DIR}"
sudo rsync -a --delete ./ "${APP_DIR}/"
sudo chown -R "${USER_NAME}:${USER_NAME}" "${APP_DIR}"

sudo cp systemd/pocket-cache-portal.service "${SERVICE}"
sudo sed -i "s/User=pi/User=${USER_NAME}/" "${SERVICE}"

sudo systemctl daemon-reload
sudo systemctl enable pocket-cache-portal.service
sudo systemctl restart pocket-cache-portal.service

echo "Portal demo installed."
echo "Open from phone: http://10.0.0.1"
echo "Logs: sudo journalctl -u pocket-cache-portal -f"
