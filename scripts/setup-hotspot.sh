#!/usr/bin/env bash
# setup-hotspot.sh — Configure a Raspberry Pi as a pocket-cache Wi-Fi hotspot.
# Installs hostapd, dnsmasq, and iptables, then writes config files derived
# from /etc/pocket-cache/firmware.json (SSID, password, IP).
# Run once after install-autoboot.sh: sudo ./scripts/setup-hotspot.sh
set -euo pipefail

CONFIG_FILE="/etc/pocket-cache/firmware.json"
IFACE="wlan0"
HOTSPOT_IP="10.0.0.1"
DHCP_RANGE_START="10.0.0.10"
DHCP_RANGE_END="10.0.0.50"
DHCP_LEASE="12h"

# ── read firmware config ──────────────────────────────────────────────────────
if [ ! -f "${CONFIG_FILE}" ]; then
  echo "ERROR: ${CONFIG_FILE} not found. Run install-autoboot.sh first." >&2
  exit 1
fi

SSID=$(python3 -c "import json; d=json.load(open('${CONFIG_FILE}')); print(d.get('ssid','PocketCache'))")
PASS=$(python3 -c "import json; d=json.load(open('${CONFIG_FILE}')); print(d.get('password','cache-ready'))")
IP=$(python3 -c "import json; d=json.load(open('${CONFIG_FILE}')); print(d.get('ip_address','10.0.0.1'))")

echo "Configuring hotspot:"
echo "  SSID     : ${SSID}"
echo "  IP       : ${IP}"
echo "  Interface: ${IFACE}"
echo ""

# ── install packages ──────────────────────────────────────────────────────────
apt-get update -qq
apt-get install -y hostapd dnsmasq iptables-persistent rfkill

# Unblock WiFi radio (often soft-blocked on fresh Pi OS images)
rfkill unblock wifi || true

# ── static IP for wlan0 via dhcpcd ───────────────────────────────────────────
DHCPCD_CONF="/etc/dhcpcd.conf"
if ! grep -q "interface ${IFACE}" "${DHCPCD_CONF}" 2>/dev/null; then
  cat >> "${DHCPCD_CONF}" <<DHCPCD

# pocket-cache hotspot static IP
interface ${IFACE}
    static ip_address=${IP}/24
    nohook wpa_supplicant
DHCPCD
  echo "Added static IP to ${DHCPCD_CONF}"
else
  echo "dhcpcd.conf already has ${IFACE} config — skipping"
fi

# ── dnsmasq: DHCP + captive-portal DNS spoofing ───────────────────────────────
DNSMASQ_CONF="/etc/dnsmasq.conf"
cp "${DNSMASQ_CONF}" "${DNSMASQ_CONF}.bak" 2>/dev/null || true
cat > "${DNSMASQ_CONF}" <<DNSMASQ
# pocket-cache dnsmasq config
interface=${IFACE}
bind-interfaces
dhcp-range=${DHCP_RANGE_START},${DHCP_RANGE_END},${DHCP_LEASE}
# Redirect all DNS queries to the device (captive portal behaviour)
address=/#/${IP}
DNSMASQ
echo "Wrote ${DNSMASQ_CONF}"

# ── hostapd: access point config ─────────────────────────────────────────────
HOSTAPD_CONF="/etc/hostapd/hostapd.conf"
cat > "${HOSTAPD_CONF}" <<HOSTAPD
interface=${IFACE}
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=6
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

# Point hostapd daemon to the config file
HOSTAPD_DEFAULT="/etc/default/hostapd"
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' "${HOSTAPD_DEFAULT}" 2>/dev/null || \
  echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' >> "${HOSTAPD_DEFAULT}"

# ── iptables: NAT masquerade (optional upstream internet sharing) ─────────────
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || true
iptables -A FORWARD -i eth0 -o "${IFACE}" -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true
iptables -A FORWARD -i "${IFACE}" -o eth0 -j ACCEPT 2>/dev/null || true
# Persist iptables rules
netfilter-persistent save 2>/dev/null || true
echo "IP forwarding / NAT rules set"

# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

# ── enable and start services ─────────────────────────────────────────────────
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq

echo ""
echo "Hotspot configured. Rebooting in 5 seconds to apply changes..."
echo "After reboot, connect to Wi-Fi '${SSID}' and open http://${IP}"
sleep 5
reboot
