#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-80}"
cd "$(dirname "$0")/../portal"

echo "Serving pocket-cache portal at http://0.0.0.0:${PORT}"
echo "From a phone on the pocket-cache Wi-Fi, open http://10.0.0.1"
sudo python3 -m http.server "${PORT}" --bind 0.0.0.0
