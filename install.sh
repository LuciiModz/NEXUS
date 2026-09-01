#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# NEXUS — Auto Installer
# Usage: chmod +x install.sh && ./install.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[+]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
err()  { echo -e "${RED}[-]${NC} $*"; }

echo -e "\n${GREEN}"
echo " ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗"
echo " ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝"
echo " ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗"
echo " ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║"
echo " ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║"
echo " ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
echo -e "${NC} Linux Cybersec Toolkit — Installer\n"

# ── Root check ──────────────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
  warn "Not running as root — some installs may need sudo."
fi

# ── APT packages ─────────────────────────────────────────────────────────────
ok "Updating apt..."
apt-get update -qq

APT_PKGS=(
  nmap gobuster ffuf enum4linux whatweb nikto sqlmap hydra john hashcat
  tcpdump netcat-openbsd dsniff proxychains4 aircrack-ng binwalk
  libimage-exiftool-perl curl python3-pip ruby perl sleuthkit
  wordlists seclists
)

ok "Installing apt packages..."
apt-get install -y "${APT_PKGS[@]}" 2>/dev/null || warn "Some apt packages may have failed — continuing."

# ── Rockyou wordlist ─────────────────────────────────────────────────────────
if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
  ok "Decompressing rockyou.txt..."
  gzip -dk /usr/share/wordlists/rockyou.txt.gz 2>/dev/null || true
fi

# ── Python packages ───────────────────────────────────────────────────────────
ok "Installing Python dependencies..."
pip3 install rich impacket bloodhound ldap3 ldapdomaindump shodan pwncat-cs --break-system-packages 2>/dev/null \
  || pip3 install rich impacket bloodhound ldap3 ldapdomaindump shodan pwncat-cs

# ── Ruby gems ─────────────────────────────────────────────────────────────────
ok "Installing Ruby gems (evil-winrm, wpscan)..."
gem install evil-winrm wpscan 2>/dev/null || warn "gem install failed — install ruby first."

# ── theHarvester ─────────────────────────────────────────────────────────────
if ! command -v theHarvester &>/dev/null; then
  ok "Installing theHarvester..."
  git clone -q https://github.com/laramies/theHarvester.git /opt/theHarvester 2>/dev/null || true
  pip3 install -r /opt/theHarvester/requirements/base.txt --break-system-packages 2>/dev/null || true
  ln -sf /opt/theHarvester/theHarvester.py /usr/local/bin/theHarvester
fi

# ── Sublist3r ─────────────────────────────────────────────────────────────────
if ! command -v sublist3r &>/dev/null; then
  ok "Installing Sublist3r..."
  git clone -q https://github.com/aboul3la/Sublist3r.git /opt/Sublist3r 2>/dev/null || true
  pip3 install -r /opt/Sublist3r/requirements.txt --break-system-packages 2>/dev/null || true
  ln -sf /opt/Sublist3r/sublist3r.py /usr/local/bin/sublist3r
fi

# ── Amass ─────────────────────────────────────────────────────────────────────
if ! command -v amass &>/dev/null; then
  ok "Installing Amass via snap..."
  snap install amass 2>/dev/null || warn "snap not available — install amass manually."
fi

# ── XSStrike ──────────────────────────────────────────────────────────────────
if [ ! -d /opt/XSStrike ]; then
  ok "Installing XSStrike..."
  git clone -q https://github.com/s0md3v/XSStrike.git /opt/XSStrike 2>/dev/null || true
  pip3 install -r /opt/XSStrike/requirements.txt --break-system-packages 2>/dev/null || true
  ln -sf /opt/XSStrike/xsstrike.py /usr/local/bin/xsstrike
fi

# ── Commix ────────────────────────────────────────────────────────────────────
if ! command -v commix &>/dev/null; then
  ok "Installing Commix..."
  git clone -q https://github.com/commixproject/commix.git /opt/commix 2>/dev/null || true
  ln -sf /opt/commix/commix.py /usr/local/bin/commix
fi

# ── Chisel ────────────────────────────────────────────────────────────────────
if ! command -v chisel &>/dev/null; then
  ok "Installing Chisel..."
  CHISEL_URL="https://github.com/jpillora/chisel/releases/latest/download/chisel_linux_amd64.gz"
  wget -q "$CHISEL_URL" -O /tmp/chisel.gz && \
    gunzip /tmp/chisel.gz && \
    mv /tmp/chisel /usr/local/bin/chisel && \
    chmod +x /usr/local/bin/chisel || warn "Chisel install failed."
fi

# ── pspy ──────────────────────────────────────────────────────────────────────
if ! command -v pspy64 &>/dev/null; then
  ok "Installing pspy64..."
  wget -q "https://github.com/DominicBreuker/pspy/releases/latest/download/pspy64" \
    -O /usr/local/bin/pspy64 && chmod +x /usr/local/bin/pspy64 || warn "pspy install failed."
fi

# ── Volatility 3 ─────────────────────────────────────────────────────────────
if [ ! -d /opt/volatility3 ]; then
  ok "Installing Volatility 3..."
  git clone -q https://github.com/volatilityfoundation/volatility3.git /opt/volatility3 2>/dev/null || true
  pip3 install -r /opt/volatility3/requirements.txt --break-system-packages 2>/dev/null || true
  ln -sf /opt/volatility3/vol.py /usr/local/bin/vol.py
fi

# ── hashid ────────────────────────────────────────────────────────────────────
if ! command -v hashid &>/dev/null; then
  ok "Installing hashid..."
  pip3 install hashid --break-system-packages 2>/dev/null || true
fi

# ── BloodHound Python ────────────────────────────────────────────────────────
if ! command -v bloodhound-python &>/dev/null; then
  ok "Installing bloodhound-python..."
  pip3 install bloodhound --break-system-packages 2>/dev/null || true
fi

# ── LinPEAS (cache locally) ───────────────────────────────────────────────────
if [ ! -f /opt/linpeas.sh ]; then
  ok "Downloading LinPEAS..."
  curl -sL https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh \
    -o /opt/linpeas.sh && chmod +x /opt/linpeas.sh || warn "LinPEAS download failed."
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
ok "Install complete. Run the toolkit:"
echo -e "  ${GREEN}python3 nexus.py${NC}\n"
