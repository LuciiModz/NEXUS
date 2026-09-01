# NEXUS — Linux Cybersec Toolkit

```
 ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
 ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
 ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
 ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
 ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
 ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

Terminal-native cybersecurity toolkit for Linux. 62 tools across 10 categories — fill fields, generate commands, run them directly, no browser needed.

---

## Install

```bash
git clone https://github.com/LuciiModz/NEXUS.git
cd NEXUS
chmod +x install.sh && sudo ./install.sh
```

Or manually:

```bash
pip install -r requirements.txt --break-system-packages --ignore-installed packaging
python3 nexus.py
```

> **Note:** If you hit a `packaging 25.0` error during install, run:
> ```bash
> pip3 install packaging --break-system-packages --ignore-installed packaging
> ```
> Then re-run `install.sh` or go straight to `python3 nexus.py` — it won't affect functionality.

---

## Categories

| # | Category      | Tools | Coverage |
|---|--------------|-------|----------|
| 1 | RECON        | 9     | nmap, gobuster, amass, ffuf, shodan, theHarvester, sublist3r |
| 2 | WEB ATTACK   | 7     | sqlmap, xsstrike, nikto, wpscan, commix, SSRF probe |
| 3 | PRIVESC      | 8     | linpeas, SUID, pspy, cron, docker escape, capabilities |
| 4 | NETWORK      | 7     | tcpdump, ARP MITM, chisel, proxychains, WiFi WPA crack |
| 5 | EXPLOIT      | 6     | MSF handler, revshell gen (7 types), msfvenom, pwncat |
| 6 | CREDS / HASH | 6     | hashcat, john, hydra, hashid, pass-the-hash, secretsdump |
| 7 | ACTIVE DIR   | 5     | bloodhound, kerberoast, AS-REP, LDAP dump, evil-winrm |
| 8 | PERSISTENCE  | 4     | cron, systemd, .bashrc hook, SSH key drop |
| 9 | LOG CLEAR    | 5     | log wipe, history nuke, utmp, shred, timestamp stomp |
| 10| FORENSICS    | 5     | volatility3, binwalk, strings, timeline, exiftool |

---

## Usage

```
python3 nexus.py

  1-10  select category
  c     cheat sheet (14 quick-reference one-liners)
  q     quit

Inside a category:
  #     select tool
  b     back

Inside a tool:
  fill fields → GENERATE → r (run) / g (regenerate) / b (back)
```

---

## Requirements

- Python 3.8+
- `rich` (pip)
- See `requirements.txt` for full dependency list and `install.sh` for automated setup

---

## Platform

Tested on Kali Linux, Parrot OS, Ubuntu 22.04+. Most tools are pre-installed on Kali — `install.sh` handles the rest.
