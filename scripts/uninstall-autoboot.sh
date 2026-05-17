#!/usr/bin/env bash
set -euo pipefail

sudo systemctl disable --now pocket-cache-firmware.service || true
sudo rm -f /etc/systemd/system/pocket-cache-firmware.service
sudo systemctl daemon-reload

echo "Disabled pocket-cache firmware autoboot service."
