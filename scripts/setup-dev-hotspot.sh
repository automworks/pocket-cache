#!/usr/bin/env bash
# setup-dev-hotspot.sh — Dev-mode hotspot for Pi Zero 2W (single WiFi radio).
#
# Creates a virtual AP interface (uap0) on top of the existing wlan0 client
# connection. The Pi stays on home WiFi for SSH while broadcasting the
# PocketCache hotspot on uap0 at the same time.
#
# Run once: sudo ./scripts/setup-dev-hotspot.sh
set -euo pipefail

CONFIG_FILE="/etc/pocket-cache/firmware.json"
AP_IFACE="uap0"
BASE_IFACE="wlan0"
HOTSPOT_IP="10.0.0.1"
DHCP_START="10.0.0.10"
DHCP_END="10.0.0.50"
DHCP_LEASE="12h"

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: run as root (sudo ./scripts/setup-dev-hotspot.sh)" >&2
  exit 1
fi

if [ ! -f "${CONFIG_FILE}" ]; then
  echo "ERROR: ${CONFIG_FILE} not found. Run install-autoboot.sh first." >&2
  exit 1
fi

SSID=$(python3 -c "import json; d=json.load(open('${CONFIG_FILE}')); print(d.get('ssid','PocketCache'))")
PASS=$(python3 -c "import json; d=json.load(open('${CONFIG_FILE}')); print(d.get('password','cache-ready'))")
# AP must share the same channel as wlan0 (same physical radio)
CHANNEL=$(iw dev "${BASE_IFACE}" info 2>/dev/null | awk '/channel/{print $2; exit}')
CHANNEL=${CHANNEL:-6}

echo "Configuring dev hotspot:"
echo "  SSID     : ${SSID}"
echo "  IP       : ${HOTSPOT_IP}"
echo "  AP iface : ${AP_IFACE} (virtual, on top of ${BASE_IFACE})"
echo "  Channel  : ${CHANNEL} (matching ${BASE_IFACE})"
echo ""

# ── install packages ──────────────────────────────────────────────────────────
apt-get update -qq
apt-get install -y hostapd dnsmasq rfkill
rfkill unblock wifi || true

# ── systemd service to create uap0 before hostapd starts ─────────────────────
# Runs at every boot: removes any stale uap0, then creates it fresh on wlan0.
cat > /etc/systemd/system/uap0-create.service <<SERVICE
[Unit]
Description=Create uap0 virtual AP interface on ${BASE_IFACE}
Before=hostapd.service dnsmasq.service
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=-/sbin/iw dev ${AP_IFACE} del
ExecStart=/sbin/iw dev ${BASE_IFACE} interface add ${AP_IFACE} type __ap
ExecStart=/sbin/ip addr add ${HOTSPOT_IP}/24 broadcast 10.0.0.255 dev ${AP_IFACE}
ExecStart=/sbin/ip link set ${AP_IFACE} up

[Install]
WantedBy=multi-user.target
SERVICE
echo "Wrote uap0-create.service"

# ── dnsmasq: DHCP + captive-portal DNS spoofing on uap0 only ─────────────────
cp /etc/dnsmasq.conf /etc/dnsmasq.conf.bak 2>/dev/null || true
cat > /etc/dnsmasq.conf <<DNSMASQ
# pocket-cache dev hotspot
interface=${AP_IFACE}
bind-interfaces
dhcp-range=${DHCP_START},${DHCP_END},${DHCP_LEASE}
# Redirect all DNS queries to the device (captive portal behaviour)
address=/#/${HOTSPOT_IP}
DNSMASQ
echo "Wrote /etc/dnsmasq.conf"

# ── hostapd: AP config on uap0, same channel as wlan0 ────────────────────────
HOSTAPD_CONF="/etc/hostapd/hostapd.conf"
cat > "${HOSTAPD_CONF}" <<HOSTAPD
interface=${AP_IFACE}
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=${CHANNEL}
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=${PASS}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
HOSTAPD
chmod 600 "${HOSTAPD_CONF}"
echo "Wrote ${HOSTAPD_CONF}"

# Point hostapd daemon at the config file
HOSTAPD_DEFAULT="/etc/default/hostapd"
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' "${HOSTAPD_DEFAULT}" 2>/dev/null || \
  echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' >> "${HOSTAPD_DEFAULT}"

# ── enable services ───────────────────────────────────────────────────────────
systemctl daemon-reload
systemctl enable uap0-create.service
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
echo "Services enabled"

echo ""
echo "Dev hotspot configured. Rebooting in 5 seconds..."
echo "After reboot:"
echo "  - SSH still works on home WiFi (wlan0 unchanged)"
echo "  - Phone can join '${SSID}' to test the captive portal"
sleep 5
reboot
